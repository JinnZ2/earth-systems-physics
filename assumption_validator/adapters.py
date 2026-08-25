# assumption_validator/adapters.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Ingestion adapters: turn raw sensor data into layer_state dicts
# that the assumption validator can consume.
#
# Supported sources:
#   - DictAdapter   : manual readings or JSON
#   - CSVAdapter    : time-series logs (timestamp, sensor, value)
#   - CANBusAdapter : J1939/OBD-II (stubbed for your rig)
#   - CompositeAdapter: merge multiple sources, resolve conflicts
#
# All adapters fill missing values from a fallback layer state
# (default: BASELINE from cascade_engine).

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List, Callable, Any, Union
from pathlib import Path

import numpy as np

from cascade_engine import BASELINE
from assumption_validator.registry import REGISTRY


# ─────────────────────────────────────────────
# SENSOR MAP
# Maps physical sensor names to layer_key + source_layer.
# This is the translation layer between your rig and the physics engine.
# ─────────────────────────────────────────────

SENSOR_MAP: Dict[str, Dict] = {
    # ── RIG / VEHICLE SENSORS ──────────────────────────────────────────
    "coolant_temp_c": {
        "layer_key": "SST_anomaly_K",
        "source_layer": 4,
        "transform": lambda x: (x - 85) / 10,  # rough K anomaly from nominal
    },
    "oil_pressure_kPa": {
        "layer_key": "fault_coulomb_change_Pa",
        "source_layer": 5,
        "transform": lambda x: (x - 350) * 1000,  # kPa → Pa offset
    },
    "engine_rpm": {
        "layer_key": "coriolis_f_rads",
        "source_layer": 3,
        "transform": lambda x: 1e-4 + (x / 6000) * 1e-5,  # not physical, just demo
    },
    "fuel_pressure_kPa": {
        "layer_key": "volcanic_enhancement",
        "source_layer": 5,
        "transform": lambda x: 0.8 + (x / 1000) * 0.4,
    },
    "intake_temp_c": {
        "layer_key": "arctic_amplification_K",
        "source_layer": 4,
        "transform": lambda x: (x - 20) / 10,
    },
    "battery_voltage_V": {
        "layer_key": "magnomech_piezo_voltage_V",
        "source_layer": 0,
        "transform": lambda x: x / 12.0,
    },
    # ── WEATHER / ENVIRONMENT ────────────────────────────────────────
    "ambient_temp_c": {
        "layer_key": "GHG_forcing_Wm2",
        "source_layer": 3,
        "transform": lambda x: 1.5 + (x - 15) * 0.1,
    },
    "wind_speed_ms": {
        "layer_key": "convection_active",
        "source_layer": 3,
        "transform": lambda x: 0.0 if x < 5 else 1.0,
    },
    "barometric_pressure_hPa": {
        "layer_key": "jet_shear_proxy",
        "source_layer": 3,
        "transform": lambda x: -8e-4 + (x - 1013) * 1e-6,
    },
    # ── MANUAL / OBSERVATIONAL ──────────────────────────────────────
    "observer_calibration_offset": {
        "layer_key": "magnonic_damping_total",
        "source_layer": 0,
        "transform": lambda x: max(0.0, min(1.0, x / 100)),
    },
    "stress_feeling_1to10": {
        "layer_key": "nutrient_stress_factor",
        "source_layer": 6,
        "transform": lambda x: 1.0 - (x / 10) * 0.5,
    },
}

# Reverse map: layer_key → list of sensor names that can provide it
LAYER_KEY_TO_SENSORS: Dict[str, List[str]] = {}
for sensor, info in SENSOR_MAP.items():
    lk = info["layer_key"]
    LAYER_KEY_TO_SENSORS.setdefault(lk, []).append(sensor)


# ─────────────────────────────────────────────
# BASE ADAPTER
# ─────────────────────────────────────────────

