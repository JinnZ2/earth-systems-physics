# assumption_validator/monitors.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# Live monitoring layer.
# Polls layer coupling_state outputs on a schedule.
# Tracks drift over time.
# Detects rate-of-change acceleration.
# Feeds registry for assumption validity assessment.
# This is the thing that watches the thing.

import time
import threading
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field

from cascade_engine import run_all_layers, BASELINE, SCENARIOS, run_cascade
from assumption_validator.registry import (
    full_report,
    assess_from_layer_states,
    detect_cascade_risk,
    global_confidence_multiplier,
    REGISTRY,
    RiskLevel,
)


# ─────────────────────────────────────────────
# TIME SERIES RECORD
# ─────────────────────────────────────────────

@dataclass
class AssumptionRecord:
    """Single timestamped measurement for one assumption."""
    timestamp  : datetime
    value      : float
    status     : str
    penalty    : float
    proximity  : float


@dataclass
class MonitorState:
    """
    Rolling time series for one assumption.
    Tracks history, drift rate, acceleration.
    """
    assumption_id  : str
    name           : str
    units          : str
    maxlen         : int = 8760          # one year at hourly resolution
    records        : deque = field(default_factory=deque)

    def __post_init__(self):
        self.records = deque(maxlen=self.maxlen)

    def push(self, record: AssumptionRecord):
        self.records.append(record)

    def latest(self) -> Optional[AssumptionRecord]:
        return self.records[-1] if self.records else None

    def values(self) -> List[float]:
        return [r.value for r in self.records if r.value is not None]

    def timestamps(self) -> List[datetime]:
        return [r.timestamp for r in self.records]

    def drift_rate(self, window: int = 24) -> Optional[float]:
        """
        Rate of change over last `window` records.
        Units: assumption units per record interval.
        Returns None if insufficient data.
        """
        vals = self.values()
        if len(vals) < 2:
            return None
        n = min(window, len(vals))
        recent = vals[-n:]
        if len(recent) < 2:
            return None
        # Simple linear slope
        x = np.arange(len(recent), dtype=float)
        slope = np.polyfit(x, recent, 1)[0]
        return float(slope)

    def acceleration(self, window: int = 168) -> Optional[float]:
        """
        Rate of change of drift rate — second derivative.
        Positive = worsening faster.
        Returns None if insufficient data.
        """
        vals = self.values()
        if len(vals) < 4:
            return None
        n = min(window, len(vals))
        recent = np.array(vals[-n:], dtype=float)
        x = np.arange(len(recent), dtype=float)
        # Fit quadratic — coefficient of x^2 is half-acceleration
        coeffs = np.polyfit(x, recent, 2)
        return float(2 * coeffs[0])

    def time_to_red(self) -> Optional[float]:
        """
        Extrapolate current drift rate to RED threshold.
        Returns hours to threshold, or None if moving away from red.
        """
        boundary = REGISTRY.get(self.assumption_id)
        if boundary is None:
            return None
        latest = self.latest()
        if latest is None or latest.value is None:
            return None
        rate = self.drift_rate()
        if rate is None or rate == 0:
            return None

        current = latest.value
        red     = boundary.red_threshold

        if boundary.higher_is_worse:
            if current >= red:
                return 0.0
            if rate <= 0:
                return None  # moving away
            return (red - current) / rate
        else:
            if current <= red:
                return 0.0
            if rate >= 0:
                return None  # moving away
            return (current - red) / abs(rate)

    def status_history(self, n: int = 24) -> List[str]:
        recent = list(self.records)[-n:]
        return [r.status for r in recent]

    def consecutive_yellow_or_red(self) -> int:
        """Count of consecutive most-recent records in YELLOW or RED."""
        count = 0
        for r in reversed(list(self.records)):
            if r.status in ("YELLOW", "RED"):
                count += 1
            else:
                break
        return count


# ─────────────────────────────────────────────
# CASCADE HISTORY
# ─────────────────────────────────────────────

@dataclass
class CascadeSnapshot:
    timestamp   : datetime
    level       : str
    n_red       : int
    n_yellow    : int
    n_coupled   : int
    multiplier  : float
    message     : str


