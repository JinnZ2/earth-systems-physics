# meta_experiments.py
# climate_modeling
# CC0 — No Rights Reserved
#
# Level-2: experiments about experiments. Run the audit suite, and for every
# detected failure ask the AI proposer what structural repair would address it.
# This is the "AI as co-scientist" loop: not a parameter sweep, but reasoning
# about which modelling assumption failed and how to fix it.
#
# Note (honest scope): the loop reports the proposed repair rather than silently
# rewriting model source. Auto-applying a structural patch (adding a state
# variable, a threshold term, a coupling) is a code-generation problem, not a
# parameter tweak, and doing it invisibly would defeat the audit's purpose. The
# proposal is the deliverable; a human (or a downstream codegen step) applies it.

from .audits.audit_registry import all_audits
from .ai_interface import AIScientist


class MetaExperiment:
    def __init__(self, ai=None):
        self.ai = ai if ai is not None else AIScientist(backend="dummy")

    def run(self, verbose=False):
        """Run every audit; attach an AI-proposed repair to each failure.

        Returns a list of records: the audit result plus, when it failed, the
        proposer's suggested structural repair.
        """
        records = []
        for audit in all_audits():
            result = audit.run()
            record = {"result": result}
            if result["failure_detected"]:
                record["proposed_patch"] = self.ai.propose_patch(result)
            records.append(record)
            if verbose:
                status = "FAIL" if result["failure_detected"] else "pass"
                line = f"[{status}] {result['audit_name']}"
                if result["failure_detected"]:
                    line += f"  -> {record['proposed_patch']['suggestion']}"
                print(line)
        return records

    @staticmethod
    def report_card(records):
        """Summarise a meta-experiment run: counts + the failure->repair map."""
        failures = [r for r in records if r["result"]["failure_detected"]]
        return {
            "n_audits": len(records),
            "n_failures": len(failures),
            "repairs": {r["result"]["audit_name"]: r["proposed_patch"]["suggestion"]
                        for r in failures},
        }


if __name__ == "__main__":
    meta = MetaExperiment()
    recs = meta.run(verbose=True)
    card = MetaExperiment.report_card(recs)
    print(f"\n{card['n_failures']}/{card['n_audits']} audits failed; "
          f"each has a proposed structural repair.")