class SensorAdapter:
    """Base class — defines how raw data becomes layer_state dicts."""

    def read(self) -> Dict[int, Dict]:
        """Return layer_states dict (0-6) with current values.
        Missing layers are filled from fallback.
        """
        raise NotImplementedError

    def _merge_with_fallback(self, layer_states: Dict[int, Dict]) -> Dict[int, Dict]:
        """Fill missing layers from BASELINE."""
        merged = dict(BASELINE)  # shallow copy
        for layer, state in layer_states.items():
            merged[layer] = state
        return merged

    def _apply_sensor_map(self, raw: Dict[str, float]) -> Dict[int, Dict]:
        """Translate sensor readings into layer_state dicts using SENSOR_MAP."""
        layer_states: Dict[int, Dict] = {}

        for sensor_name, value in raw.items():
            if sensor_name not in SENSOR_MAP:
                continue  # ignore unknown sensors

            info = SENSOR_MAP[sensor_name]
            layer = info["source_layer"]
            key = info["layer_key"]
            transform = info.get("transform", lambda x: x)

            try:
                val = transform(value)
            except Exception:
                continue  # transform failed

            if layer not in layer_states:
                layer_states[layer] = {}
            layer_states[layer][key] = val

        return layer_states


# ─────────────────────────────────────────────
# DICT ADAPTER — manual readings or JSON
# ─────────────────────────────────────────────

class DictAdapter(SensorAdapter):
    """Accepts a dict of sensor readings (name → value)."""

    def __init__(self, readings: Dict[str, float], fallback: Optional[Dict] = None):
        self.readings = readings
        self.fallback = fallback or BASELINE

    def read(self) -> Dict[int, Dict]:
        raw = self._apply_sensor_map(self.readings)
        merged = dict(self.fallback)  # base from fallback
        for layer, state in raw.items():
            if layer not in merged:
                merged[layer] = {}
            merged[layer].update(state)
        return merged


# ─────────────────────────────────────────────
# CSV ADAPTER — time-series log
# ─────────────────────────────────────────────

