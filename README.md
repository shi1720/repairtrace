# RepairTrace

Provenance-preserving access redesign for circular products. Research artifact by Shivam Gupta.

The method keeps primitive prerequisite constraints distinct from derived reachability. It evaluates joint edits, provides an exact mixed-integer selector, and supplies sharp access bounds when only baseline reachability is known. It operates on additive conjunctive DAG models. The artifact does not establish mechanical feasibility, actual technician-time reductions, or a production benefit.

## Reproduce

Python 3.9 or later (the recorded run uses Python 3.9.6). From this directory:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/experiments.py
.venv/bin/python src/envelopes.py
.venv/bin/python src/sensitivity.py
.venv/bin/python src/summarize.py
.venv/bin/python src/figures.py
.venv/bin/python src/demo.py
```

The default run uses the frozen metadata and does not contact iFixit. `src/collect.py` is an optional metadata refresh; live guides may change. To reproduce the reported paper, retain `data/guide_metadata.json` at its recorded revisions. Run time, solver floating-point gaps, and platform strings can vary. All primary objectives and selections are deterministic for the pinned environment.

## Contents

- `src/model.py`: access oracle, Boolean provenance circuit, exhaustive selector, adaptive greedy, and exact MILP.
- `src/experiments.py`: independent DFS verification, 180 controlled maps, five public metadata cases, 80 exhaustive/MILP checks, and 30 scaling cases.
- `src/envelopes.py`: exhaustive sharp-bound verification over all 357 ordered five-node reachability classes.
- `src/sensitivity.py`: public-map sensitivity to zero-own-step guide modules.
- `src/demo.py`: replayable certificate for the complementary two-edit construction.
- `results/`: per-instance objectives, selected edge identities, solver bounds, and verification counts.
- `figures/`: vector figures generated from these results.
- `data/`: source metadata and attribution.

The manuscript is kept outside the public Git history pending author and venue review. The repository is a research artifact, not a claim of acceptance or peer review.

## Reproduced findings

- 441,600 provenance/independent-DFS pair checks: no mismatch.
- 54,405 access-envelope target checks: no violation; exact endpoints verified.
- 80 MILP/exhaustive optimal objectives: agreement within 1e-7.
- 180 controlled instances: naive closure selections have strictly greater realized effort than primitive-optimal selections in 113 cases. Median excess effort is 1.81% of baseline.
- Public metadata: 89 replacement-guide targets across five products. Four have different selected edits under raw-list and reduced-list primitive assumptions, although baseline reachability agrees.

These are generated-model results and documentation ambiguity results, respectively. Neither constitutes a measured physical repair improvement. The closure-based selector is valid as a conservative optimizer under the paper's broad reachability-only uncertainty class; it is inaccurate when interpreted as an exact known-primitive prediction.

## Licenses

Original code is MIT licensed. iFixit-derived metadata is CC BY-NC-SA 3.0, attributed to iFixit and the guides at the source URLs and revision identifiers recorded in the metadata. See `data/PROVENANCE.txt`. Public guide modules are documentation, not validated engineering primitives. Commercial use of iFixit data requires appropriate permission or commercial licensing; the algorithm can operate on independently licensed manufacturer data. Figure 3 derives from those metadata and retains their noncommercial share-alike terms; the other figures and generated results are original research artifacts.
