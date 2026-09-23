# intersecting_projects/

**STATUS: FURTHER RESEARCH NEEDED.** Nothing in this folder is wired into the physics
stack, tested, or cited by any module. These are working documents from projects that
intersect this repo's audits. They are kept verbatim as supplied, because what they claim
now is the record, and every flag below is a place to do more research.

Source: `OKComputer_Thwaites_Glacier_2026_Review.zip` (2026-09-23/24), alongside the
Thwaites audit that became `../research.md`.

## Files

| file | subject | intersects |
|---|---|---|
| `warning_card_spec.md` | observable-indicator warning cards: must report miss rate AND false-alarm rate | `research.md` §12a/§12d; `risk_posture.py` |
| `worker_field_brief_design_life.md` | one-page brief: committed ice loss vs infrastructure design life | `research.md` §5, §12d; `thwaites_teis_2026.py` |
| `operations_redundancy_audit_template.md` | effective vs nominal redundancy for crews, fleets, farms | `research.md` §6 (observing-system redundancy) |
| `automation_gap_audit.md` | measured automation deployments vs vendor claims | `substrate_audit.py`, `thermodynamic_price_guard.py` |
| `demo_corpus_audit.md` | 16 automation demos through the harness; curated corpus, event-sampled | `research.md` §3 (event-sampled records) |
| `komatsu_ahs_input_scaffold.md` | FrontRunner AHS vs human haulage, input by input | `automation_gap_audit.md` |
| `field_layer_seed_roads.md` | road wear: human-run unpaved vs autonomy's infrastructure bill | `automation_gap_audit.md` |

## Known flags (found while filing; files not edited)

- **`worker_field_brief_design_life.md`:**
  - **Wrong author credited.** It attributes the 150-year committed-loss finding to "Bradley et al."; the paper is
    **Williams, C. R., et al. 2026**, GRL 53(14), doi:10.1029/2026GL122843 (Bradley is last
    author). See `../thwaites_teis_2026.py` `LITERATURE["williams_2026"]`.
  - **One number is unsourced.** It says "three numbers, all from published 2026 work", but the **75-year design life**
    carries no source.
  - **One claim leans on a narrow result.** Its "no referee instrument" paragraph rests on `research.md` §4's "no shared
    quantity", which §15b notes is a property of the audit's own measurement-fork spec.
- **Thwaites-derived files in general.** Any figure taken from Goldberg et al. is from a preprint, and
  "2.6 mm/yr by 2200" is unlocated (`research.md` §15a).
- **Automation files:** these carry their own MEASURED / VENDOR / FORECAST / CONSTRUCTED labels, but
  none of those sources has been checked from this repo yet.

## Before anything here moves into a module

1. Check every MEASURED number against its primary source, and grade it the way
   `thwaites_teis_2026.LITERATURE` does.
2. Resolve the flags above in a new version of the file. Keep the original beside it
   (the repo's retire-don't-delete rule).
3. Add tests for any number that becomes code.