class CSVAdapter(SensorAdapter):
    """
    Reads timestamped sensor logs from CSV.

    Expected columns:
        timestamp, sensor_name, value
    or:
        timestamp, coolant_temp_c, oil_pressure_kPa, ...

    The adapter reads all rows and returns the most recent complete row.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        timestamp_col: str = "timestamp",
        value_col: str = "value",
        sensor_col: str = "sensor_name",
        long_format: bool = True,
        fallback: Optional[Dict] = None,
    ):
        """
        long_format=True:
            timestamp, sensor_name, value
        long_format=False:
            timestamp, sensor1, sensor2, sensor3, ...
        """
        self.file_path = Path(file_path)
        self.ts_col = timestamp_col
        self.value_col = value_col
        self.sensor_col = sensor_col
        self.long_format = long_format
        self.fallback = fallback or BASELINE

    def read(self) -> Dict[int, Dict]:
        if not self.file_path.exists():
            return self.fallback

        with open(self.file_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return self.fallback

        if self.long_format:
            # Long format: each row is one sensor reading at a timestamp
            # We need to group by timestamp and take the latest complete set
            latest_ts = None
            latest_readings = {}
            for row in rows:
                ts = row.get(self.ts_col, "")
                if not ts:
                    continue
                if latest_ts is None or ts > latest_ts:
                    latest_ts = ts
                    # reset readings for this timestamp
                    latest_readings = {}
                if ts == latest_ts:
                    sensor = row.get(self.sensor_col, "")
                    val_str = row.get(self.value_col, "")
                    if sensor and val_str:
                        try:
                            latest_readings[sensor] = float(val_str)
                        except ValueError:
                            pass
        else:
            # Wide format: each row is a full snapshot
            latest_row = rows[-1]  # assume sorted by time
            latest_readings = {}
            for col, val_str in latest_row.items():
                if col == self.ts_col:
                    continue
                try:
                    latest_readings[col] = float(val_str)
                except ValueError:
                    pass

        # Translate through sensor map
        raw = self._apply_sensor_map(latest_readings)
        merged = dict(self.fallback)
        for layer, state in raw.items():
            if layer not in merged:
                merged[layer] = {}
            merged[layer].update(state)

        return merged


# ─────────────────────────────────────────────
# CAN BUS ADAPTER — for rig
# ─────────────────────────────────────────────

class CANBusAdapter(SensorAdapter):
    """
    Reads from a CAN bus interface (J1939 for heavy trucks).

    Stubbed: replace with actual CAN library (python-can, etc.)
    """

    # J1939 SPN → SENSOR_MAP key mapping
    SPN_MAP = {
        110: "coolant_temp_c",       # Engine Coolant Temperature
        100: "oil_pressure_kPa",     # Engine Oil Pressure
        190: "engine_rpm",          # Engine Speed
        94: "fuel_pressure_kPa",    # Fuel Pressure
        105: "intake_temp_c",       # Intake Manifold Temperature
        168: "battery_voltage_V",   # Battery Potential / Power Input
    }

    def __init__(
        self,
        interface: str = "can0",
        bustype: str = "socketcan",
        fallback: Optional[Dict] = None,
    ):
        self.interface = interface
        self.bustype = bustype
        self.fallback = fallback or BASELINE
        self._bus = None

    def _connect(self):
        try:
            import can
            self._bus = can.Bus(interface=self.interface, bustype=self.bustype)
        except ImportError:
            raise RuntimeError("python-can not installed. Install with: pip install python-can")
        except Exception:
            self._bus = None

    def read(self) -> Dict[int, Dict]:
        if self._bus is None:
            self._connect()

        if self._bus is None:
            return self.fallback

        # Read a single non-blocking frame
        try:
            msg = self._bus.recv(timeout=0.5)
            if msg is None:
                return self.fallback
        except Exception:
            return self.fallback

        # Parse PGN and SPN from CAN ID (simplified)
        # J1939: message ID includes PGN (3 bytes), source address
        pgn = (msg.arbitration_id >> 8) & 0xFFFF
        spn_lookup = {
            0xF004: 110,  # EEC1 - Engine Coolant Temp
            0xF003: 100,  # EEC2 - Oil Pressure
            0xF000: 190,  # EEC3 - Engine Speed
            0xF00C: 94,   # Fuel Pressure
            0xF005: 105,  # Intake Temp
            0xF011: 168,  # Battery Voltage
        }
        spn = spn_lookup.get(pgn)
        if spn is None:
            return self.fallback

        sensor_name = self.SPN_MAP.get(spn)
        if sensor_name is None:
            return self.fallback

        # Decode value from payload (simplified — real J1939 is byte-scaled)
        # This is a placeholder; real decoding depends on SPN scaling
        raw_value = msg.data[0] if msg.data else 0
        # Scale based on known SPN ranges
        scaling = {
            110: (0.5,  -40),   # °C = value*0.5 - 40
            100: (4,    0),     # kPa = value*4
            190: (0.125, 0),    # rpm = value*0.125
            94:  (0.5,  0),     # kPa = value*0.5
            105: (0.5,  -40),   # °C = value*0.5 - 40
            168: (0.05, 0),     # V = value*0.05
        }
        scale, offset = scaling.get(spn, (1.0, 0.0))
        value = raw_value * scale + offset

        # Translate through sensor map
        raw_readings = {sensor_name: value}
        layer_states = self._apply_sensor_map(raw_readings)

        # Merge with fallback
        merged = dict(self.fallback)
        for layer, state in layer_states.items():
            if layer not in merged:
                merged[layer] = {}
            merged[layer].update(state)

        return merged


# ─────────────────────────────────────────────
# COMPOSITE ADAPTER — merge multiple sources
# ─────────────────────────────────────────────

class CompositeAdapter(SensorAdapter):
    """
    Merges multiple adapters in priority order.
    First adapter that returns a value for a given layer_key wins.
    """

    def __init__(self, adapters: List[SensorAdapter], fallback: Optional[Dict] = None):
        self.adapters = adapters
        self.fallback = fallback or BASELINE

    def read(self) -> Dict[int, Dict]:
        merged = dict(self.fallback)
        # Collect all layer states from all adapters
        all_states = []
        for adapter in self.adapters:
            try:
                states = adapter.read()
                all_states.append(states)
            except Exception:
                continue

        # Priority order: earlier adapters override later
        for states in all_states:
            for layer, state in states.items():
                if layer not in merged:
                    merged[layer] = {}
                # Only override if the key is not already set
                for key, val in state.items():
                    if key not in merged[layer]:
                        merged[layer][key] = val

        return merged


# ─────────────────────────────────────────────
# CLOCK ADAPTER — cycles BASELINE + small drift
# ─────────────────────────────────────────────

class ClockAdapter(SensorAdapter):
    """
    For testing: spins through BASELINE with a slow sinusoidal drift.
    Simulates a warming climate to exercise the monitor.
    """

    def __init__(self, period_hours: float = 24.0, amplitude: float = 0.1, fallback: Optional[Dict] = None):
        self.period_hours = period_hours
        self.amplitude = amplitude
        self.fallback = fallback or BASELINE
        self._start = datetime.utcnow()

    def read(self) -> Dict[int, Dict]:
        elapsed = (datetime.utcnow() - self._start).total_seconds() / 3600
        phase = (elapsed / self.period_hours) * 2 * np.pi

        # Apply drift to key assumption variables
        drift = self.amplitude * np.sin(phase)

        # Start from BASELINE
        merged = dict(self.fallback)
        # Perturb a few layer keys
        for layer in merged:
            state = merged[layer]
            # Add drift to numeric values
            for key, val in state.items():
                if isinstance(val, (int, float)):
                    # Apply to a few specific keys
                    if key in ["GHG_forcing_Wm2", "net_forcing_Wm2", "arctic_amplification_K"]:
                        state[key] = val + drift * 0.5
                    elif key in ["AMOC_heat_transport_W", "total_bottom_water_Sv"]:
                        state[key] = val + drift * (-1e13)
                    elif key in ["permafrost_CO2_GtC_yr", "atmospheric_CO2_accumulation"]:
                        state[key] = val + drift * 0.02

        return merged


# ─────────────────────────────────────────────
# FACTORY — convenience for common setups
# ─────────────────────────────────────────────

def adapter_from_config(config: Dict) -> SensorAdapter:
    """
    Build an adapter from a config dict.

    Example:
        {
            "type": "csv",
            "path": "logs/sensors.csv",
            "format": "long",
            "fallback": "baseline"
        }
    """
    adapter_type = config.get("type", "dict")
    fallback = config.get("fallback", BASELINE)

    if adapter_type == "dict":
        return DictAdapter(config.get("readings", {}), fallback=fallback)

    elif adapter_type == "csv":
        return CSVAdapter(
            config["path"],
            long_format=(config.get("format", "long") == "long"),
            fallback=fallback,
        )

    elif adapter_type == "can":
        return CANBusAdapter(
            interface=config.get("interface", "can0"),
            bustype=config.get("bustype", "socketcan"),
            fallback=fallback,
        )

    elif adapter_type == "clock":
        return ClockAdapter(
            period_hours=config.get("period_hours", 24.0),
            amplitude=config.get("amplitude", 0.1),
            fallback=fallback,
        )

    elif adapter_type == "composite":
        adapters = [adapter_from_config(cfg) for cfg in config.get("sources", [])]
        return CompositeAdapter(adapters, fallback=fallback)

    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")



# assumption_validator/adapters.py

class SensorAdapter:
    """Base class — defines how raw data becomes layer_state dicts."""
    
    def read(self) -> Dict[int, Dict]:
        """Return layer_states dict (0-6) with current values."""
        raise NotImplementedError

class CANBusAdapter(SensorAdapter):
    """Reads from rig CAN bus via OBD-II or J1939."""
    # Maps CAN PIDs to layer_keys
    MAP = {
        "coolant_temp": "hydro_SST",
        "oil_pressure": "litho_fault_stress",  # proxy
        "rpm": "atmo_coriolis",  # not directly, but for demo
        # etc...
    }
    def __init__(self, can_interface, fallback=None):
        self.can = can_interface
        self.fallback = fallback or BASELINE

    def read(self) -> Dict[int, Dict]:
        raw = self.can.poll()
        # Translate into layer_states, fill missing from fallback
        ...

class CSVAdapter(SensorAdapter):
    """Reads from timestamped CSV — for replay or manual logging."""
    def __init__(self, csv_path, timestamps, fallback=None):
        ...

class ManualAdapter(SensorAdapter):
    """Accepts dict of manual readings (sight, sound, smell, feel)."""
    def __init__(self, readings: Dict[str, float], fallback=None):
        ...
