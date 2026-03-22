# assumption_validator/api.py
# earth-systems-physics
# CC0 — No Rights Reserved
#
# REST API exposing live assumption validity to any external system.
# AI models, grid operators, climate tools, autonomous systems —
# anything that needs to know whether its equations are still valid
# can query this endpoint before acting.
#
# Requires: pip install flask flask-cors

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import threading
import json
import time
from datetime import datetime
from typing import Dict, Optional

from cascade_engine import BASELINE, SCENARIOS, run_all_layers, run_cascade
from assumption_validator.registry import (
    full_report,
    REGISTRY,
    RiskLevel,
)
from assumption_validator.monitors import (
    EarthSystemsMonitor,
    print_alert,
    Alert,
)


# ─────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

# Global monitor — started once at launch
_monitor: Optional[EarthSystemsMonitor] = None
_monitor_lock = threading.Lock()


def get_monitor() -> EarthSystemsMonitor:
    global _monitor
    with _monitor_lock:
        if _monitor is None:
            _monitor = EarthSystemsMonitor(
                params           = dict(BASELINE),
                poll_interval_s  = 60.0,
                alert_callbacks  = [print_alert],
            )
            _monitor.start()
        return _monitor


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _json(obj, status=200):
    return Response(
        json.dumps(obj, indent=2, default=str),
        status=status,
        mimetype="application/json",
    )


def _error(msg, status=400):
    return _json({"error": msg}, status)


def _status_color(level: str) -> str:
    return {
        "GREEN":    "✓",
        "YELLOW":   "~",
        "RED":      "✗",
        "CRITICAL": "🔴",
        "HIGH":     "⚠",
        "MODERATE": "~",
        "LOW":      "·",
        "MINIMAL":  "·",
    }.get(level, "?")


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

