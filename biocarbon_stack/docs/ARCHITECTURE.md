# Architecture

How the modules couple. What flows where.

```
                    ATMOSPHERIC CO2 + CH4 BUDGET
                              |
                              v
        +---------------------+---------------------+
        |                                           |
    DRAWDOWN                                    BUFFERS
        |                                           |
        v                                           v
+----------------+                          +------------------+
| WETLAND CORE   |<-spike mitigation------->| BOUNDARY CONDS   |
|   peat         |                          |   kelp <- otter  |
|   methanotroph |                          |   permafrost <-  |
|   methanogen   |                          |     herbivore    |
+--------+-------+                          +---------+--------+
         |                                            |
         | aerenchyma                                 | nested thresholds
         v                                            v
+----------------+                          +------------------+
| ADAPTIVE LAYER |<-load-bearing under all->| REDUNDANCY       |
|   earthworm    |                          |   guild stacking |
|   mycorrhizal  |                          |   range shift    |
+--------+-------+                          +---------+--------+
         |                                            |
         | regional species filter                    | option space
         v                                            v
+----------------+                          +------------------+
| MARINE CORE    |                          | GOVERNANCE       |
|   kelp         |                          |   held open      |
|   deep export  |                          |   not resolved   |
+--------+-------+                          +------------------+
         |
         v
+----------------+
| GLOBAL POTENT  |
|   extent x     |
|   rate         |
+--------+-------+
         |
         v
+----------------+
| MONTE CARLO    |
|   uncertainty  |
+----------------+
```

## Coupling rules

1. **Wetland and adaptive layer are mutually reinforcing.** Earthworm
   porosity reduces methanotroph colonization lag during drawdowns.
   Wetland anoxia kills earthworms in saturated zones — earthworms
   work the rhizosphere edge and upland margins, not the saturated
   center.
1. **Buffers nest.** Kelp protected by otter. Otter protected by
   thermal range. If thermal range exceeded, otter buffer fails
   regardless of how many otters are present. Same logic for
   herbivore-permafrost.
1. **Redundancy stacking is the response to nested buffer failure.**
   Multi-species guilds across geographic dispersion. No single
   climate event affects all nodes simultaneously.
1. **Regional species filter applies before deployment.** Glaciated
   North American forests get mycorrhizal-only protocol, not
   earthworm. Tropics get native-only filter on Amynthas. Wetland
   aquatic gets native semi-aquatic species only.
1. **Phase 0 calibration runs before Phase 1 scaling.** 100 nodes,
   3 years, biome-specific data. No global rollout on theoretical
   numbers.

## Where this composes with other JinnZ2 frameworks

- **earth-systems-physics**: this repo IS a layer of earth-systems-physics,
  the biosphere-hydrosphere-atmosphere coupled subsystem. Should be
  imported as a module, not maintained separately, eventually.
- **first_principles_audit**: run the audit on every parameter and
  coupling here. The audit will flag estimated values, missing
  parameters, and bias patterns.
- **assumption_validator**: every parameter range in this framework
  is an assumption with validity bounds. The validator should monitor
  whether observed system behavior stays inside the bounds.
- **PhysicsGuard**: any policy claim made on top of this framework
  should pass through PhysicsGuard. Claims like “this solves climate
  change” fail the physics check. Claims like “this provides 30 to
  45 percent of growth offset under specified conditions” survive.
- **energy_english**: the framework should be readable by an energy_english
  parser. Verb-first physics, no noun-first morality, no narrative
  closure. The README and docstrings target this.
- **Combine-Cognitive-Architecture**: this framework is a constraint
  geometry that humans and AIs collide their proposals against. The
  collision space lets the framework refine.
- **Resilience**: scraper principle, formal-actual gap, and
  asymmetric ratchet dynamics from the resilience repo apply directly
  to deployment of this framework. Without that lens, biological
  restoration gets captured by extractive financial logic.

## Operating loop

The framework follows the JinnZ2 operating loop:

1. What am I missing?      -> OPEN_QUESTIONS.md, regional species filter
1. What else is related?   -> coupling rules, composition with other frameworks
1. How can risks be averted? -> nested buffers, redundancy stacking, Phase 0 calibration
1. What are the tail risks? -> cascading failure scenarios, regime shifts

Every module re-runs this loop. Output goes back into the framework
as new constraints.
