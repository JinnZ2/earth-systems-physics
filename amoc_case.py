"""
amoc_case.py  —  CC0, stdlib only

Driver: runs the AMOC / Gulf-Stream early-warning signal through curiosity_engine.py.

Observation (van Westen & Dijkstra 2026, Comm. Earth & Env. 7:197;
high-res 0.1deg ocean sim + satellite altimetry 1993-2024):
  AMOC weakening drifts the Gulf Stream near Cape Hatteras northward gradually
  (~133 km over ~392 model years), then ABRUPTLY jumps ~219 km within 2 years,
  a few decades before AMOC collapse. Satellite + subsurface obs already show
  the northward trend -> the early stage is present-day, not hypothetical.

The model's clock:
  ~392 yr slow drift, ~25-yr lead from the abrupt jump to collapse.
  BUT: the simulation used a SLOWLY-INCREASING freshwater forcing. Co-author
  Ben-Yami states plainly the real forcing rate is faster, so the 25-yr lead
  "could shrink to almost nothing."

The thing Kavik's gut flagged, made explicit:
  The spatial markers (northward drift, abrupt jump, DWBC weakening) are VALID.
  The TIMELINE bolted to them is inherited from a forcing regime that does not
  match reality. Real forcing is fast and still accelerating. A system forced
  faster than its equilibration time does not glide to a tipping point on the
  slow-forcing schedule — it OVERSHOOTS and RINGS (oscillates), with rising
  amplitude, until one overshoot fails to recover. So:
    - collapse likely sooner than 25-34 yr from the jump
    - preceded by oscillation, not smooth approach
    - the slow-forcing timeline is a FALSE FIT of an old clock to new physics

This is the same frame-collapse the rest of the stack documents: fitting the
SHAPE of a past/slow cascade onto a faster load and importing its schedule.

Run:  python3 amoc_case.py
"""

from curiosity_engine import (
    Configuration, Alternative, Phenomenon, Hypothesis, wonder, hubris_check
)


def main():
    p = Phenomenon(
        survivor=Configuration(
            name="northward Gulf-Stream shift as AMOC early-warning, WITH its "
                 "~392yr-drift / ~25yr-lead timeline",
            conserves={"energy", "momentum", "information", "load_path"},
            selected_in="high-res ocean sim under SLOWLY-increasing freshwater forcing",
        ),
        alternatives=[
            Alternative("same spatial markers but under FAST (real, accelerating) forcing",
                        differs_by="forcing rate >> system equilibration rate",
                        status="works_elsewhere?"),
            Alternative("smooth monotonic approach to tipping (no oscillation)",
                        differs_by="assumes system equilibrates between forcing increments",
                        status="rejected_here"),
            Alternative("markers are response-to-weakening only, never cross to collapse",
                        differs_by="northward jump happens but AMOC restabilizes",
                        status="untested"),
            Alternative("the ~25yr lead transferred directly to the real world",
                        differs_by="borrows the slow-forcing clock unchanged",
                        status="rejected_here"),
        ],
        note="Two facts to honor: the spatial markers are observed in real data; "
             "the timeline was generated under a forcing rate slower than reality.",
    )

    hypotheses = [
        Hypothesis(
            why="FORCING-RATE MISMATCH (false fit of clock): the markers are valid but "
                "the 392yr/25yr schedule is an artifact of slow forcing. Under fast, "
                "accelerating forcing the lead collapses toward zero and the approach "
                "is NOT smooth — the system overshoots and oscillates because it can't "
                "equilibrate between increments.",
            would_break="if true, raising the forcing RATE in the same model (holding "
                        "total freshwater equal) should (a) shorten the jump->collapse "
                        "lead and (b) introduce growing-amplitude oscillation before "
                        "collapse",
            test="rerun the 0.1deg sim across a sweep of dF/dt at matched cumulative F; "
                 "measure lead-time and pre-collapse variance/oscillation vs dF/dt",
            explains=0.6,
        ),
        Hypothesis(
            why="CLOCK-TRANSFERS-INTACT: equilibration is fast relative to even real "
                "forcing, so the ~25yr lead and smooth approach hold approximately in "
                "the real world; the slow-forcing timeline is roughly portable.",
            would_break="if true, the dF/dt sweep should leave lead-time and pre-collapse "
                        "smoothness ~unchanged across rates",
            test="same sweep; null result (flat lead-time vs dF/dt) would support this",
            explains=0.3,
        ),
        Hypothesis(
            why="MARKER-WITHOUT-COLLAPSE: the abrupt northward jump is a response to "
                "weakening that can occur WITHOUT subsequent collapse, so it is not a "
                "reliable tripwire at all (Ben-Yami's alternative).",
            would_break="if true, ensembles should show jumps that are followed by AMOC "
                        "recovery, not just collapse",
            test="large ensemble under varied forcing; count jump-then-recover vs "
                 "jump-then-collapse trajectories",
            explains=0.35,
        ),
    ]

    print(wonder(p, hypotheses))

    print("\n" + "=" * 70)
    print("WHY THE TWO TOP HYPOTHESES ARE THE SAME EXPERIMENT")
    print("=" * 70)
    print("Forcing-rate-mismatch (0.60) and clock-transfers-intact (0.30) are")
    print("opposite predictions of ONE knob: dF/dt at matched cumulative forcing.")
    print("  lead-time shrinks + oscillation appears as dF/dt rises  -> mismatch")
    print("  lead-time + smoothness flat across dF/dt                -> clock portable")
    print("This is the falsifiable core. The published run fixed dF/dt low; nobody")
    print("swept it. The 25-34yr number is a single point on an un-swept axis.")
    print()
    print("OSCILLATION is the tell: a smooth-approach model cannot produce it.")
    print("If the rate sweep produces growing-amplitude ringing before collapse,")
    print("the slow-forcing timeline is confirmed as a FALSE FIT — right markers,")
    print("wrong clock — and collapse arrives off-schedule, likely early.")

    print("\n" + "-" * 70)
    for candidate in [
        "Let's build a better AMOC model that beats theirs on lead-time.",
        "Why does the timeline change with forcing rate, and where does oscillation enter?",
    ]:
        print(f"  output : {candidate}")
        print(f"  guard  : {hubris_check(candidate)}\n")


if __name__ == "__main__":
    main()
