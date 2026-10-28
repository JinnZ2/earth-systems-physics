# test_estimate_direction_tally.py — earth-systems-physics — CC0
import corruption_chain as cc
import estimate_direction_tally as t


def test_counts_decided_only():
    r = t.tally()
    assert r["n_decided"] == 4
    assert r["counts"] == {t.UNDER: 2, t.OVER: 1, t.SIGN: 0, t.NO_ESTIMATE: 1}
    assert r["held_apart"][t.CONDITIONAL] == ["T5"]
    assert set(r["held_apart"][t.OPEN]) == {"T4", "T6"}


def test_no_rate_from_selected_frame():
    r = t.tally()
    assert r["rate_low"] is None and "outcome" in r["rate_low_reason"]


def test_tally_reachable_both_ways():
    over_world = [dict(e, direction=t.OVER, status=t.DECIDED) for e in t.MISSES]
    r = t.tally(over_world)
    assert r["counts"][t.OVER] == len(t.MISSES) and r["counts"][t.UNDER] == 0


def test_omissions_have_both_signs_and_unknowns():
    p = t.omission_push()
    assert p[t.UNDER] and p[t.OVER] and p["UNKNOWN"]
    assert p["grade"] == t.PROPOSED
    assert all(o["check"] for o in t.CANDIDATE_OMISSIONS)


def test_direction_codes_match_corruption_chain_convention():
    d = t.corruption_directions()
    assert d["T1"] == 1 and d["T3"] == -1 and d["T7"] == 0
    # feeds compose(): two same-direction layers compound
    layers = [cc.from_flag("YELLOW", direction=d["T1"]),
              cc.from_flag("YELLOW", direction=d["T2"])]
    assert "COMPOUNDING" in cc.compose(layers)[2]
    mixed = [cc.from_flag("YELLOW", direction=d["T1"]), cc.from_flag("YELLOW", direction=d["T3"])]
    assert "MIXED" in cc.compose(mixed)[2]


def test_every_entry_sourced_and_graded():
    for e in t.MISSES:
        assert e["source"] and e["grade"] in (t.CITED_ABSTRACT, t.CITED_PRESS, t.IN_REPO)
