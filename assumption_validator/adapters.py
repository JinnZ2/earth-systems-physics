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
