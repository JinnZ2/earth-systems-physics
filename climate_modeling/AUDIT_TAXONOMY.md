# Model Failure Taxonomy

Each row is a controlled experiment in `audits/` where the true generative
process is **known** (we built it), so a detected failure is a genuine failure
of a modelling simplification — not a fitting artifact. Many rows target the
same underlying danger: **systematic underestimation of how fast a system can
collapse.**

| Audit | Philosophical fallacy | Mathematical condition | Real-world consequence |
|-------|-----------------------|------------------------|------------------------|
| Phase Change Blindness | Smoothness assumption — all change is gradual | No threshold/switching term in the ODE | Underestimating collapse from sudden extremes (bleaching, crop failure) |
| Threshold Smoothing | Transitions can be smeared without loss | A step spread over a wide sigmoid | Onset mis-timed; die-off looks earlier and gentler than it is |
| Stationarity Assumption | The past predicts the future unchanged | Constant parameters under non-stationary forcing | Projections diverge from reality as warming accelerates |
| Missing Feedback | Unidirectional causation | Omitted state variable + reciprocal coupling | Over/underestimating carbon dynamics; wrong management calls |
| Missing Positive Feedback | Amplifying loops are second-order | Feedback strength independent of the driver | Underestimating warming-driven acceleration |
| Omitted Variable | All relevant drivers are known | Missing covariate; residuals correlate with a hidden driver | Poor forecasts where an unmeasured factor dominates |
| Data Aggregation Error | Resolution is free to discard | Jensen's inequality on a nonlinear response fed averaged inputs | Biased parameters from daily/seasonal aggregates |
| Temporal Aggregation Extremes | Averaging preserves the signal | Sub-daily extremes erased by daily means | Cascade timeline extended; extinction risk understated |
| Cascade Speed Blindness | Collapse is slow and linear | Threshold + memory + feedback all absent | "50 years" when the truth is 5 |
| Spatial Homogenization | A mean cell represents the field | Averaging temperature below a local threshold | Local ignition + propagation never seen |
| Memory Amnesia | Only the current state matters | No accumulated-damage state (Markovian) | Predicting full recovery after repeated stress |
| Cross-System Coupling | Domains can be modelled in isolation | Missing inter-domain coupling | Pollinator → plant (etc.) dominoes are invisible |
| Buffer Exhaustion | Capacity is constant | Hidden reservoir depletes then gates the response | Sudden wilting/crash after a slow-looking trend |
| Clustered Extremes | Extremes are independent | Serial dependence (AR) ignored at equal variance | Compound events treated as astronomically unlikely |
| Gaussian Blindness | Equal variance is equal risk | Thin-tailed noise where the response is convex in magnitude | 1-in-100-yr events arriving every decade; collapse sooner |
| Incentive Bias | Parsimony is a proxy for truth | Model selection rewards simplicity over out-of-sample cascade skill | The chosen model is confident and wrong about speed |

## Why this is "science about how we do science"

Every audit is a controlled experiment where the truth is known, so a
discrepancy caught here is an epistemic error that would slip silently into a
real-world study where the truth isn't known. Cataloguing the errors, and the
conditions that trigger them, turns a modelling framework into a diagnostic
laboratory for model review — and with the AI proposer in the loop
(`meta_experiments.py`), a partially automated one.
