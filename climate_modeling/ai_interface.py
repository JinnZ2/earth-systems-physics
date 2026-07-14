# ai_interface.py
# climate_modeling
# CC0 — No Rights Reserved
#
# AI proposer for the meta-experiment loop. The dummy backend is rule-based and
# stdlib-only — it maps a detected failure to the structural repair that would
# address it. A real LLM backend can be dropped in behind the same interface;
# the openai import is deferred into the method so importing this module never
# requires the dependency.

# Named structural repairs, keyed by audit name -> the fix that addresses it.
PATCH_LIBRARY = {
    "Phase Change Blindness":
        "add an explicit threshold / switching term to the respiration law",
    "Threshold Smoothing":
        "narrow the transition width; do not smear a step over many degrees",
    "Stationarity Assumption":
        "let parameters or the baseline track the trend; recalibrate on a "
        "moving window instead of a fixed early one",
    "Missing Feedback":
        "add the omitted state variable and its reciprocal coupling",
    "Missing Positive Feedback":
        "add the amplifying loop and let its strength depend on the driver",
    "Omitted Variable":
        "measure and include the hidden covariate rather than assuming it "
        "constant",
    "Data Aggregation Error":
        "fit and force on the native (sub-daily) resolution, not daily means",
    "Temporal Aggregation Extremes":
        "resolve the extremes; averaging erases the events that drive collapse",
    "Cascade Speed Blindness":
        "add threshold + memory + feedback so the model can express a cascade",
    "Spatial Homogenization":
        "resolve spatial heterogeneity; a mean patch never crosses the local "
        "threshold the hot patch does",
    "Memory Amnesia":
        "add an accumulated-damage state so past stress lowers future capacity",
    "Cross-System Coupling":
        "couple the dependent domains; the domino is invisible when they are "
        "modelled in isolation",
    "Buffer Exhaustion":
        "add the buffer state and its depletion dynamics",
    "Clustered Extremes":
        "model serial dependence in the extremes, not just their variance",
    "Gaussian Blindness":
        "use a heavy-tailed noise model; equal variance is not equal tail risk",
    "Incentive Bias":
        "score models on out-of-sample cascade prediction, not parsimony alone",
}


class AIScientist:
    """Proposes a structural repair for an audit failure.

    Parameters
    ----------
    backend : str
        "dummy" (default, rule-based, stdlib-only) or "openai" (deferred import).
    """

    def __init__(self, backend="dummy", api_key=None, model="gpt-4"):
        self.backend = backend
        self.api_key = api_key
        self.model = model

    def propose_patch(self, context):
        """Return a dict with a ``suggestion`` (and ``reason``) for the failure.

        ``context`` is an audit result dict (as returned by ``BaseAudit.run``).
        """
        if self.backend == "dummy":
            name = context.get("audit_name", "")
            suggestion = PATCH_LIBRARY.get(
                name, "no automated repair known; inspect the trajectory")
            return {
                "suggestion": suggestion,
                "reason": (f"audit '{name}' detected a failure "
                           f"(metrics: {context.get('metrics', {})})"),
            }
        return self._call_openai(context)

    def _call_openai(self, context):  # pragma: no cover - requires network + key
        import json
        import openai

        openai.api_key = self.api_key
        prompt = (
            "You are auditing an ecological model. An audit detected a failure. "
            "Propose the minimal structural repair as one sentence.\n"
            f"Audit: {context.get('audit_name')}\n"
            f"Metrics: {context.get('metrics')}\n"
            f"True final: {context.get('true_final')}  "
            f"Audited final: {context.get('audited_final')}"
        )
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = resp.choices[0].message.content
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            return {"suggestion": text, "reason": "LLM free-text response"}
