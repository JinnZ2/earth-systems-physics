# ai_reference/

Machine-readable exports of the repo's catalogs, plus cross-module
glossary and composition recipes. This folder exists so any downstream
AI tool — or any program — can ingest the repo's structured content
without having to execute Python or know the source module layout.

License: CC0, same as the rest of the repository.

## What's here

```
ai_reference/
├── README.md               (this file)
├── glossary.md             unified terminology across modules
├── composition_recipes.md  cross-module analysis patterns
├── index.json              table of contents + provenance + schemas
└── catalogs/               one .jsonl file per module-level catalog
    ├── mechanisms.jsonl
    ├── epigenetic_factors.jsonl
    ├── constraint_domains.jsonl
    ├── accountability_patterns.jsonl
    ├── example_chains.jsonl
    ├── cascade_scenarios.jsonl
    ├── feedback_loops.jsonl
    ├── layer_names.jsonl
    ├── assumption_boundaries.jsonl
    ├── overhead_layers.jsonl
    ├── climate_projects.jsonl
    └── finance_scenarios.jsonl
```

## What's NOT here

- Curated LLM fine-tuning datasets (no prompt/completion pairs).
- Model-specific framing or "how Claude should think about this."
- Duplicates of `CLAUDE.md`, module docstrings, or `AI_REFERENCE`
  dicts inside the source modules — those remain the source of truth
  for narrative content.
- Any content not derivable from a Python module in the repo. If you
  see something here that isn't reproducible by running the exporter,
  that's a bug — file it or fix it.

## How to read it

### Start with `index.json`

Every catalog is registered in `index.json` with:

- `path`           — relative path under `ai_reference/`
- `source_module`  — Python module the records came from
- `source_symbol`  — name of the dict / list inside that module
- `description`    — one-line plain-English summary
- `record_count`   — number of records in the catalog
- `schema`         — `{field_name: observed_type_name}` map for every
                     non-internal field, inferred from the records

Example consumption:

```python
import json
with open("ai_reference/index.json") as f:
    idx = json.load(f)
for name, meta in idx["catalogs"].items():
    print(name, meta["record_count"], list(meta["schema"].keys()))
```

### Then stream the catalogs

Each `.jsonl` file is one JSON object per line. Streamable, parser-
friendly, no special handling required.

```python
import json
with open("ai_reference/catalogs/mechanisms.jsonl") as f:
    for line in f:
        record = json.loads(line)
        print(record["name"], "—", record["description"])
```

Records always have a `name` field. For dicts that originally had a
string key, the key becomes `name`. For lists of dataclass instances,
`name` is whatever the dataclass already exposed under that name.

### `_excluded_keys` markers

Some source dicts (notably `cascade_engine.KNOWN_LOOPS`) contain
callable values like `lambda` triggers and gain functions. Callables
are not JSON-serializable, so the exporter drops them and records the
dropped key names under `_excluded_keys` on the surviving record. If
you see `_excluded_keys` on a record, you know that record has more
information available in the source module that you cannot get from
the catalog alone.

## Regeneration

Catalogs are NOT hand-edited. They are generated from the Python
sources by `tools/export_ai_catalogs.py`. Run from the repo root:

```bash
python tools/export_ai_catalogs.py              # regenerate in place
python tools/export_ai_catalogs.py --check      # report drift, exit 1 if drifted
python tools/export_ai_catalogs.py --verbose    # per-catalog status
```

The `--check` mode is the source of truth: if the exporter says the
catalogs match the current Python sources, the folder is fresh. CI
runs the same command.

To add a new catalog: edit the `CATALOGS` list at the top of
`tools/export_ai_catalogs.py`. Each entry needs `name`, `module`,
`symbol`, and `description`. The exporter handles dicts of dicts,
dicts of dataclasses, lists of dicts, and lists of dataclasses
generically; you should not need to write per-catalog code unless the
source module exposes something unusual.

## Glossary and composition recipes

`glossary.md` and `composition_recipes.md` are hand-written. They
cover content the catalogs cannot:

- **`glossary.md`** — unified terminology across modules. The same
  word ("layer", "cascade", "blindness", "delta", "buffer") means
  different specific things in different modules; the glossary keeps
  them straight.

- **`composition_recipes.md`** — how to chain modules together to do
  end-to-end analysis. None of the individual modules document this
  because it spans the whole framework.

Both are short, deliberately. They exist to bridge gaps the
auto-generated catalogs cannot bridge.

## Conventions for downstream consumers

- Treat `name` as the primary key within a catalog.
- Treat `description` (when present) as the canonical short summary.
- `_excluded_keys` is metadata, not data; ignore it unless you want
  to know what's missing.
- `index.json["catalogs"][name]["schema"]` is the authoritative field
  list; don't assume fields based on a sample record alone, because
  some catalogs have heterogeneous records (the schema field will
  read `"mixed"` in that case).
- The format is versioned via `index.json["format_version"]`. If you
  build tooling against a specific version, pin it.
