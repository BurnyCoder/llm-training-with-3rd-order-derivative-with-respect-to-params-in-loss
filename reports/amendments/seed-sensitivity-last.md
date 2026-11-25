# Seed sensitivity is the final stage

25 November 2026. The execution order changed after the initial development pilots and several TinyStories hybrid replications. The next hybrid arm was held at a published shared checkpoint. The historical ledger records the completed jobs at the transition. Both official test sets were sealed at that time. The primary and hybrid preregistrations govern the seed assignments, token horizons, comparison arms, decision rules and replay donors. [Transition record](../../results/verification/seed-order-transition.json) · [Primary preregistration](../preregistration.md) · [Hybrid preregistration](../hybrid/preregistration.md)

## Execution order

1. Complete both corpora’s single-seed pilots, strength searches, free references and trained controls. Finish the initial and fitted checkpoint geometry. The standalone hybrid example uses the first registered hybrid seed and the five arms whose inputs already exist.
2. Train and measure the first full-budget paired seed for AdamW, Hessian trace and third order in **both** model families. These runs count toward the original registered sample of eight.
3. Complete the other seven paired primary seeds per model family. Freeze every stage’s checkpoints before evaluating its test corpus. Report and publish the original primary comparisons as specified.
4. Finish the remaining registered hybrid replications. The first hybrid seed’s replay consumes the last seed’s schedule and runs after that donor. Reconcile all checkpoint flatness and publication milestones.
5. Seal the exact summaries, stage freezes, geometry and hybrid width records. **Run the seed-sensitivity analysis last.** The same reporting command then regenerates its results from the seal. [Study coordinator](../../src/thirdloss/study.py) · [Final analysis](../../src/thirdloss/seed_sensitivity.py)

## Final descriptive analysis

For each registered primary arm, report the median, sample standard deviation and observed range of full-corpus test NLL and weight-space width across seeds. For each hybrid, report the same summaries of development NLL and final weight width. For the prespecified primary NLL contrasts and the adaptive-versus-fixed and adaptive-versus-replay contrasts, form the difference within each seed before summarizing. Report the eight medians obtained by leaving out each complete seed pair in turn and their range. Keep a censored width explicit whenever a finite summary is unidentified. A single-seed control contributes its observed outcome to the study ledger.

A seed jointly controls initialization, document order and stochastic probes. The spread describes joint run-to-run variation on these fixed corpora. The final sensitivity summaries supplement the registered sign tests and median intervals. [Paired ML benchmarking](https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Abstract.html) · [Analysis protocol](../preregistration.md)