# ── HEALTH ───────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """
    Service liveness check.
    Returns monitor status and uptime.
    """
    m = get_monitor()
    r = m.current_report()
    return _json({
        "status":        "operational",
        "service":       "earth-systems-physics / assumption-validator",
        "poll_count":    r.get("poll_count", 0) if r else 0,
        "last_poll":     r.get("timestamp")     if r else None,
        "assumptions":   len(REGISTRY),
        "scenarios":     list(SCENARIOS.keys()),
        "timestamp":     datetime.utcnow().isoformat(),
    })


# ── FULL VALIDITY REPORT ─────────────────────

@app.route("/v1/validity", methods=["GET"])
def validity():
    """
    Full assumption validity report.

    Query params:
        refresh=true   : force a new poll before returning
        layer=<int>    : filter to assumptions from one layer
        status=yellow  : filter to YELLOW|RED only
    """
    m = get_monitor()

    if request.args.get("refresh", "false").lower() == "true":
        m.poll_once()

    r = m.current_report()
    if r is None:
        r = m.poll_once()

    # Filters
    layer_filter  = request.args.get("layer")
    status_filter = request.args.get("status", "").upper()

    assumptions = r.get("assumptions", {})

    if layer_filter is not None:
        try:
            lf = int(layer_filter)
            assumptions = {
                k: v for k, v in assumptions.items()
                if v.get("source_layer") == lf
            }
        except ValueError:
            return _error("layer must be an integer 0-6")

    if status_filter in ("YELLOW", "RED"):
        assumptions = {
            k: v for k, v in assumptions.items()
            if v.get("status") == status_filter
        }

    return _json({
        "timestamp":                    r.get("timestamp"),
        "global_confidence_multiplier": r.get("global_confidence_multiplier"),
        "summary":                      r.get("summary"),
        "cascade":                      r.get("cascade"),
        "assumptions":                  assumptions,
    })


# ── SINGLE ASSUMPTION ────────────────────────

@app.route("/v1/validity/<assumption_id>", methods=["GET"])
def validity_single(assumption_id: str):
    """
    Validity status for one assumption by ID.
    Returns current value, status, trend, and time-to-red.

    Path:
        assumption_id : key from registry (e.g. bio_permafrost_flux)
    """
    if assumption_id not in REGISTRY:
        available = sorted(REGISTRY.keys())
        return _error(
            f"Unknown assumption '{assumption_id}'. "
            f"Available: {available}",
            status=404,
        )

    m = get_monitor()
    r = m.current_report()
    if r is None:
        r = m.poll_once()

    assessment = r.get("assumptions", {}).get(assumption_id, {})
    trend      = r.get("trends",      {}).get(assumption_id, {})
    boundary   = REGISTRY[assumption_id]

    return _json({
        "assumption_id":    assumption_id,
        "name":             boundary.name,
        "parameter":        boundary.parameter,
        "units":            boundary.units,
        "source_layer":     boundary.source_layer,
        "layer_key":        boundary.layer_key,
        "current_value":    assessment.get("value"),
        "status":           assessment.get("status"),
        "confidence_penalty": assessment.get("confidence_penalty"),
        "proximity_to_red": assessment.get("proximity_to_red"),
        "green_range":      boundary.green_range,
        "red_threshold":    boundary.red_threshold,
        "couplings":        boundary.couplings,
        "notes":            boundary.notes,
        "trend": {
            "drift_rate_per_hour":  trend.get("drift_rate_per_hour"),
            "acceleration":         trend.get("acceleration"),
            "hours_to_red":         trend.get("hours_to_red"),
            "consecutive_degraded": trend.get("consecutive_degraded"),
            "status_history_24h":   trend.get("status_history_24h"),
        },
        "timestamp": r.get("timestamp"),
    })


# ── LAYER SUMMARY ────────────────────────────

@app.route("/v1/layers", methods=["GET"])
def layers():
    """
    Validity summary grouped by physics layer.
    Shows worst status per layer and contributing assumptions.
    """
    m = get_monitor()
    r = m.current_report()
    if r is None:
        r = m.poll_once()

    assumptions = r.get("assumptions", {})
    layer_names = {
        0: "Electromagnetics",
        1: "Magnetosphere",
        2: "Ionosphere",
        3: "Atmosphere",
        4: "Hydrosphere",
        5: "Lithosphere",
        6: "Biosphere",
    }
    status_rank = {"GREEN": 0, "YELLOW": 1, "RED": 2, "UNKNOWN": -1}

    layers_out = {}
    for layer_id, layer_name in layer_names.items():
        layer_assm = {
            k: v for k, v in assumptions.items()
            if v.get("source_layer") == layer_id
        }
        if not layer_assm:
            continue

        worst = max(
            layer_assm.values(),
            key=lambda v: status_rank.get(v.get("status", "UNKNOWN"), -1),
        )
        worst_status = worst.get("status", "UNKNOWN")

        layers_out[str(layer_id)] = {
            "layer_id":    layer_id,
            "name":        layer_name,
            "worst_status": worst_status,
            "assumption_count": len(layer_assm),
            "assumptions": {
                k: {
                    "name":   v.get("name"),
                    "status": v.get("status"),
                    "value":  v.get("value"),
                    "units":  v.get("units"),
                }
                for k, v in layer_assm.items()
            },
        }

    return _json({
        "timestamp": r.get("timestamp"),
        "layers":    layers_out,
        "cascade":   r.get("cascade"),
    })


# ── ADJUST PREDICTION ────────────────────────

@app.route("/v1/adjust", methods=["POST"])
def adjust():
    """
    Submit a prediction; get back confidence-adjusted version.

    Request body (JSON):
    {
        "prediction":            { ...any dict... },
        "base_confidence":       0.85,
        "required_assumptions":  ["bio_permafrost_flux", "hydro_AMOC_collapse"],
        "model_name":            "optional label",
        "derivation_regime":     "holocene"
    }

    Returns the prediction with adjusted confidence and full assumption context.
    """
    data = request.get_json(silent=True)
    if not data:
        return _error("JSON body required")

    prediction       = data.get("prediction", {})
    base_conf        = data.get("base_confidence", 0.5)
    required         = data.get("required_assumptions")   # list or None
    model_name       = data.get("model_name", "unnamed")
    deriv_regime     = data.get("derivation_regime", "holocene")

    if not (0.0 <= base_conf <= 1.0):
        return _error("base_confidence must be 0.0 – 1.0")

    m = get_monitor()
    r = m.current_report()
    if r is None:
        r = m.poll_once()

    assumptions = r.get("assumptions", {})

    # Filter to required assumptions if specified
    if required:
        unknown = [a for a in required if a not in REGISTRY]
        if unknown:
            return _error(f"Unknown assumption IDs: {unknown}")
        subset = {k: v for k, v in assumptions.items() if k in required}
    else:
        subset = assumptions

    # Compute multiplier
    multiplier = 1.0
    for v in subset.values():
        penalty = v.get("confidence_penalty", 0.0)
        if isinstance(penalty, (int, float)):
            multiplier *= (1.0 - penalty)

    adjusted_conf = base_conf * multiplier

    # Overall status
    reds    = [k for k, v in subset.items() if v.get("status") == "RED"]
    yellows = [k for k, v in subset.items() if v.get("status") == "YELLOW"]

    if reds:
        overall = "INVALID"
    elif yellows:
        overall = "DEGRADED"
    else:
        overall = "VALID"

    # Regime check — simple
    current_co2 = None
    co2_data = assumptions.get("bio_co2_accumulation") or assumptions.get("atmo_ghg_forcing")
    regime_warning = None
    if deriv_regime == "holocene":
        atmo = r.get("assumptions", {}).get("atmo_ghg_forcing", {})
        ghg  = atmo.get("value", 0)
        if isinstance(ghg, (int, float)) and ghg > 3.7:
            regime_warning = (
                "Model derived in Holocene regime. "
                "Current GHG forcing exceeds Holocene range. "
                "Equations may not apply to current conditions."
            )

    # Build warnings list
    warnings = []
    for k in reds:
        b = REGISTRY.get(k)
        warnings.append(
            f"CRITICAL [{k}]: {b.name if b else k} assumption is RED. "
            f"Value: {assumptions[k].get('value'):.4g} {assumptions[k].get('units','')}."
        )
    for k in yellows:
        b = REGISTRY.get(k)
        warnings.append(
            f"CAUTION [{k}]: {b.name if b else k} assumption is YELLOW. "
            f"Value: {assumptions[k].get('value'):.4g} {assumptions[k].get('units','')}."
        )
    if regime_warning:
        warnings.append(regime_warning)

    return _json({
        "model_name":            model_name,
        "derivation_regime":     deriv_regime,
        "prediction":            prediction,
        "original_confidence":   base_conf,
        "adjusted_confidence":   adjusted_conf,
        "confidence_multiplier": multiplier,
        "confidence_loss_pct":   round((1.0 - multiplier) * 100, 1),
        "overall_status":        overall,
        "red_assumptions":       reds,
        "yellow_assumptions":    yellows,
        "warnings":              warnings,
        "regime_warning":        regime_warning,
        "cascade_level":         r.get("cascade", {}).get("cascade_level"),
        "timestamp":             r.get("timestamp"),
    })


# ── CASCADE STATUS ───────────────────────────

@app.route("/v1/cascade", methods=["GET"])
def cascade():
    """
    Current cascade risk level and history.

    Query params:
        history=<int>  : number of historical snapshots (default 24)
    """
    n = int(request.args.get("history", 24))
    m = get_monitor()
    r = m.current_report()
    if r is None:
        r = m.poll_once()

    return _json({
        "current":  r.get("cascade"),
        "history":  m.cascade_trend(n=n),
        "timestamp": r.get("timestamp"),
    })


# ── TRENDS ───────────────────────────────────

@app.route("/v1/trends", methods=["GET"])
def trends():
    """
    Drift rate and time-to-red for all assumptions.
    Sorted by proximity to red threshold.

    Query params:
        imminent=true  : only show assumptions with hours_to_red < 720
    """
    m = get_monitor()
    r = m.current_report()
    if r is None:
        r = m.poll_once()

    trend_data = r.get("trends", {})
    imminent   = request.args.get("imminent", "false").lower() == "true"

    if imminent:
        trend_data = {
            k: v for k, v in trend_data.items()
            if isinstance(v.get("hours_to_red"), (int, float))
            and v["hours_to_red"] < 720
        }

    # Sort by hours_to_red ascending (soonest first)
    sorted_trends = dict(
        sorted(
            trend_data.items(),
            key=lambda item: (
                item[1].get("hours_to_red") or 1e9
            ),
        )
    )

    return _json({
        "timestamp": r.get("timestamp"),
        "trends":    sorted_trends,
    })


# ── ALERTS ───────────────────────────────────

@app.route("/v1/alerts", methods=["GET"])
def alerts():
    """
    Return and drain pending alerts.
    Once read, alerts are cleared from the queue.
    """
    m  = get_monitor()
    al = m.drain_alerts()

    return _json({
        "count":  len(al),
        "alerts": [
            {
                "timestamp":       a.timestamp.isoformat(),
                "assumption_id":   a.assumption_id,
                "assumption_name": a.assumption_name,
                "alert_type":      a.alert_type,
                "previous_status": a.previous_status,
                "current_status":  a.current_status,
                "message":         a.message,
                "hours_to_red":    a.hours_to_red,
                "cascade_level":   a.cascade_level,
            }
            for a in al
        ],
    })


# ── SCENARIOS ────────────────────────────────

@app.route("/v1/scenarios", methods=["GET"])
def list_scenarios():
    """List available cascade scenarios."""
    out = {}
    for name, forcing in SCENARIOS.items():
        out[name] = {
            "description": forcing.description,
            "layer":       forcing.layer,
            "variable":    forcing.variable,
            "magnitude":   forcing.magnitude,
            "units":       forcing.units,
        }
    return _json({"scenarios": out})


@app.route("/v1/scenarios/<name>", methods=["POST"])
def run_scenario(name: str):
    """
    Run a named scenario and return the full validity report
    for the perturbed state — without changing monitor params.

    Useful for: what-if analysis, forecasting,
    testing which assumptions a given forcing breaks.
    """
    if name not in SCENARIOS:
        return _error(
            f"Unknown scenario '{name}'. "
            f"Available: {list(SCENARIOS.keys())}",
            status=404,
        )

    m = get_monitor()
    baseline_params = dict(m.params)

    # Run scenario (does not modify monitor state)
    result = run_cascade(SCENARIOS[name], baseline=baseline_params, verbose=False)

    # Full validity on perturbed states
    report = full_report(result.layer_states)

    return _json({
        "scenario":       name,
        "forcing": {
            "description": SCENARIOS[name].description,
            "layer":       SCENARIOS[name].layer,
            "variable":    SCENARIOS[name].variable,
            "magnitude":   SCENARIOS[name].magnitude,
            "units":       SCENARIOS[name].units,
        },
        "validity": {
            "global_confidence_multiplier": report["global_confidence_multiplier"],
            "summary":   report["summary"],
            "cascade":   report["cascade"],
        },
        "assumptions_changed": {
            k: v for k, v in report["assumptions"].items()
            if v.get("status") in ("YELLOW", "RED")
        },
        "thresholds_crossed": result.threshold_crossings,
        "amplifying_loops":   result.amplifying_loops,
        "timestamp": datetime.utcnow().isoformat(),
    })


# ── APPLY SCENARIO TO MONITOR ────────────────

@app.route("/v1/scenarios/<name>/apply", methods=["POST"])
def apply_scenario(name: str):
    """
    Apply a scenario to the monitor's live parameters.
    Subsequent polls will use perturbed parameters.

    POST /v1/scenarios/permafrost_acceleration/apply
    """
    if name not in SCENARIOS:
        return _error(
            f"Unknown scenario '{name}'.",
            status=404,
        )

    m = get_monitor()
    m.apply_scenario(name)
    r = m.poll_once()

    return _json({
        "applied":   name,
        "message":   f"Monitor parameters updated with scenario '{name}'",
        "cascade":   r.get("cascade"),
        "summary":   r.get("summary"),
        "timestamp": r.get("timestamp"),
    })


# ── RESET MONITOR ────────────────────────────

@app.route("/v1/reset", methods=["POST"])
def reset():
    """Reset monitor parameters to BASELINE."""
    m = get_monitor()
    m.set_params(dict(BASELINE))
    r = m.poll_once()
    return _json({
        "message":   "Monitor reset to BASELINE",
        "cascade":   r.get("cascade"),
        "summary":   r.get("summary"),
        "timestamp": r.get("timestamp"),
    })


# ── REGISTRY ─────────────────────────────────

@app.route("/v1/registry", methods=["GET"])
def registry():
    """
    Return full assumption registry — boundaries, units,
    source layers, couplings, notes.
    """
    out = {}
    for aid, b in REGISTRY.items():
        out[aid] = {
            "name":             b.name,
            "parameter":        b.parameter,
            "units":            b.units,
            "green_range":      b.green_range,
            "yellow_range":     b.yellow_range,
            "red_threshold":    b.red_threshold,
            "higher_is_worse":  b.higher_is_worse,
            "source_layer":     b.source_layer,
            "layer_key":        b.layer_key,
            "couplings":        b.couplings,
            "rate_of_change":   b.rate_of_change,
            "notes":            b.notes,
        }
    return _json({"count": len(out), "registry": out})


# ── SSE STREAM ───────────────────────────────

@app.route("/v1/stream", methods=["GET"])
def stream():
    """
    Server-sent events stream of assumption validity updates.
    Clients receive a JSON event each poll cycle.

    Usage:
        curl -N http://localhost:5000/v1/stream
    """
    m = get_monitor()

    def event_generator():
        last_poll = -1
        while True:
            r = m.current_report()
            if r is not None:
                poll = r.get("poll_count", 0)
                if poll != last_poll:
                    last_poll = poll
                    payload = json.dumps({
                        "timestamp":   r.get("timestamp"),
                        "multiplier":  r.get("global_confidence_multiplier"),
                        "summary":     r.get("summary"),
                        "cascade":     r.get("cascade"),
                    }, default=str)
                    yield f"data: {payload}\n\n"
            time.sleep(5)

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────

def print_routes():
    print("=" * 56)
    print("EARTH SYSTEMS PHYSICS — ASSUMPTION VALIDATOR API")
    print("=" * 56)
    routes = [
        ("GET",  "/health",                    "Service liveness"),
        ("GET",  "/v1/validity",               "Full validity report"),
        ("GET",  "/v1/validity/<id>",          "Single assumption"),
        ("GET",  "/v1/layers",                 "Per-layer summary"),
        ("POST", "/v1/adjust",                 "Adjust prediction confidence"),
        ("GET",  "/v1/cascade",                "Cascade status + history"),
        ("GET",  "/v1/trends",                 "Drift rates + time-to-red"),
        ("GET",  "/v1/alerts",                 "Drain alert queue"),
        ("GET",  "/v1/scenarios",              "List scenarios"),
        ("POST", "/v1/scenarios/<name>",       "Run scenario (read-only)"),
        ("POST", "/v1/scenarios/<name>/apply", "Apply scenario to monitor"),
        ("POST", "/v1/reset",                  "Reset to BASELINE"),
        ("GET",  "/v1/registry",               "Full assumption registry"),
        ("GET",  "/v1/stream",                 "SSE live updates"),
    ]
    for method, path, desc in routes:
        print(f"  {method:<5} {path:<38} {desc}")
    print("=" * 56)


if __name__ == "__main__":
    print_routes()
    print("Starting monitor...")
    get_monitor()   # initializes and starts background polling
    print("Monitor running. Starting API on port 5000.\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
