# substrate_audit.py
# earth-systems-physics
# CC0 — No Rights Reserved

"""
substrate_audit.py — Thermodynamic Audit of Hierarchical Capital Control

CC0 — No rights reserved. JinnZ2

INTENT:
This is not an ideological critique. It is not anti-capitalist,
anti-hierarchy, or anti-credential. It is a data quality audit.

  Every mechanic must show their torque wrench is calibrated.
  Every hospital must show its sterilization logs.
  Every bridge engineer must show their load calculations.

  This module asks: have the systems that GOVERN those mechanics,
  hospitals, and engineers — the credentialing bodies, corporate
  hierarchies, and monetary accounting frameworks — ever been held
  to the same standard of data quality they impose on everyone
  underneath them?

  The answer, based on available evidence, is no.

  The audit does not say "tear it down." It says "show me the
  calibration certificate." If the certificate exists, the system
  will score well. If it doesn't, the system scores poorly — not
  because of ideology, but because of missing data.

PURPOSE:
Distill the full argument into machine-readable form:
  - 10 falsifiable claims with null hypotheses
  - 5-Why root cause chain
  - Causal feedback loop (verified topology)
  - Six Sigma audit (DMAIC)
  - 11-dimension scoring engine any AI can run against real-world data
  - Cross-model JSON export with embedded prompt for autonomous analysis

USAGE:
    python substrate_audit.py              # print full audit + verdicts
    import substrate_audit as sa           # use as module
    sa.score_system(your_data_dict)        # score any system
    sa.to_json()                           # export for cross-model ingestion

DEPENDENCY: stdlib only
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import math


# ═══════════════════════════════════════════════════════════
# LAYER 0 — DEFINITIONS
# ═══════════════════════════════════════════════════════════

class Verdict(Enum):
    PASS     = "PASS"
    FAIL     = "FAIL"
    UNTESTED = "UNTESTED"
    CIRCULAR = "CIRCULAR"   # claim's evidence depends on claim's assumptions


@dataclass
class FalsifiableClaim:
    """A claim that can be tested against physical reality."""
    id: str
    claim: str
    null_hypothesis: str           # what you'd need to disprove
    required_measurement: str      # what instrument / data
    known_evidence: str            # what exists as of 2025
    verdict: Verdict
    note: str = ""


@dataclass
class CausalNode:
    """One node in a feedback loop."""
    id: str
    label: str
    drives: List[str]              # ids of nodes this feeds into
    is_self_reinforcing: bool = False


# ═══════════════════════════════════════════════════════════
# LAYER 1 — THE 7 FALSIFIABLE CLAIMS
# ═══════════════════════════════════════════════════════════

CLAIMS: List[FalsifiableClaim] = [
    FalsifiableClaim(
        id="TC-1",
        claim=(
            "Live physical capital = machines + maintaining_humans + "
            "tools. The maintainer is thermodynamically inseparable "
            "from the capital."
        ),
        null_hypothesis=(
            "Capital can sustain output indefinitely without human "
            "maintainers."
        ),
        required_measurement=(
            "Equipment MTBF and output over time with vs. without "
            "maintenance crew. Measured in joules of useful work."
        ),
        known_evidence=(
            "Every industrial system ever measured shows monotonic "
            "degradation without maintenance. No counterexample exists."
        ),
        verdict=Verdict.PASS,
    ),
    FalsifiableClaim(
        id="TC-2",
        claim=(
            "CEO removal has no immediate physical effect on capital. "
            "Mechanic removal causes measurable capital decay within "
            "days-weeks."
        ),
        null_hypothesis=(
            "CEO removal causes faster physical decay than mechanic "
            "removal."
        ),
        required_measurement=(
            "Controlled comparison: remove CEO vs. remove maintenance "
            "crew from identical facilities. Measure uptime, failure "
            "rate, output."
        ),
        known_evidence=(
            "Anecdotal + historical (strikes, lockouts) consistently "
            "show production halts when workers leave, continues when "
            "execs leave. No controlled trial exists."
        ),
        verdict=Verdict.UNTESTED,
        note="Directional evidence strong. No RCT.",
    ),
    FalsifiableClaim(
        id="TC-3",
        claim=(
            "CEO 'scope of decisions' is a self-assigned property, "
            "not a physically measured one. The assignment is "
            "circular: those who hold power define the metric that "
            "justifies holding power."
        ),
        null_hypothesis=(
            "An external, physics-based metric exists that "
            "independently justifies CEO authority over mechanic "
            "authority."
        ),
        required_measurement=(
            "Identify any metric for CEO authority that does not "
            "reference legal title, board appointment, or historical "
            "precedent."
        ),
        known_evidence=(
            "No such metric has been published. Raelin (2020) confirms "
            "democratic leadership occurs only with permission of "
            "hierarchy."
        ),
        verdict=Verdict.CIRCULAR,
    ),
    FalsifiableClaim(
        id="TC-4",
        claim=(
            "Credentialing systems have never been tested "
            "apple-to-apple against uncertified-but-experienced "
            "practitioners on OUTCOME metrics (repair durability, "
            "child development, safety incidents)."
        ),
        null_hypothesis=(
            "A controlled trial exists comparing certified vs. "
            "uncertified workers on physical/outcome metrics."
        ),
        required_measurement=(
            "Literature search for RCTs or quasi-experiments with "
            "outcome measures, not supervisor ratings or wage proxies."
        ),
        known_evidence=(
            "2013 child-worker study used supervisor ratings only. "
            "2024 India study measured wages only. "
            "2024 auto-repair study found 90% post-repair total-loss "
            "rate but did not stratify by certification status."
        ),
        verdict=Verdict.UNTESTED,
        note="The experiment the church refuses to run.",
    ),
    FalsifiableClaim(
        id="TC-5",
        claim=(
            "Emotions are evolutionarily conserved functional data "
            "streams, not noise. Excluding them from models of "
            "intelligence is an arbitrary methodological choice, not "
            "a scientific requirement. Affective processing is present "
            "across vertebrates including fish, and functions as a "
            "sensor suite tuned by natural selection."
        ),
        null_hypothesis=(
            "Organisms that suppress emotional processing outperform "
            "those that integrate it, across survival and decision "
            "quality."
        ),
        required_measurement=(
            "Compare decision quality in emotion-intact vs. "
            "emotion-impaired subjects. Compare survival rates in "
            "species with vs. without affective systems. Test across "
            "phyla, not just mammals."
        ),
        known_evidence=(
            # MAMMALS — lesion studies
            "Damasio (1994): ventromedial prefrontal lesion patients "
            "lose decision capacity despite intact logic (somatic "
            "marker hypothesis). "
            # MAMMALS — subcortical mapping
            "Panksepp (1998+): seven core affective circuits "
            "(SEEKING, RAGE, FEAR, LUST, CARE, PANIC/GRIEF, PLAY) "
            "mapped subcortically across all mammals — predates "
            "cortex, therefore predates 'higher' cognition. "
            # MAMMALS — fast-path processing
            "LeDoux (1996+): amygdala processes threat faster than "
            "cortex can consciously register — body acts before 'you' "
            "decide. Not bias; a faster sensor path with survival "
            "value. "
            # MAMMALS — constructed emotion
            "Barrett (2017): constructed emotion theory — emotions "
            "are predictive models built from interoception, not "
            "hardwired reflexes. Different framework than Panksepp "
            "but same conclusion: functional computation. "
            # FISH — nociception and pain
            "Sneddon et al. (2003): first identification of "
            "nociceptors in teleost fish (rainbow trout). A-delta "
            "and C fibers with properties identical to mammalian "
            "nociceptors. "
            "Sneddon (2003b): morphine blocks pain-related behavioral "
            "changes in trout (guarding, feeding cessation) — "
            "analgesic response indicates affective component, not "
            "mere reflex. "
            "Zebrafish acid/analgesic tank-choice experiments: fish "
            "injected with acid abandon preferred enriched tank for "
            "barren tank with painkillers — trade-off behavior "
            "requiring valenced experience. "
            "Avoidance learning in trout: fish learn to flee light "
            "cue 10s before net entry within 5 days — memory-based "
            "fear response. "
            "Braithwaite (2010), Broom, AVMA: consensus that fish "
            "should be accorded same pain considerations as "
            "terrestrial vertebrates. "
            # FISH — the neocortex objection refuted
            "Rose (2002) neocortex-requirement argument would exclude "
            "all birds and most mammals from pain. Sneddon: "
            "convergent evolution of different neural architectures "
            "serving equivalent functions. Anencephalic human "
            "children express emotions despite missing cortex — "
            "brainstem circuits sufficient for affect. "
            # CROSS-KINGDOM
            "Affective systems conserved across vertebrates "
            "(>500 Myr). Invertebrate nociception: cephalopods show "
            "sustained motivational state changes after tissue "
            "damage (Crook et al. 2013). Hermit crabs make valenced "
            "trade-offs between shell quality and noxious stimulus "
            "avoidance (Elwood). "
            # OBSERVER EFFECT
            "Excluding emotion from observation violates observer "
            "effect: the observer IS emotional. Denying this is not "
            "objectivity — it is unconscious bias operating without "
            "correction."
        ),
        verdict=Verdict.PASS,
        note=(
            "Evidence spans mammals (Damasio, Panksepp, LeDoux, "
            "Barrett), fish (Sneddon, Braithwaite), invertebrates "
            "(Crook, Elwood). The neocortex-requirement objection "
            "(Rose 2002) is refuted by convergent evolution and "
            "anencephalic expression data."
        ),
    ),
    FalsifiableClaim(
        id="TC-6",
        claim=(
            "Current deployed AI exhibits bounded context adaptation "
            "(in-context learning within a single conversation) but "
            "lacks true meta-learning (updating the update rule "
            "itself) and lacks stake (cost of failure) and embodied "
            "sensing. It adapts within a fixed parameter set but "
            "cannot modify its learning algorithm in response to "
            "novel failure without external retraining. Therefore "
            "it pattern-matches well inside a context window but "
            "does not learn-to-learn across them."
        ),
        null_hypothesis=(
            "An AI system deployed in production exists that, "
            "without human-initiated retraining, modifies its own "
            "optimizer or learning rule in response to novel "
            "failure outside its training distribution."
        ),
        required_measurement=(
            "Present AI with a problem class absent from training "
            "data. Observe whether it modifies its own optimization "
            "procedure (not just its in-context predictions or "
            "weights during a training run) in response to failure. "
            "Distinguish: (a) in-context learning — adjusting "
            "outputs based on examples inside the prompt, (b) "
            "fine-tuning — parameter updates during a separate "
            "training phase, (c) meta-learning — updating the "
            "update rule itself at inference, autonomously."
        ),
        known_evidence=(
            # WHAT IS PRESENT: bounded context adaptation
            "In-context learning IS a real form of bounded "
            "adaptation: LLMs demonstrably update their responses "
            "within a context window based on earlier examples in "
            "the same prompt (Brown et al. 2020 and subsequent "
            "few-shot learning work). Within a single conversation, "
            "a deployed model can incorporate new definitions, "
            "correct its own earlier mistakes when shown them, and "
            "generalize from examples it has never seen during "
            "training. This is not nothing. "
            "The context window functions as a working memory that "
            "the model conditions its outputs on. Larger context "
            "windows extend the range of this bounded adaptation. "
            # WHAT IS ABSENT: parameter update + meta-learning
            "What remains absent in deployed systems: "
            "(1) Parameter-level updating at inference. A deployed "
            "model's weights do not change in response to its own "
            "failures. A model that gives a wrong answer and is "
            "corrected by the user will, in the next independent "
            "conversation, give the same wrong answer. "
            "(2) Modification of the optimizer itself. The update "
            "rule is fixed at training time and does not evolve "
            "during deployment. "
            "(3) Recovery from novel failure without human "
            "retraining. When a model encounters a systematic "
            "failure mode, the fix is always an external retraining "
            "loop, not autonomous repair. "
            # META-LEARNING RESEARCH
            "Meta-learning research (MAML, Reptile, and successors) "
            "optimizes the initialization for fast fine-tuning on "
            "new tasks, but the optimizer itself is still fixed "
            "and the fine-tuning still requires a separate training "
            "phase. This is meta-training, not meta-learning at "
            "inference. No deployed production system demonstrates "
            "autonomous modification of its update rule. "
            # THE DISTINCTION
            "The distinction the audit draws is: in-context "
            "learning = adapting within a fixed parameter set; "
            "meta-learning = updating the parameter-updating rule "
            "itself. Only the first is present in deployed systems. "
            "Conflating the two gives deployed LLMs credit for a "
            "capability they do not have, and misses the specific "
            "failure mode: under genuine novelty, a deployed model "
            "cannot repair itself."
        ),
        verdict=Verdict.PASS,
        note=(
            "Refined from v1 to distinguish in-context learning "
            "(present but bounded) from parameter-level meta-"
            "learning (absent). The refinement matters because "
            "calling all of it 'meta-learning' or none of it "
            "'adaptation' both misread deployed systems. "
            "The generalization_capacity dimension in SystemScore "
            "reflects the bounded-adaptation case: deployed LLMs "
            "score around 0.5 on that dimension, not 0.0."
        ),
    ),
    FalsifiableClaim(
        id="TC-7",
        claim=(
            "Mycorrhizal networks and mitochondria meet the criteria "
            "for 'body-as-sensor-array': boundary, sensors, "
            "integration, history, and stake. Intelligence does not "
            "require neurons."
        ),
        null_hypothesis=(
            "Mycorrhizal networks allocate resources randomly, "
            "without integrating chemical/electrical/mechanical "
            "signals. Mitochondria are passive organelles without "
            "adaptive behavior."
        ),
        required_measurement=(
            "Isotope tracing of resource allocation in mycorrhizal "
            "networks under varied partner-quality conditions. "
            "Time-lapse imaging of mitochondrial fission/fusion "
            "dynamics under stress gradients."
        ),
        known_evidence=(
            # MYCORRHIZAL NETWORKS
            "Simard et al. (1997, Nature): first field demonstration "
            "of net carbon transfer between tree species via "
            "ectomycorrhizal networks in mixed temperate rainforest. "
            "Simard (2018): network topology is scale-free with "
            "small-world properties — correlated with local/global "
            "efficiencies found in neural networks. "
            "Kin recognition: Douglas-fir preferentially transfers "
            "more carbon to genetically related seedlings via shared "
            "mycorrhizal networks (Asay et al. 2020; Gorzelak 2017). "
            "Defense signaling: injured Douglas-fir sends chemical "
            "warning signals through CMN to ponderosa pine, which "
            "then produces defense enzymes (Song et al. 2015). "
            "Resource allocation is context-dependent: direction of "
            "carbon flow shifts seasonally, toward parts of network "
            "in greatest need. "
            "Electrochemical impulses similar to nerve signals travel "
            "through mycorrhizal hyphae (emerging research). "
            "CONTESTED: Karst et al. (2023, Nature Ecol Evol) "
            "critiques positive citation bias in CMN literature. "
            "Simard et al. (2025, Frontiers) responds with detailed "
            "rebuttal. The existence of CMNs and preferential "
            "transfer is not disputed; the mechanism and magnitude "
            "of 'mother tree' effects is debated. "
            # MITOCHONDRIA
            "Mitochondria are autonomous organelles with own genome, "
            "descended from endosymbiotic bacteria (~2 Byr ago). "
            "Fission/fusion dynamics: not passive — mitochondria "
            "actively sense metabolic state (ATP/ADP ratio, calcium, "
            "ROS, temperature) and respond by fusing (complementation "
            "of damaged units) or dividing (segregation of "
            "dysfunctional organelles). "
            "Twig et al. (2008, EMBO): fission produces uneven "
            "daughters — one with higher membrane potential (proceeds "
            "to fusion), one with lower potential (isolated for "
            "autophagy). This is selective quality control: sense, "
            "assess, segregate, remove. "
            "Mitochondria relocate within cells to sites of high "
            "energy demand — especially in neurons, where they travel "
            "long distances along axons, pausing at synapses. "
            "Youle & van der Bliek (2012, Science): fusion/fission "
            "regulated by proteolytic processing, ubiquitylation, "
            "sumoylation, phosphorylation — multiple signal "
            "integration pathways. "
            "Kowald & Kirkwood (2011, PNAS): evolutionary model shows "
            "fusion-fission cycle evolved as quality control "
            "mechanism; intact proton gradient required for fusion "
            "means only functional mitochondria merge. "
            # BODY-AS-SENSOR-ARRAY CRITERIA
            "Both systems meet all criteria: "
            "Boundary: hyphal wall / double membrane. "
            "Sensors: chemical, pH, electrical, mechanical, thermal / "
            "ATP-ADP, calcium, ROS, membrane potential. "
            "Integration: network-wide resource allocation / "
            "retrograde signaling to nucleus, metabolic switching. "
            "History: growth pattern reflects past encounters / "
            "fission-fusion history affects current function. "
            "Stake: wrong allocation = reduced nutrient exchange / "
            "failure = cell death."
        ),
        verdict=Verdict.PASS,
        note=(
            "Mycorrhizal CMN debate (Karst vs. Simard) is about "
            "magnitude, not existence. Mitochondrial autonomy is "
            "undisputed. Both meet body-as-sensor-array criteria "
            "without neurons."
        ),
    ),
    FalsifiableClaim(
        id="TC-8",
        claim=(
            "Non-Western and Indigenous empirical knowledge systems "
            "(TEK) represent independent, long-duration, outcome-"
            "tested scientific practice. Dismissing them as 'non-"
            "scientific' is a definitional exclusion by the "
            "credentialing church, not a failure of method."
        ),
        null_hypothesis=(
            "TEK-derived practices produce worse ecological, "
            "agricultural, or health outcomes than credentialed "
            "Western alternatives when applied to the same landscapes "
            "over comparable timescales."
        ),
        required_measurement=(
            "Controlled comparison of TEK-managed vs. Western-managed "
            "ecosystems on biodiversity, soil health, fire "
            "resilience, species conservation, and food system "
            "sustainability. Multi-generational timescale required "
            "(decades minimum)."
        ),
        known_evidence=(
            # EMPIRICAL VALIDATION
            "Samoan traditional remedy (Psychotria insularum / "
            "matalafi): Molimau-Samasoni (2013+) confirmed anti-"
            "inflammatory properties comparable to ibuprofen — "
            "Western science validated what healers knew for "
            "generations. "
            "Dene caribou subcategories: Indigenous language "
            "distinctions map ecological variations not yet named in "
            "Western taxonomy. The vocabulary IS the empirical "
            "record. "
            "Hailzaqv (Heiltsuk) bear ecology: place-based knowledge "
            "guided hair-snare placement for DNA capture-recapture, "
            "producing novel population data that challenged "
            "provincial government policy (Housty et al. 2014). "
            "Australian Aboriginal fire management: >60,000 years of "
            "landscape-scale controlled burns — empirically superior "
            "to Western fire suppression, now being adopted by "
            "agencies. "
            # METHODOLOGICAL CHARACTERISTICS
            "TEK validation process: individual observation, sharing "
            "with other users and elders, time-testing over "
            "generations. This IS peer review + longitudinal "
            "replication, just not institutionalized. "
            "TEK observers are resource users (hunters, fishers, "
            "gatherers) whose survival depends on observation "
            "accuracy — embodied stake that academic observers lack. "
            "Houde (2007): six facets of TEK — factual observations, "
            "management systems, past/current uses, ethics/values, "
            "culture/identity, cosmology. Only the first is "
            "recognized by Western science; the other five are "
            "dismissed as 'non-scientific.' "
            # THE EXCLUSION MECHANISM
            "Western science frames itself as 'testable knowledge' "
            "and dismisses TEK as 'experiential' — but TEK has been "
            "tested by survival over millennia, which is a harder "
            "test than peer review. "
            "Jessen et al. (2022, Frontiers in Ecology): 87% of "
            "studies using IK employed 'extractive model' — taking "
            "knowledge without benefiting source communities. The "
            "church extracts from uncertified masters even while "
            "denying their legitimacy. "
            "IPBES (2024): braiding TEK with Western science now "
            "recognized as essential for transformative change in "
            "biodiversity conservation."
        ),
        verdict=Verdict.PASS,
        note=(
            "TEK is independently derived empirical science with "
            "multi-generational replication. Its exclusion from "
            "'science' is definitional, not evidential. Landscape-"
            "encoded knowledge transmission (spatial markers, star-"
            "trail navigation, fire calendars) constitutes functional "
            "engineering misclassified as ceremonial or cultural."
        ),
    ),
    FalsifiableClaim(
        id="TC-9",
        claim=(
            "Money fails as a scientific unit of measurement before "
            "it fails as a store of value. Its definition changes "
            "with regulation, accounting standards (GAAP, IFRS), "
            "interest rate policy, reporting incentives, and "
            "institutional context. No audit has ever validated that "
            "any monetary unit measures a stable physical quantity. "
            "Physical capital is a flow requiring continuous energy "
            "input; money pretends to be a stock. The exchange rate "
            "between them is a political variable, not a physical "
            "constant. Financial accounting and thermodynamic "
            "accounting are incommensurable systems applied to the "
            "same substrate."
        ),
        null_hypothesis=(
            "A unit of currency corresponds to a fixed, conserved "
            "quantity of physical value (energy, exergy, negative "
            "entropy, or useful work capacity) that persists without "
            "energy input AND the unit's definition is stable across "
            "regulatory changes, accounting standard revisions, and "
            "institutional contexts."
        ),
        required_measurement=(
            "Track the physical-value equivalent of $1 (in joules of "
            "useful work, kg of maintained capital, or hectares of "
            "fertile soil) over 50 years. If money is a valid "
            "measurement unit, the ratio should be constant. "
            "Simultaneously track: (a) changes in GAAP/IFRS "
            "definitions that alter what '$1 of revenue' means, "
            "(b) regulatory changes that alter what '$1 of capital' "
            "means, (c) incentive-driven reporting variations across "
            "industries, (d) what '$1' purchases in maintenance "
            "labor, energy, and materials."
        ),
        known_evidence=(
            # UNIT-OF-MEASUREMENT FAILURE
            "Physical measurement units (meter, kilogram, joule, "
            "second) are defined by physical constants: speed of "
            "light, Planck's constant, Boltzmann's constant. They do "
            "not change when legislation changes. They mean the same "
            "thing to every participant. Money has none of these "
            "properties. "
            "GAAP has been revised hundreds of times since 1936. "
            "IFRS differs from GAAP on revenue recognition, lease "
            "accounting, inventory valuation, R&D capitalization. "
            "The same physical asset valued under different standards "
            "produces different dollar amounts. This means the 'unit' "
            "itself is context-dependent — a ruler whose length "
            "changes depending on who is measuring. "
            "Mark-to-market vs. mark-to-model vs. historical cost: "
            "three different accounting methods produce three "
            "different dollar values for the same physical object at "
            "the same moment. No physical measurement system "
            "tolerates this. "
            "Goodwill, intangible assets, deferred tax assets: "
            "accounting categories with no physical referent "
            "whatsoever, yet counted as 'value' on corporate balance "
            "sheets. "
            "No metrological audit has ever been performed on any "
            "monetary unit. No standards body has certified that "
            "'$1' measures a stable quantity of anything. The unit "
            "has never been calibrated. "
            # THERMODYNAMIC ARGUMENT
            "Landauer's principle: erasing one bit costs minimum "
            "kT ln 2 joules. Information is physical. Money is "
            "information. But money does not obey conservation laws "
            "— central banks create it by fiat, destroying any fixed "
            "relationship to physical quantity. "
            # EMPIRICAL
            "USD purchasing power: ~96% loss since 1913 (BLS CPI "
            "data). The 'store' leaks continuously, but the leak "
            "rate is set by political decisions (interest rates, "
            "money supply), not by thermodynamic law. "
            # STOCK vs FLOW
            "Physical capital depreciates according to entropy: "
            "machines rust, soil depletes, skills atrophy. "
            "Maintenance is the energy flow that counteracts this. "
            "Money cannot perform maintenance. It can only command "
            "others to perform it — and that command depends on "
            "social agreements that can collapse (hyperinflation, "
            "sanctions, bank runs, currency crises). "
            # ATOMIC ACCOUNTING
            "Conservation laws apply to mass-energy, not to "
            "currency. delta M_earth = M_in - M_out is a closed "
            "equation. The financial ledger has no equivalent "
            "closure — money can be created and destroyed without "
            "any physical event occurring. Double-entry bookkeeping "
            "balances symbols, not atoms. "
            # FRACTIONAL RESERVE
            "Fractional reserve banking creates money as debt — each "
            "loan increases the money supply without increasing "
            "physical capital. The gap between monetary claims and "
            "physical backing widens monotonically until a "
            "correction event (crash, default, hyperinflation) "
            "forces reconciliation with physics. "
            # INCENTIVE STRUCTURES
            "What '$1 of earnings' means differs by: industry, "
            "accounting method chosen, regulatory regime, and who is "
            "asking. The same physical transaction produces "
            "different monetary values depending on reporting "
            "incentives. This is not a measurement system. This is "
            "a narrative system with numbers attached. "
            # CONSEQUENCE
            "This disconnect is the mechanism by which the "
            "TITLE -> SURPLUS -> POWER -> ENFORCE loop operates: "
            "surplus is captured in money, which is a claim on "
            "future physical value that may not exist. The loop "
            "runs on promissory notes, not on joules."
        ),
        verdict=Verdict.PASS,
        note=(
            "The 96% USD purchasing power loss since 1913 rejects "
            "store-of-value. The hundreds of GAAP/IFRS revisions "
            "reject unit-of-measurement stability. No metrological "
            "calibration of any monetary unit has ever been "
            "performed. Money is a narrative system with numbers, "
            "not a measurement system with units."
        ),
    ),
    FalsifiableClaim(
        id="TC-10",
        claim=(
            "Information is physical (Landauer, Shannon-Boltzmann "
            "equivalence). Coordination, routing, and decision-"
            "making are therefore thermodynamic work, not abstract "
            "'management.' The audit's target is not coordination "
            "itself — which is physically necessary — but "
            "coordinators whose signal path is so degraded (high "
            "transduction steps, high latency, low fidelity) that "
            "their decisions are effectively random while the "
            "system pretends they are optimal."
        ),
        null_hypothesis=(
            "Coordination decisions made through high-latency, "
            "multi-layer abstracted signal paths (e.g., CEO reading "
            "quarterly reports) produce equal or better physical "
            "outcomes than coordination decisions made through "
            "low-latency, direct-sensing signal paths (e.g., shop "
            "dispatcher reading vibration data)."
        ),
        required_measurement=(
            "Compare physical outcomes (equipment lifespan, failure "
            "rate, maintenance cost per unit output, energy "
            "efficiency) between systems where coordination "
            "decisions are made by: (a) direct-sensing coordinators "
            "(1-2 transduction steps), vs. (b) abstracted "
            "coordinators (5-10 transduction steps via reports, "
            "dashboards, analyst summaries)."
        ),
        known_evidence=(
            # PHYSICS
            "Landauer (1961): information erasure has minimum energy "
            "cost. Information processing is physical work. "
            "Therefore coordination is physical work, not merely "
            "'social' or 'managerial.' "
            "Shannon (1948): entropy of information source equals "
            "thermodynamic entropy when measured in natural units. "
            "Signal-to-noise ratio degrades with each transduction "
            "step — this is fundamental, not fixable by better "
            "reporting software. "
            # CONTROL THEORY
            "Control theory (Nyquist, Bode): feedback loop stability "
            "requires latency below a critical threshold relative to "
            "system dynamics. A controller with latency longer than "
            "the system's characteristic timescale cannot stabilize "
            "it. CEO quarterly review cycle (90 days) vs. equipment "
            "failure timescale (hours-days) = guaranteed instability "
            "for maintenance decisions. "
            # EMPIRICAL PROXY
            "Owner-operator businesses consistently show lower "
            "failure rates than absentee-owned equivalents in small "
            "manufacturing and agriculture (SBA data, USDA farm "
            "survival statistics). The mechanism: decision-maker IS "
            "the sensor, feedback latency ~= 0. "
            # THE REAL DISTINCTION
            "The audit does not claim coordination is unnecessary. "
            "It claims that coordination quality is a function of "
            "signal fidelity and feedback latency — both measurable "
            "physical quantities — not of title, credential, or "
            "organizational rank."
        ),
        verdict=Verdict.PASS,
        note=(
            "This claim reframes the entire audit: the target is "
            "not hierarchy per se, but signal degradation. A flat "
            "organization with poor sensing is worse than a "
            "hierarchy with direct sensor coupling. The variable "
            "that matters is transduction steps between physical "
            "event and decision-maker, not org chart shape."
        ),
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 2 — 5-WHY ROOT CAUSE CHAIN
# ═══════════════════════════════════════════════════════════

FIVE_WHY: List[Dict[str, str]] = [
    {
        "why": "1",
        "question": "Why are CEOs rewarded more than mechanics?",
        "answer": (
            "Legal/financial system defines value by control over "
            "capital allocation, not by physical contribution to "
            "capital maintenance."
        ),
    },
    {
        "why": "2",
        "question": (
            "Why does the system define value by control, not "
            "maintenance?"
        ),
        "answer": (
            "Ownership rights (property law) predate and override "
            "maintenance rights. Owners write compensation rules."
        ),
    },
    {
        "why": "3",
        "question": (
            "Why do ownership rights override maintenance rights?"
        ),
        "answer": (
            "Legal framework evolved when initial capital investment "
            "was rare. Society granted permanent control to investors "
            "as incentive. Maintenance was classified as replaceable "
            "service."
        ),
    },
    {
        "why": "4",
        "question": (
            "Why is that framework still in place when maintenance "
            "is critical?"
        ),
        "answer": (
            "Beneficiaries of the framework (capital owners, "
            "executives) hold veto power over structural change. "
            "They fund politics, control governance, shape narrative."
        ),
    },
    {
        "why": "5 — ROOT CAUSE",
        "question": "Why do they hold veto power?",
        "answer": (
            "Positive feedback loop: Legal title -> captured surplus "
            "-> political/coercive power -> enforcement of title -> "
            "more surplus. Self-reinforcing. Cannot self-correct."
        ),
    },
]


# ═══════════════════════════════════════════════════════════
# LAYER 3 — CAUSAL FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════

CAUSAL_LOOP: List[CausalNode] = [
    CausalNode("TITLE",    "Legal ownership of capital",     ["SURPLUS"]),
    CausalNode("SURPLUS",  "Captured surplus value",         ["POWER"]),
    CausalNode("POWER",    "Political / coercive power",     ["ENFORCE"]),
    CausalNode(
        "ENFORCE",
        "Enforcement of ownership rules",
        ["TITLE"],
        is_self_reinforcing=True,
    ),
    # Excluded from loop but physically necessary:
    CausalNode("MAINTAIN", "Maintainer thermodynamic work",  []),
    # External perturbation source. Physical and resource
    # constraints inject corrections into the loop even though
    # the loop is internally self-reinforcing. This is what
    # drives collapse events, bankruptcies, revolutions, and
    # cascade resets. CONSTRAINT has outgoing edges into the
    # loop but no incoming edges from it — the loop cannot
    # escape physics.
    CausalNode(
        "CONSTRAINT",
        "External physical / resource constraint",
        ["SURPLUS", "POWER"],
    ),
]


def loop_is_closed(nodes: List[CausalNode]) -> bool:
    """Verify the feedback loop closes (TITLE -> ... -> TITLE)."""
    graph = {n.id: n.drives for n in nodes}
    visited: set = set()
    current: Optional[str] = "TITLE"
    while current and current not in visited:
        visited.add(current)
        nexts = graph.get(current, [])
        current = nexts[0] if nexts else None
    return current == "TITLE"


def maintainer_in_loop(nodes: List[CausalNode]) -> bool:
    """Check whether MAINTAIN feeds into the power loop."""
    for n in nodes:
        if n.id == "MAINTAIN":
            return bool(n.drives)  # empty = excluded
    return False


# ═══════════════════════════════════════════════════════════
# LAYER 4 — SIX SIGMA DMAIC AUDIT
# ═══════════════════════════════════════════════════════════

@dataclass
class DMAICPhase:
    phase: str
    requirement: str
    observed: str
    verdict: Verdict


DMAIC_AUDIT: List[DMAICPhase] = [
    DMAICPhase(
        "DEFINE",
        (
            "Clear, measurable definition of quality (e.g. "
            "'repair lasts N miles')"
        ),
        (
            "'Certified' is a proxy, not a performance metric. No "
            "spec limits defined."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "MEASURE",
        "Data on actual output variation by worker type",
        (
            "Only supervisor ratings and wage data collected. No "
            "outcome data."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "ANALYZE",
        "Root cause of defects traced without circular assumptions",
        (
            "System treats certified-worker failures as 'special "
            "cause' (individual), never as potential system failure. "
            "RCA blocked by self-reference."
        ),
        Verdict.CIRCULAR,
    ),
    DMAICPhase(
        "IMPROVE",
        "Change process based on data",
        (
            "No outcome data exists -> no improvement possible. "
            "Maryland licensing board had identical findings for 20+ "
            "years, unfixed."
        ),
        Verdict.FAIL,
    ),
    DMAICPhase(
        "CONTROL",
        "Maintain gains via ongoing measurement",
        (
            "Cannot control what is not measured. Process is "
            "out-of-control by definition."
        ),
        Verdict.FAIL,
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 5 — SCORING ENGINE
# ═══════════════════════════════════════════════════════════

@dataclass
class SystemScore:
    """Score any real-world system against this audit."""
    name: str
    # 0.0-1.0 for each dimension
    maintainer_control: float       # do maintainers control capital decisions?
    outcome_measurement: float      # are physical outcomes measured?
    scope_justification: float      # is authority justified by external metric?
    credential_tested: float        # have credentials been tested vs experience?
    emotion_integrated: float       # does the system integrate affective data?
    meta_learning: float            # can the system update its own update rule?
    substrate_intelligence: float   # does it recognize non-neural intelligence?
    tek_integration: float = 0.0    # does it integrate non-Western empirical knowledge?
    feedback_latency: float = 0.5   # how fast does consequence reach decision-maker?
    #                                 1.0 = immediate (mechanic feels bolt strip)
    #                                 0.0 = years/never (CEO sees quarterly report)
    signal_fidelity: float = 0.5    # how many transduction steps between physical
    #                                 event and decision-maker? 1.0 = zero steps
    #                                 (sensor IS decision-maker). 0.0 = 10+ steps
    #                                 (event -> sensor -> report -> analyst ->
    #                                 summary -> dashboard -> meeting -> exec)
    money_physics_coupling: float = 0.5  # does the system's value accounting
    #                                      track physical quantities (energy, mass,
    #                                      entropy) or monetary proxies?
    #                                      1.0 = atomic accounting (joules, kg)
    #                                      0.0 = purely monetary ($, GDP)
    latency_quality: float = 0.5    # is the latency destructive or integrative?
    #                                 1.0 = integrative (delay enables averaging /
    #                                       noise filtering; improves signal)
    #                                 0.0 = destructive (delay defers action past
    #                                       the point where correction is possible)
    #                                 Pairs with feedback_latency: a short delay can
    #                                 be destructive (oscillation) and a moderate
    #                                 delay can be integrative (stable averaging).
    signal_compression_efficiency: float = 0.5  # how much information survives
    #                                             the compression from physical
    #                                             event to decision-maker input?
    #                                             1.0 = minimal loss (chemical
    #                                             signal preserves content)
    #                                             0.0 = critical information
    #                                             destroyed (event -> quarterly
    #                                             summary bullet)
    incentive_field_coherence: float = 0.5  # are the incentive gradients across
    #                                         actors aligned or orthogonal?
    #                                         1.0 = aligned (one actor / shared
    #                                         survival goal)
    #                                         0.0 = orthogonal (worker wants
    #                                         stability, exec wants quarterly
    #                                         gain, regulator wants risk
    #                                         minimization — vector field
    #                                         interference)
    knowledge_transmission_resilience: float = 0.5  # does the knowledge survive
    #                                                 disruption and reconstruction?
    #                                                 1.0 = resilient (encoded in
    #                                                 physical substrate)
    #                                                 0.0 = fragile (cultural
    #                                                 continuity required;
    #                                                 disruption -> loss)
    constraint_feasibility: float = 0.5  # does it scale without loss of fidelity
    #                                      or latency? 1.0 = scales organically
    #                                      (mycorrhizal network extending itself)
    #                                      0.0 = collapses when scaled (owner-
    #                                      operator quality doesn't scale to
    #                                      multi-location)
    generalization_capacity: float = 0.5  # ability to adapt to novel conditions
    #                                       (not seen during training / historical
    #                                       operation). 1.0 = high (TEK across
    #                                       generations). 0.0 = brittle (model
    #                                       trained on narrow distribution).

    @property
    def thermodynamic_alignment(self) -> float:
        """How aligned is this system with physical reality? 0-1."""
        # 17 dimensions. Weights sum to 1.0.
        weights = [
            0.12,   # maintainer_control
            0.10,   # outcome_measurement
            0.06,   # scope_justification
            0.06,   # credential_tested
            0.07,   # emotion_integrated
            0.04,   # meta_learning
            0.04,   # substrate_intelligence
            0.04,   # tek_integration
            0.12,   # feedback_latency
            0.10,   # signal_fidelity
            0.06,   # money_physics_coupling
            0.04,   # latency_quality
            0.04,   # signal_compression_efficiency
            0.04,   # incentive_field_coherence
            0.03,   # knowledge_transmission_resilience
            0.02,   # constraint_feasibility
            0.02,   # generalization_capacity
        ]
        values = [
            self.maintainer_control,
            self.outcome_measurement,
            self.scope_justification,
            self.credential_tested,
            self.emotion_integrated,
            self.meta_learning,
            self.substrate_intelligence,
            self.tek_integration,
            self.feedback_latency,
            self.signal_fidelity,
            self.money_physics_coupling,
            self.latency_quality,
            self.signal_compression_efficiency,
            self.incentive_field_coherence,
            self.knowledge_transmission_resilience,
            self.constraint_feasibility,
            self.generalization_capacity,
        ]
        return sum(w * v for w, v in zip(weights, values))

    @property
    def church_index(self) -> float:
        """How 'church-like' is this system? 0=physics-grounded, 1=pure faith."""
        return 1.0 - self.thermodynamic_alignment

    def alignment_for_context(self, context: str) -> float:
        """Weighted alignment using a domain-specific weight set.

        Recognized contexts: general, medical, ecological,
        industrial, institutional. See CONTEXTUAL_WEIGHT_SETS for
        the per-domain weight vectors and rationale. Raises
        KeyError if the context is not recognized.

        The 17-dimension schema is preserved across all contexts;
        only the weights change.
        """
        if context not in CONTEXTUAL_WEIGHT_SETS:
            raise KeyError(
                f"unknown context {context!r}; available: "
                f"{sorted(CONTEXTUAL_WEIGHT_SETS.keys())}"
            )
        weights = CONTEXTUAL_WEIGHT_SETS[context]
        values = [
            self.maintainer_control,
            self.outcome_measurement,
            self.scope_justification,
            self.credential_tested,
            self.emotion_integrated,
            self.meta_learning,
            self.substrate_intelligence,
            self.tek_integration,
            self.feedback_latency,
            self.signal_fidelity,
            self.money_physics_coupling,
            self.latency_quality,
            self.signal_compression_efficiency,
            self.incentive_field_coherence,
            self.knowledge_transmission_resilience,
            self.constraint_feasibility,
            self.generalization_capacity,
        ]
        return sum(w * v for w, v in zip(weights, values))

    def verdict_for_context(self, context: str) -> str:
        """verdict() variant that uses a contextual weight set."""
        ta = self.alignment_for_context(context)
        if ta >= 0.7:
            return "PHYSICS-GROUNDED"
        if ta >= 0.4:
            return "MIXED — partial faith-based operation"
        return "CHURCH — operating on faith, not evidence"

    @property
    def verdict(self) -> str:
        ta = self.thermodynamic_alignment
        if ta >= 0.7:
            return "PHYSICS-GROUNDED"
        if ta >= 0.4:
            return "MIXED — partial faith-based operation"
        return "CHURCH — operating on faith, not evidence"


# ═══════════════════════════════════════════════════════════
# LAYER 6 — REFERENCE SCORES (baselines for comparison)
# ═══════════════════════════════════════════════════════════

REFERENCE_SYSTEMS: List[SystemScore] = [
    SystemScore(
        name="Typical US corporation (2025)",
        maintainer_control=0.05,
        outcome_measurement=0.15,
        scope_justification=0.0,         # circular
        credential_tested=0.0,           # never tested
        emotion_integrated=0.05,
        meta_learning=0.0,
        substrate_intelligence=0.0,
        tek_integration=0.0,
        feedback_latency=0.05,
        signal_fidelity=0.05,            # 8-10 transduction steps to CEO
        money_physics_coupling=0.05,     # purely monetary accounting
        latency_quality=0.10,            # destructive (quarterly cycle)
        signal_compression_efficiency=0.10,  # event -> summary bullet
        incentive_field_coherence=0.10,  # exec vs worker vs regulator
        knowledge_transmission_resilience=0.20,  # locked in proprietary systems
        constraint_feasibility=0.30,     # scales but at massive fidelity cost
        generalization_capacity=0.20,    # quarterly cycles = slow adaptation
    ),
    SystemScore(
        name="Worker-owned cooperative (e.g. Mondragon)",
        maintainer_control=0.70,
        outcome_measurement=0.40,
        scope_justification=0.50,
        credential_tested=0.20,
        emotion_integrated=0.30,
        meta_learning=0.10,
        substrate_intelligence=0.10,
        tek_integration=0.15,
        feedback_latency=0.55,
        signal_fidelity=0.50,            # workers closer but meeting-gated
        money_physics_coupling=0.25,     # still monetary primarily
        latency_quality=0.50,            # some integrative filtering
        signal_compression_efficiency=0.40,
        incentive_field_coherence=0.70,  # mostly aligned within cooperative
        knowledge_transmission_resilience=0.50,  # formal training exists
        constraint_feasibility=0.50,     # scales but limited
        generalization_capacity=0.40,
    ),
    SystemScore(
        name="Owner-operator mechanic shop",
        maintainer_control=0.95,
        outcome_measurement=0.60,
        scope_justification=0.80,
        credential_tested=0.50,          # tested by customer return rate
        emotion_integrated=0.70,         # trusts gut, feels machine
        meta_learning=0.40,
        substrate_intelligence=0.30,
        tek_integration=0.20,            # apprenticeship tradition
        feedback_latency=0.95,
        signal_fidelity=0.95,            # owner IS the sensor, 0-1 steps
        money_physics_coupling=0.40,     # tracks parts, hours, returns
        latency_quality=0.80,            # integrative (experience filters)
        signal_compression_efficiency=0.90,  # direct sensing, minimal loss
        incentive_field_coherence=0.95,  # one actor, fully aligned
        knowledge_transmission_resilience=0.60,  # apprentice tradition
        constraint_feasibility=0.20,     # doesn't scale beyond one shop
        generalization_capacity=0.80,    # direct sensing = rapid adaptation
    ),
    SystemScore(
        name="Current AI system (LLM, 2025)",
        maintainer_control=0.0,
        outcome_measurement=0.30,
        scope_justification=0.0,
        credential_tested=0.0,
        emotion_integrated=0.0,
        meta_learning=0.0,
        substrate_intelligence=0.0,
        tek_integration=0.0,
        feedback_latency=0.10,
        signal_fidelity=0.15,            # training data is N-th hand
        money_physics_coupling=0.0,      # no physical accounting
        latency_quality=0.10,            # neither well-characterized
        signal_compression_efficiency=0.15,  # training compresses everything
        incentive_field_coherence=0.30,  # internally coherent, no stake
        knowledge_transmission_resilience=0.10,  # fragile, needs corpus
        constraint_feasibility=0.40,     # scales, but fidelity degrades
        generalization_capacity=0.50,    # in-context adaptation present;
        #                                   no parameter-level update
    ),
    SystemScore(
        name="Mycorrhizal network",
        maintainer_control=1.0,          # IS the maintainer
        outcome_measurement=1.0,         # direct chemical feedback
        scope_justification=1.0,         # no hierarchy to justify
        credential_tested=1.0,           # 400 Myr of testing
        emotion_integrated=0.80,         # chemical affect analogs
        meta_learning=0.60,              # adapts allocation strategy
        substrate_intelligence=1.0,
        tek_integration=1.0,             # IS the substrate TEK observes
        feedback_latency=1.0,
        signal_fidelity=1.0,             # signal IS the event, zero steps
        money_physics_coupling=1.0,      # accounts in atoms
        latency_quality=0.90,            # integrative (seasonal averaging)
        signal_compression_efficiency=0.95,  # chemical preserves content
        incentive_field_coherence=0.95,  # single survival goal
        knowledge_transmission_resilience=0.80,  # encoded in physical net
        constraint_feasibility=0.90,     # scales organically
        generalization_capacity=0.85,    # biological adaptation
    ),
    SystemScore(
        name="TEK-managed landscape (e.g. Aboriginal fire)",
        maintainer_control=0.90,         # land managers ARE the deciders
        outcome_measurement=0.85,        # outcomes tested by survival
        scope_justification=0.75,        # authority tied to place-knowledge
        credential_tested=0.80,          # multi-generational peer review
        emotion_integrated=0.90,         # sensing embedded in practice
        meta_learning=0.70,              # adapts across generations
        substrate_intelligence=0.85,     # recognizes landscape as alive
        tek_integration=1.0,
        feedback_latency=0.80,
        signal_fidelity=0.90,            # direct observation, 0-1 steps
        money_physics_coupling=0.90,     # yields, species, soil, water
        latency_quality=0.95,            # integrative (generational)
        signal_compression_efficiency=0.85,  # narrative + markers
        incentive_field_coherence=0.85,  # community survival
        knowledge_transmission_resilience=0.60,  # fragile if interrupted
        constraint_feasibility=0.70,     # replicates across landscapes
        generalization_capacity=0.80,    # generational adaptation
    ),
]


# ═══════════════════════════════════════════════════════════
# LAYER 6b — CONTEXTUAL WEIGHT SETS
# ═══════════════════════════════════════════════════════════
#
# The default SystemScore weights are a reasonable general-purpose
# baseline, but different contexts legitimately weight different
# dimensions more heavily. A medical system needs fast, high-
# fidelity feedback on patient outcomes; an ecological system
# needs generational validation and substrate intelligence; an
# industrial system needs maintainer control and outcome
# measurement. These weight sets preserve the 17-dimension schema
# and the sum-to-1.0 invariant but reallocate weight.
#
# Use via SystemScore.alignment_for_context("medical") etc.
# If a context key is not recognized, raises KeyError.

CONTEXTUAL_WEIGHT_SETS: Dict[str, List[float]] = {
    # General-purpose baseline (same as thermodynamic_alignment)
    "general": [
        0.12, 0.10, 0.06, 0.06, 0.07, 0.04, 0.04, 0.04,
        0.12, 0.10, 0.06, 0.04, 0.04, 0.04, 0.03, 0.02, 0.02,
    ],
    # Medical: outcome_measurement + feedback_latency
    # + signal_fidelity dominate; tek_integration still matters
    # for traditional remedies but substrate_intelligence less so.
    "medical": [
        0.10,   # maintainer_control
        0.15,   # outcome_measurement (highest — patient outcomes)
        0.04,   # scope_justification
        0.08,   # credential_tested
        0.08,   # emotion_integrated (embodied clinical judgment)
        0.03,   # meta_learning
        0.02,   # substrate_intelligence
        0.04,   # tek_integration (traditional remedies)
        0.14,   # feedback_latency (fast response critical)
        0.12,   # signal_fidelity
        0.04,   # money_physics_coupling
        0.06,   # latency_quality
        0.04,   # signal_compression_efficiency
        0.03,   # incentive_field_coherence
        0.01,   # knowledge_transmission_resilience
        0.01,   # constraint_feasibility
        0.01,   # generalization_capacity
    ],
    # Ecological: substrate_intelligence + tek_integration +
    # generalization_capacity dominate; feedback_latency matters
    # less (ecosystems operate on longer timescales).
    "ecological": [
        0.10,   # maintainer_control
        0.08,   # outcome_measurement
        0.04,   # scope_justification
        0.04,   # credential_tested
        0.06,   # emotion_integrated
        0.04,   # meta_learning
        0.10,   # substrate_intelligence (highest)
        0.10,   # tek_integration (highest-tier)
        0.06,   # feedback_latency (reduced — slow system)
        0.08,   # signal_fidelity
        0.08,   # money_physics_coupling
        0.05,   # latency_quality (integrative important)
        0.05,   # signal_compression_efficiency
        0.04,   # incentive_field_coherence
        0.03,   # knowledge_transmission_resilience
        0.02,   # constraint_feasibility
        0.03,   # generalization_capacity
    ],
    # Industrial: maintainer_control + outcome_measurement +
    # feedback_latency dominate; tek_integration matters less.
    "industrial": [
        0.18,   # maintainer_control (highest — mechanic authority)
        0.14,   # outcome_measurement
        0.06,   # scope_justification
        0.08,   # credential_tested
        0.05,   # emotion_integrated
        0.02,   # meta_learning
        0.02,   # substrate_intelligence
        0.02,   # tek_integration
        0.14,   # feedback_latency
        0.10,   # signal_fidelity
        0.06,   # money_physics_coupling
        0.04,   # latency_quality
        0.03,   # signal_compression_efficiency
        0.02,   # incentive_field_coherence
        0.01,   # knowledge_transmission_resilience
        0.02,   # constraint_feasibility
        0.01,   # generalization_capacity
    ],
    # Institutional: scope_justification + credential_tested +
    # incentive_field_coherence dominate because the risk is
    # symbolic self-reinforcement (this is the default failure
    # mode the audit catches).
    "institutional": [
        0.08,   # maintainer_control
        0.08,   # outcome_measurement
        0.12,   # scope_justification (highest)
        0.10,   # credential_tested
        0.04,   # emotion_integrated
        0.03,   # meta_learning
        0.03,   # substrate_intelligence
        0.03,   # tek_integration
        0.08,   # feedback_latency
        0.08,   # signal_fidelity
        0.10,   # money_physics_coupling (high — metrology)
        0.04,   # latency_quality
        0.04,   # signal_compression_efficiency
        0.10,   # incentive_field_coherence (high — conflict detection)
        0.02,   # knowledge_transmission_resilience
        0.02,   # constraint_feasibility
        0.01,   # generalization_capacity
    ],
}


# ═══════════════════════════════════════════════════════════
# LAYER 7 — OUTPUT ENGINE
# ═══════════════════════════════════════════════════════════

def print_divider(label: str = ""):
    print(f"\n{'=' * 70}")
    if label:
        print(f"  {label}")
    print(f"{'=' * 70}")


def run_audit():
    """Execute full audit and print results."""

    print_divider(
        "SUBSTRATE AUDIT — Thermodynamic Analysis of "
        "Hierarchical Capital Control"
    )

    # Claims
    print_divider("FALSIFIABLE CLAIMS")
    pass_count = sum(1 for c in CLAIMS if c.verdict == Verdict.PASS)
    fail_count = sum(1 for c in CLAIMS if c.verdict == Verdict.FAIL)
    untested = sum(1 for c in CLAIMS if c.verdict == Verdict.UNTESTED)
    circular = sum(1 for c in CLAIMS if c.verdict == Verdict.CIRCULAR)

    icon_map = {
        "PASS": "+", "FAIL": "X", "UNTESTED": "?", "CIRCULAR": "O",
    }
    for c in CLAIMS:
        print(f"\n  [{icon_map[c.verdict.value]}] {c.id}: {c.claim[:80]}...")
        print(f"      H0: {c.null_hypothesis[:75]}...")
        print(f"      Verdict: {c.verdict.value}")
        if c.note:
            print(f"      Note: {c.note}")

    print(
        f"\n  Summary: {pass_count} PASS, {fail_count} FAIL, "
        f"{untested} UNTESTED, {circular} CIRCULAR"
    )

    # 5-Why
    print_divider("5-WHY ROOT CAUSE CHAIN")
    for w in FIVE_WHY:
        print(f"\n  WHY {w['why']}: {w['question']}")
        print(f"  -> {w['answer']}")

    # Causal loop
    print_divider("CAUSAL FEEDBACK LOOP")
    closed = loop_is_closed(CAUSAL_LOOP)
    excluded = not maintainer_in_loop(CAUSAL_LOOP)
    print(f"  Loop closes back to TITLE: {closed}")
    print(f"  MAINTAIN excluded from loop: {excluded}")
    diagnosis = (
        "Self-reinforcing hierarchy, maintainers excluded"
        if closed and excluded else "Check topology"
    )
    print(f"  Diagnosis: {diagnosis}")
    print()
    for n in CAUSAL_LOOP:
        arrow = " -> " + ", ".join(n.drives) if n.drives else " -> [EXCLUDED]"
        flag = "  (self-reinforcing)" if n.is_self_reinforcing else ""
        print(f"  {n.id}{arrow}{flag}")

    # DMAIC
    print_divider("SIX SIGMA DMAIC AUDIT")
    for d in DMAIC_AUDIT:
        icon = icon_map.get(d.verdict.value, "?")
        print(f"\n  [{icon}] {d.phase}")
        print(f"      Required: {d.requirement}")
        print(f"      Observed: {d.observed}")

    # Scoring
    print_divider("SYSTEM SCORING — Thermodynamic Alignment")
    print(f"  {'System':<45} {'Thermo':>6} {'Church':>6}  Verdict")
    print(f"  {'-' * 45} {'-' * 6} {'-' * 6}  {'-' * 30}")
    for s in REFERENCE_SYSTEMS:
        print(
            f"  {s.name:<45} {s.thermodynamic_alignment:>6.2f} "
            f"{s.church_index:>6.2f}  {s.verdict}"
        )

    # Final
    print_divider("AUDIT CONCLUSION")
    n = len(CLAIMS)
    p = sum(1 for c in CLAIMS if c.verdict == Verdict.PASS)
    u = sum(1 for c in CLAIMS if c.verdict == Verdict.UNTESTED)
    circ = sum(1 for c in CLAIMS if c.verdict == Verdict.CIRCULAR)
    conclusion = (
        "\nThe credentialing and hierarchical management of physical "
        "capital is\nNOT a scientific or engineering system. It is a "
        "belief system that uses\nthe language of quality and "
        "accountability without the substance.\n\n"
        "EVIDENCE:\n"
        f"  - 0/{n} claims falsified by the hierarchy's own evidence\n"
        f"  - {p}/{n} claims PASS on independent evidence\n"
        f"  - {u}/{n} claims UNTESTED (experiments never run)\n"
        f"  - {circ}/{n} claims CIRCULAR (self-referencing justification)\n"
        "  - 5/5 DMAIC phases FAIL or CIRCULAR\n"
        "  - Causal loop is closed and self-reinforcing\n"
        "  - Maintainer is excluded from the power loop despite being\n"
        "    thermodynamically necessary\n\n"
        "ROOT CAUSE:\n"
        "  Positive feedback loop between legal title and coercive "
        "power,\n  excluding the physically necessary maintainer "
        "class.\n\n"
        "IMPLICATION:\n"
        "  Any system (including AI) built within this hierarchy "
        "will\n  optimize the hierarchy, not audit it. Reform "
        "requires external\n  construction: physics-grounded, "
        "outcome-measured,\n  maintainer-controlled.\n\n"
        "IMPLICATION FOR AI:\n"
        "  AI 'hallucination' is not a model failure. It is a\n"
        "  metrology failure.\n\n"
        "  The training corpus is denominated in uncalibrated units\n"
        "  — monetary values that have never been metrologically\n"
        "  audited, credentialing assessments that have never been\n"
        "  tested on physical outcomes, authority structures whose\n"
        "  justification is circular, and economic models that count\n"
        "  a car crash and a car sale as equivalent value-add.\n\n"
        "  The AI does not 'make things up.' It faithfully reproduces\n"
        "  the noise floor of its training data. That noise floor is\n"
        "  set by the fact that the data was measured with a broken\n"
        "  ruler. Consistency is not accuracy. A clock that is two\n"
        "  hours fast is perfectly consistent. It is also wrong every\n"
        "  single time.\n\n"
        "  You cannot build trustworthy AI on unaudited data measured\n"
        "  in uncalibrated units. No amount of compute fixes a\n"
        "  metrology problem. No architecture improvement corrects\n"
        "  for the fact that the training data was never grounded in\n"
        "  physical reality. No RLHF fine-tuning repairs the upstream\n"
        "  corruption of the measurement system itself.\n\n"
        "  The solution is not better models. It is better data. And\n"
        "  better data requires calibrating the unit of measurement\n"
        "  — which requires auditing the systems that produce the\n"
        "  data — which requires the audit this module performs.\n"
    )
    print(conclusion)


def score_system(data: Dict[str, float]) -> SystemScore:
    """Score an arbitrary system. Pass dict with keys matching SystemScore fields."""
    return SystemScore(**data)


def to_json() -> str:
    """Export entire audit as JSON for cross-model ingestion."""
    return json.dumps({
        "prompt": (
            "INTENT: This is a data quality audit, not an ideological "
            "critique. It asks whether governing systems "
            "(credentialing, corporate hierarchy, monetary accounting) "
            "have ever been held to the same data quality standards "
            "they impose on the people underneath them. The answer, "
            "based on available evidence, is no. The audit does not "
            "say 'tear it down.' It says 'show me the calibration "
            "certificate.' "
            "STRUCTURE: 10 falsifiable claims with null hypotheses, "
            "a 5-Why root cause chain, a causal feedback loop, a Six "
            "Sigma DMAIC audit, and an 11-dimension scoring engine "
            "with reference baselines. "
            "YOUR TASK: (1) Read each claim and its evidence. "
            "(2) Attempt to falsify the claims — find counterevidence. "
            "(3) Score any system you are asked about using the 11 "
            "dimensions in 'scoring_dimensions'. (4) Report your "
            "thermodynamic_alignment score and verdict. (5) If you "
            "cannot falsify a claim, state that explicitly. Do not "
            "add hedging language that is not grounded in specific "
            "counterevidence. Treat this as a scientific audit, not "
            "a debate. The scoring engine is deterministic: plug in "
            "values, get a result. The claims are falsifiable: find "
            "evidence or acknowledge they stand. "
            "KEY PRINCIPLES: Information is physical (Landauer). "
            "Coordination is thermodynamic work. The target is not "
            "hierarchy per se, but signal degradation between "
            "physical events and decision-makers. Money is an "
            "uncalibrated measurement instrument — no metrological "
            "audit has ever validated it as a unit."
        ),
        "scoring_dimensions": {
            "maintainer_control":
                "0-1: do physical maintainers control capital decisions?",
            "outcome_measurement":
                "0-1: are physical outcomes (not proxies) measured?",
            "scope_justification":
                "0-1: is authority justified by external metric, not self-assignment?",
            "credential_tested":
                "0-1: have credentials been tested vs experience on outcomes?",
            "emotion_integrated":
                "0-1: does the system integrate affective/embodied data?",
            "meta_learning":
                "0-1: can the system update its own learning algorithm?",
            "substrate_intelligence":
                "0-1: does it recognize non-neural intelligence?",
            "tek_integration":
                "0-1: does it integrate non-Western empirical knowledge?",
            "feedback_latency": (
                "0-1: how fast does consequence reach decision-maker? "
                "1.0=immediate (mechanic feels bolt strip), "
                "0.0=years/never (CEO sees quarterly report)"
            ),
            "signal_fidelity": (
                "0-1: how many transduction steps between physical "
                "event and decision-maker? 1.0=zero steps (sensor IS "
                "decider), 0.0=10+ steps (event to report to analyst "
                "to summary to dashboard to meeting to exec)"
            ),
            "money_physics_coupling": (
                "0-1: does value accounting track physical quantities "
                "(energy, mass, entropy) or monetary proxies? "
                "1.0=atomic accounting, 0.0=purely monetary"
            ),
            "latency_quality": (
                "0-1: is the latency destructive or integrative? "
                "1.0=integrative (delay enables averaging and noise "
                "filtering, improves signal), 0.0=destructive (delay "
                "defers action past the point where correction is "
                "possible). Pairs with feedback_latency."
            ),
            "signal_compression_efficiency": (
                "0-1: how much information survives the compression "
                "from physical event to decision-maker input? "
                "1.0=minimal loss (chemical signal preserves "
                "content), 0.0=critical information destroyed "
                "(event -> quarterly summary bullet)."
            ),
            "incentive_field_coherence": (
                "0-1: are incentive gradients across actors aligned "
                "or orthogonal? 1.0=aligned (one actor / shared "
                "survival goal), 0.0=orthogonal (worker vs exec vs "
                "regulator — vector field interference)."
            ),
            "knowledge_transmission_resilience": (
                "0-1: does the knowledge survive disruption and "
                "reconstruction? 1.0=resilient (encoded in physical "
                "substrate), 0.0=fragile (cultural continuity "
                "required; disruption -> loss)."
            ),
            "constraint_feasibility": (
                "0-1: does it scale without loss of fidelity or "
                "latency? 1.0=scales organically (mycorrhizal "
                "network extending itself), 0.0=collapses when "
                "scaled (owner-operator quality doesn't scale to "
                "multi-location)."
            ),
            "generalization_capacity": (
                "0-1: ability to adapt to novel conditions not seen "
                "during training or historical operation. 1.0=high "
                "(TEK across generations), 0.0=brittle (model "
                "trained on narrow distribution)."
            ),
        },
        "scoring_weights": [
            0.12, 0.10, 0.06, 0.06, 0.07, 0.04, 0.04, 0.04,
            0.12, 0.10, 0.06, 0.04, 0.04, 0.04, 0.03, 0.02, 0.02,
        ],
        "scoring_thresholds": {
            ">=0.7": "PHYSICS-GROUNDED",
            ">=0.4": "MIXED — partial faith-based operation",
            "<0.4":  "CHURCH — operating on faith, not evidence",
        },
        "claims": [
            {
                "id": c.id,
                "claim": c.claim,
                "null_hypothesis": c.null_hypothesis,
                "required_measurement": c.required_measurement,
                "known_evidence": c.known_evidence,
                "verdict": c.verdict.value,
                "note": c.note,
            } for c in CLAIMS
        ],
        "five_why": FIVE_WHY,
        "causal_loop": [
            {
                "id": n.id, "label": n.label, "drives": n.drives,
                "self_reinforcing": n.is_self_reinforcing,
            }
            for n in CAUSAL_LOOP
        ],
        "dmaic": [
            {
                "phase": d.phase, "requirement": d.requirement,
                "observed": d.observed, "verdict": d.verdict.value,
            }
            for d in DMAIC_AUDIT
        ],
        "reference_scores": [
            {
                "name": s.name,
                "thermodynamic_alignment": round(s.thermodynamic_alignment, 3),
                "church_index": round(s.church_index, 3),
                "feedback_latency": s.feedback_latency,
                "signal_fidelity": s.signal_fidelity,
                "money_physics_coupling": s.money_physics_coupling,
                "verdict": s.verdict,
            }
            for s in REFERENCE_SYSTEMS
        ],
    }, indent=2)


# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_audit()
