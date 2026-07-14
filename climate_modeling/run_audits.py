#!/usr/bin/env python3
# run_audits.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Run the whole audit suite and print a failure report card. Each audit is a
# controlled experiment: FAIL means the simplified model diverged dangerously
# from the known true system.
#
#   python -m climate_modeling.run_audits

import json
import time

from .audits.audit_registry import all_audits


def run_all(verbose=True):
    results = []
    for audit in all_audits():
        t0 = time.time()
        res = audit.run()
        res["_seconds"] = round(time.time() - t0, 3)
        results.append(res)
        if verbose:
            status = "FAIL" if res["failure_detected"] else "pass"
            print(f"[{status}] {res['audit_name']:<32} ({res['_seconds']}s)")
    n_fail = sum(r["failure_detected"] for r in results)
    if verbose:
        print(f"\n{n_fail}/{len(results)} audits detected a modelling failure.")
    return results


if __name__ == "__main__":
    out = run_all()
    with open("audit_report.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nReport written to audit_report.json")