# ─────────────────────────────────────────────
# ALERT
# ─────────────────────────────────────────────

@dataclass
class Alert:
    timestamp       : datetime
    assumption_id   : str
    assumption_name : str
    alert_type      : str   # STATUS_CHANGE | ACCELERATION | THRESHOLD_IMMINENT | CASCADE
    previous_status : str
    current_status  : str
    message         : str
    hours_to_red    : Optional[float] = None
    cascade_level   : Optional[str]   = None


# ─────────────────────────────────────────────
# MONITOR ENGINE
# ─────────────────────────────────────────────

class EarthSystemsMonitor:
    """
    Continuous monitor for the earth-systems-physics layer stack.

    Usage
    -----
    monitor = EarthSystemsMonitor()
    monitor.start()                         # background polling
    report  = monitor.current_report()      # latest full state
    alerts  = monitor.drain_alerts()        # unread alerts
    monitor.stop()
    """

    def __init__(
        self,
        params          : Dict          = None,
        poll_interval_s : float         = 60.0,
        alert_callbacks : List[Callable]= None,
    ):
        """
        params          : parameter dict for run_all_layers (defaults to BASELINE)
        poll_interval_s : seconds between polls (default 60)
        alert_callbacks : list of callables(Alert) for external notification
        """
        self.params           = dict(params or BASELINE)
        self.poll_interval    = poll_interval_s
        self.alert_callbacks  = alert_callbacks or []

        # Per-assumption rolling state
        self.states: Dict[str, MonitorState] = {
            aid: MonitorState(
                assumption_id = aid,
                name          = b.name,
                units         = b.units,
            )
            for aid, b in REGISTRY.items()
        }

        # Cascade history
        self.cascade_history: deque = deque(maxlen=8760)

        # Alert queue
        self._alerts: deque = deque(maxlen=1000)
        self._alert_lock    = threading.Lock()

        # Latest full report cache
        self._latest_report : Optional[Dict] = None
        self._latest_states : Optional[Dict] = None
        self._report_lock   = threading.Lock()

        # Thread control
        self._running  = False
        self._thread   = None
        self._poll_count = 0

    # ── PUBLIC API ───────────────────────────────────────────────────

    def start(self):
        """Start background polling thread."""
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(
            target=self._poll_loop, daemon=True, name="EarthSystemsMonitor"
        )
        self._thread.start()

    def stop(self):
        """Stop background polling thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)

    def poll_once(self, params: Dict = None) -> Dict:
        """
        Single synchronous poll. Returns full report.
        Useful for testing or forcing an update.
        """
        p = dict(params or self.params)
        return self._do_poll(p)

    def current_report(self) -> Optional[Dict]:
        """Return latest cached full report (thread-safe)."""
        with self._report_lock:
            return self._latest_report

    def current_layer_states(self) -> Optional[Dict]:
        """Return latest layer coupling_state outputs."""
        with self._report_lock:
            return self._latest_states

    def drain_alerts(self) -> List[Alert]:
        """Return and clear all pending alerts."""
        with self._alert_lock:
            alerts = list(self._alerts)
            self._alerts.clear()
        return alerts

    def assumption_trend(self, assumption_id: str) -> Dict:
        """
        Return trend analysis for a single assumption.
        """
        ms = self.states.get(assumption_id)
        if ms is None:
            return {"error": f"Unknown assumption: {assumption_id}"}

        latest = ms.latest()
        return {
            "assumption_id":           assumption_id,
            "name":                    ms.name,
            "units":                   ms.units,
            "latest_value":            latest.value if latest else None,
            "latest_status":           latest.status if latest else None,
            "drift_rate_per_hour":     ms.drift_rate(window=24),
            "acceleration":            ms.acceleration(window=168),
            "hours_to_red":            ms.time_to_red(),
            "consecutive_degraded":    ms.consecutive_yellow_or_red(),
            "record_count":            len(ms.records),
            "status_history_24h":      ms.status_history(24),
        }

    def all_trends(self) -> Dict[str, Dict]:
        """Return trend analysis for all assumptions."""
        return {aid: self.assumption_trend(aid) for aid in self.states}

    def cascade_trend(self, n: int = 24) -> List[Dict]:
        """Return recent cascade history."""
        recent = list(self.cascade_history)[-n:]
        return [
            {
                "timestamp":  s.timestamp.isoformat(),
                "level":      s.level,
                "n_red":      s.n_red,
                "n_yellow":   s.n_yellow,
                "n_coupled":  s.n_coupled,
                "multiplier": s.multiplier,
                "message":    s.message,
            }
            for s in recent
        ]

    def set_params(self, params: Dict):
        """Update simulation parameters (thread-safe)."""
        self.params = dict(params)

    def apply_scenario(self, scenario_name: str):
        """
        Apply a named scenario from cascade_engine.SCENARIOS
        by perturbing current params.
        """
        from cascade_engine import SCENARIOS, apply_forcing
        if scenario_name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}. "
                             f"Available: {list(SCENARIOS.keys())}")
        forcing      = SCENARIOS[scenario_name]
        self.params  = apply_forcing(self.params, forcing)

    # ── INTERNAL ─────────────────────────────────────────────────────

    def _poll_loop(self):
        """Background polling loop."""
        while self._running:
            try:
                self._do_poll(self.params)
            except Exception as exc:
                self._raise_alert(Alert(
                    timestamp       = datetime.utcnow(),
                    assumption_id   = "monitor",
                    assumption_name = "Monitor Engine",
                    alert_type      = "POLL_ERROR",
                    previous_status = "UNKNOWN",
                    current_status  = "ERROR",
                    message         = f"Poll error: {exc}",
                ))
            time.sleep(self.poll_interval)

    def _do_poll(self, params: Dict) -> Dict:
        """Execute one poll cycle."""
        now = datetime.utcnow()

        # Run physics
        layer_states = run_all_layers(params)

        # Full registry assessment
        report = full_report(layer_states)

        # Update per-assumption state and detect alerts
        prev_statuses = {
            aid: (ms.latest().status if ms.latest() else "UNKNOWN")
            for aid, ms in self.states.items()
        }

        for aid, assessment in report["assumptions"].items():
            ms = self.states.get(aid)
            if ms is None:
                continue

            value   = assessment.get("value")
            status  = assessment.get("status", "UNKNOWN")
            penalty = assessment.get("confidence_penalty", 0.0)
            prox    = assessment.get("proximity_to_red", 0.0)

            if isinstance(value, (int, float, np.floating)):
                record = AssumptionRecord(
                    timestamp = now,
                    value     = float(value),
                    status    = status,
                    penalty   = float(penalty) if isinstance(penalty, (int, float)) else 0.0,
                    proximity = float(prox)   if isinstance(prox,   (int, float)) else 0.0,
                )
                ms.push(record)

                # Alert: status change
                prev = prev_statuses.get(aid, "UNKNOWN")
                if status != prev and prev != "UNKNOWN":
                    self._raise_alert(Alert(
                        timestamp       = now,
                        assumption_id   = aid,
                        assumption_name = ms.name,
                        alert_type      = "STATUS_CHANGE",
                        previous_status = prev,
                        current_status  = status,
                        message         = (
                            f"{ms.name} changed from {prev} to {status}. "
                            f"Value: {value:.4g} {ms.units}. "
                            f"{assessment.get('notes', '')}"
                        ),
                    ))

                # Alert: acceleration
                accel = ms.acceleration()
                if accel is not None and abs(accel) > 0:
                    boundary = REGISTRY.get(aid)
                    if boundary:
                        accel_threshold = abs(boundary.red_threshold - boundary.green_range[0]) * 0.001
                        if abs(accel) > accel_threshold and status in ("YELLOW", "RED"):
                            self._raise_alert(Alert(
                                timestamp       = now,
                                assumption_id   = aid,
                                assumption_name = ms.name,
                                alert_type      = "ACCELERATION",
                                previous_status = status,
                                current_status  = status,
                                message         = (
                                    f"{ms.name} drift accelerating. "
                                    f"Acceleration: {accel:.3g} {ms.units}/record². "
                                    f"Current: {value:.4g} {ms.units}."
                                ),
                            ))

                # Alert: threshold imminent
                hours = ms.time_to_red()
                if hours is not None and hours < 720:  # within 30 days
                    self._raise_alert(Alert(
                        timestamp       = now,
                        assumption_id   = aid,
                        assumption_name = ms.name,
                        alert_type      = "THRESHOLD_IMMINENT",
                        previous_status = status,
                        current_status  = status,
                        message         = (
                            f"{ms.name} RED threshold in {hours:.0f} hours "
                            f"at current rate. Value: {value:.4g}, "
                            f"Threshold: {REGISTRY[aid].red_threshold:.4g} {ms.units}."
                        ),
                        hours_to_red    = hours,
                    ))

        # Cascade snapshot
        cascade   = report["cascade"]
        multiplier = report["global_confidence_multiplier"]
        snap = CascadeSnapshot(
            timestamp  = now,
            level      = cascade["cascade_level"],
            n_red      = cascade["n_red"],
            n_yellow   = cascade["n_yellow"],
            n_coupled  = cascade["n_coupled_pairs"],
            multiplier = multiplier,
            message    = cascade["message"],
        )
        self.cascade_history.append(snap)

        # Alert: cascade escalation
        prev_snap = None
        if len(self.cascade_history) >= 2:
            prev_snap = list(self.cascade_history)[-2]
        if prev_snap and snap.level != prev_snap.level:
            levels = ["MINIMAL", "LOW", "MODERATE", "HIGH", "CRITICAL"]
            if levels.index(snap.level) > levels.index(prev_snap.level):
                self._raise_alert(Alert(
                    timestamp       = now,
                    assumption_id   = "cascade",
                    assumption_name = "Cascade Engine",
                    alert_type      = "CASCADE",
                    previous_status = prev_snap.level,
                    current_status  = snap.level,
                    message         = (
                        f"Cascade risk escalated: {prev_snap.level} → {snap.level}. "
                        f"RED: {snap.n_red}, YELLOW: {snap.n_yellow}, "
                        f"Coupled pairs: {snap.n_coupled}. "
                        f"Global confidence: {multiplier:.0%}. "
                        f"{cascade['message']}"
                    ),
                    cascade_level   = snap.level,
                ))

        # Enrich report with trend data
        report["trends"]           = self.all_trends()
        report["cascade_history"]  = self.cascade_trend(n=24)
        report["poll_count"]       = self._poll_count
        report["timestamp"]        = now.isoformat()

        self._poll_count += 1

        # Cache
        with self._report_lock:
            self._latest_report = report
            self._latest_states = layer_states

        return report

    def _raise_alert(self, alert: Alert):
        """Queue alert and call registered callbacks."""
        with self._alert_lock:
            self._alerts.append(alert)
        for cb in self.alert_callbacks:
            try:
                cb(alert)
            except Exception:
                pass


# ─────────────────────────────────────────────
# CONSOLE REPORTER
# Prints monitor output in single-tap-copyable format
# ─────────────────────────────────────────────

def print_report(report: Dict, show_green: bool = False):
    """
    Print monitor report. Designed for mobile — full shape visible at once.
    show_green : if False, only shows YELLOW/RED/UNKNOWN
    """
    ts  = report.get("timestamp", "")
    s   = report.get("summary", {})
    cas = report.get("cascade", {})
    mul = report.get("global_confidence_multiplier", 1.0)

    print("=" * 56)
    print(f"EARTH SYSTEMS MONITOR  {ts[:19]}")
    print("=" * 56)
    print(f"  Confidence : {mul:.0%}")
    print(f"  GREEN      : {s.get('green',0)}")
    print(f"  YELLOW     : {s.get('yellow',0)}")
    print(f"  RED        : {s.get('red',0)}")
    print(f"  CASCADE    : {cas.get('cascade_level','?')}")
    print(f"  {cas.get('message','')}")
    print()

    # Assumptions
    assumptions = report.get("assumptions", {})
    for aid, data in sorted(assumptions.items()):
        status = data.get("status", "?")
        if not show_green and status == "GREEN":
            continue
        val   = data.get("value")
        units = data.get("units", "")
        prox  = data.get("proximity_to_red", 0.0)
        val_str = f"{val:.4g}" if isinstance(val, (int, float)) else str(val)

        # Trend annotation
        trend = report.get("trends", {}).get(aid, {})
        drift = trend.get("drift_rate_per_hour")
        h2r   = trend.get("hours_to_red")
        drift_str = f"  drift {drift:+.3g}/hr" if drift is not None else ""
        h2r_str   = f"  ⚠ RED in {h2r:.0f}h" if h2r is not None and h2r < 720 else ""

        marker = {"GREEN": "✓", "YELLOW": "~", "RED": "✗"}.get(status, "?")
        print(f"  [{marker}] {status:<7} L{data.get('source_layer','?')}  "
              f"{data.get('name','')[:30]:<30}  "
              f"{val_str} {units}{drift_str}{h2r_str}")

    # Cascade couplings
    coupled = cas.get("coupled_degraded", [])
    if coupled:
        print()
        print("  ACTIVE COUPLING PATHS:")
        for a, b in coupled:
            na = REGISTRY.get(a, None)
            nb = REGISTRY.get(b, None)
            na_s = na.name if na else a
            nb_s = nb.name if nb else b
            print(f"    {na_s}  →  {nb_s}")

    # Irreversible thresholds
    irreversible = cas.get("irreversible_active", [])
    if irreversible:
        print()
        print("  IRREVERSIBLE THRESHOLDS ACTIVE:")
        for aid in irreversible:
            b = REGISTRY.get(aid)
            print(f"    ✗ {b.name if b else aid}")

    print("=" * 56)


# ─────────────────────────────────────────────
# ALERT PRINTER
# ─────────────────────────────────────────────

def print_alert(alert: Alert):
    """Default alert callback — prints to stdout."""
    icons = {
        "STATUS_CHANGE":     "⚡",
        "ACCELERATION":      "↑↑",
        "THRESHOLD_IMMINENT":"⏳",
        "CASCADE":           "🔴",
        "POLL_ERROR":        "⚠",
    }
    icon = icons.get(alert.alert_type, "!")
    print(f"\n{icon} ALERT [{alert.alert_type}] {alert.timestamp.isoformat()[:19]}")
    print(f"   {alert.assumption_name}")
    print(f"   {alert.previous_status} → {alert.current_status}")
    print(f"   {alert.message}")
    if alert.hours_to_red is not None:
        print(f"   Hours to RED: {alert.hours_to_red:.0f}")
    if alert.cascade_level:
        print(f"   Cascade level: {alert.cascade_level}")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("earth-systems-physics / assumption_validator / monitors")
    print("Starting monitor — single poll with BASELINE parameters\n")

    monitor = EarthSystemsMonitor(
        params           = BASELINE,
        poll_interval_s  = 60.0,
        alert_callbacks  = [print_alert],
    )

    # Single synchronous poll
    report = monitor.poll_once()
    print_report(report, show_green=False)

    # Trend sample
    print("\nSAMPLE TRENDS (first 5 assumptions with records):")
    trends = report.get("trends", {})
    shown  = 0
    for aid, t in trends.items():
        if t.get("latest_value") is not None:
            print(f"  {t['name'][:40]:<40}  "
                  f"drift: {str(t.get('drift_rate_per_hour','—'))[:10]}  "
                  f"h2red: {str(t.get('hours_to_red','—'))[:8]}")
            shown += 1
            if shown >= 5:
                break

    # Demo: run a scenario and re-poll
    print("\nApplying scenario: permafrost_acceleration")
    monitor.apply_scenario("permafrost_acceleration")
    report2 = monitor.poll_once()
    print_report(report2, show_green=False)

    alerts = monitor.drain_alerts()
    if alerts:
        print(f"\n{len(alerts)} alert(s) generated:")
        for a in alerts:
            print_alert(a)
    else:
        print("\nNo alerts generated on first two polls.")

    print("\nTo run continuous monitoring:")
    print("  monitor.start()")
    print("  # ... your code ...")
    print("  monitor.stop()")
