# Planned runs

<!-- RUNS:START -->

## Current evidence and remaining runs

**Snapshot at 2026-11-26T08:53:01+00:00** · 199/305 experimental milestones complete.

**Recorded activity** · Between recorded training and scoring updates.

**Next scheduled work** · Research abstracts · Hessian trace · confirm seed 4 (1%).

The measured remaining-time scenarios are 19.59–20.23 machine-hours.

| Work | Complete | Remaining | Planned |
| --- | --- | --- | --- |
| TinyStories · development and controls | 12 | 0 | 12 |
| TinyStories · full-budget primary runs | 24 | 0 | 24 |
| TinyStories · frozen tests | 24 | 0 | 24 |
| TinyStories · checkpoint flatness | 64 | 28 | 92 |
| Research abstracts · development and controls | 12 | 0 | 12 |
| Research abstracts · full-budget primary runs | 11 | 13 | 24 |
| Research abstracts · frozen tests | 0 | 24 | 24 |
| Research abstracts · checkpoint flatness | 24 | 13 | 37 |
| TinyStories · shared hybrid checkpoints | 5 | 3 | 8 |
| TinyStories · full hybrid runs | 23 | 25 | 48 |

The final seed-sensitivity analysis follows every model, frozen test and flatness measurement. [Final analysis](seed-sensitivity.md) · [Measured time remaining](progress.md)

<details><summary>TinyStories · every planned run</summary>

| Phase | Seed | Arm | Strength | Training targets | Training and development | Frozen test | Flatness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pilot | 0 | [Third derivative](../results/stories-pilot-s00-third-r03/) | 3% | 2,097,152 | Complete | — | Complete |
| control | 0 | [Initial checkpoint](../results/stories-control-s00-initial-r00/) | 0% | 0 | Complete | — | Complete |
| control | 0 | [Unigram](../results/stories-control-s00-unigram-r00/) | 0% | 0 | Complete | — | Complete |
| pilot | 0 | [Ordinary AdamW](../results/stories-pilot-s00-ce-r00/) | 0% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/stories-pilot-s00-trace-r01/) | 1% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/stories-pilot-s00-trace-r03/) | 3% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/stories-pilot-s00-trace-r10/) | 10% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Third derivative](../results/stories-pilot-s00-third-r01/) | 1% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Third derivative](../results/stories-pilot-s00-third-r10/) | 10% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Squared Hessian norm](../results/stories-pilot-s00-hessian_norm-r03/) | 3% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Randomized gradient signs](../results/stories-pilot-s00-sham-r01/) | 1% | 2,097,152 | Complete | — | Complete |
| pilot | 0 | [Trace + third derivative](../results/stories-pilot-s00-combined-r01/) | 1% | 2,097,152 | Complete | — | Complete |
| branch | 21 | [Shared trace checkpoint](../results/stories-branch-s21-trunk-r01/) | 1% | 8,388,608 | Complete | — | Complete |
| hybrid | 21 | [Curvature-dependent hybrid](../results/stories-hybrid-s21-adaptive-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 21 | [Fixed late hybrid](../results/stories-hybrid-s21-late-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 21 | [Hessian trace](../results/stories-hybrid-s21-trace-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 21 | [Stronger trace](../results/stories-hybrid-s21-strong-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 21 | [Always-on hybrid](../results/stories-hybrid-s21-always-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| confirm | 1 | [Third derivative](../results/stories-confirm-s01-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 1 | [Ordinary AdamW](../results/stories-confirm-s01-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 1 | [Hessian trace](../results/stories-confirm-s01-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 2 | [Third derivative](../results/stories-confirm-s02-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 2 | [Ordinary AdamW](../results/stories-confirm-s02-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 2 | [Hessian trace](../results/stories-confirm-s02-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 3 | [Third derivative](../results/stories-confirm-s03-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 3 | [Ordinary AdamW](../results/stories-confirm-s03-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 3 | [Hessian trace](../results/stories-confirm-s03-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 4 | [Third derivative](../results/stories-confirm-s04-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 4 | [Ordinary AdamW](../results/stories-confirm-s04-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 4 | [Hessian trace](../results/stories-confirm-s04-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 5 | [Third derivative](../results/stories-confirm-s05-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 5 | [Ordinary AdamW](../results/stories-confirm-s05-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 5 | [Hessian trace](../results/stories-confirm-s05-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 6 | [Third derivative](../results/stories-confirm-s06-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 6 | [Ordinary AdamW](../results/stories-confirm-s06-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 6 | [Hessian trace](../results/stories-confirm-s06-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 7 | [Third derivative](../results/stories-confirm-s07-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 7 | [Ordinary AdamW](../results/stories-confirm-s07-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 7 | [Hessian trace](../results/stories-confirm-s07-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 8 | [Third derivative](../results/stories-confirm-s08-third-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| confirm | 8 | [Ordinary AdamW](../results/stories-confirm-s08-ce-r00/) | 0% | 16,777,216 | Complete | Complete | Complete |
| confirm | 8 | [Hessian trace](../results/stories-confirm-s08-trace-r01/) | 1% | 16,777,216 | Complete | Complete | Complete |
| branch | 22 | [Shared trace checkpoint](../results/stories-branch-s22-trunk-r01/) | 1% | 8,388,608 | Complete | — | Complete |
| hybrid | 22 | [Curvature-dependent hybrid](../results/stories-hybrid-s22-adaptive-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 22 | [Fixed late hybrid](../results/stories-hybrid-s22-late-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 22 | [Hessian trace](../results/stories-hybrid-s22-trace-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 22 | [Stronger trace](../results/stories-hybrid-s22-strong-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 22 | [Always-on hybrid](../results/stories-hybrid-s22-always-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 22 | [Cross-seed replay](../results/stories-hybrid-s22-replay-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| branch | 23 | [Shared trace checkpoint](../results/stories-branch-s23-trunk-r01/) | 1% | 8,388,608 | Complete | — | Complete |
| hybrid | 23 | [Curvature-dependent hybrid](../results/stories-hybrid-s23-adaptive-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 23 | [Fixed late hybrid](../results/stories-hybrid-s23-late-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 23 | [Hessian trace](../results/stories-hybrid-s23-trace-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 23 | [Stronger trace](../results/stories-hybrid-s23-strong-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 23 | [Always-on hybrid](../results/stories-hybrid-s23-always-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 23 | [Cross-seed replay](../results/stories-hybrid-s23-replay-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| branch | 24 | [Shared trace checkpoint](../results/stories-branch-s24-trunk-r01/) | 1% | 8,388,608 | Complete | — | Complete |
| hybrid | 24 | [Curvature-dependent hybrid](../results/stories-hybrid-s24-adaptive-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 24 | [Fixed late hybrid](../results/stories-hybrid-s24-late-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 24 | [Hessian trace](../results/stories-hybrid-s24-trace-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 24 | [Stronger trace](../results/stories-hybrid-s24-strong-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 24 | [Always-on hybrid](../results/stories-hybrid-s24-always-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| hybrid | 24 | [Cross-seed replay](../results/stories-hybrid-s24-replay-r01/) | 1% | 16,777,216 | Complete | — | Complete |
| branch | 25 | [Shared trace checkpoint](../results/stories-branch-s25-trunk-r01/) | 1% | 8,388,608 | Complete | — | Complete |
| hybrid | 25 | Curvature-dependent hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 25 | Fixed late hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 25 | Hessian trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 25 | Stronger trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 25 | Always-on hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 25 | Cross-seed replay | 1% | 16,777,216 | Planned | — | Pending |
| branch | 26 | Shared trace checkpoint | 1% | 8,388,608 | Planned | — | Pending |
| hybrid | 26 | Curvature-dependent hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 26 | Fixed late hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 26 | Hessian trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 26 | Stronger trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 26 | Always-on hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 26 | Cross-seed replay | 1% | 16,777,216 | Planned | — | Pending |
| branch | 27 | Shared trace checkpoint | 1% | 8,388,608 | Planned | — | Pending |
| hybrid | 27 | Curvature-dependent hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 27 | Fixed late hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 27 | Hessian trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 27 | Stronger trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 27 | Always-on hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 27 | Cross-seed replay | 1% | 16,777,216 | Planned | — | Pending |
| branch | 28 | Shared trace checkpoint | 1% | 8,388,608 | Planned | — | Pending |
| hybrid | 28 | Curvature-dependent hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 28 | Fixed late hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 28 | Hessian trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 28 | Stronger trace | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 28 | Always-on hybrid | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 28 | Cross-seed replay | 1% | 16,777,216 | Planned | — | Pending |
| hybrid | 21 | Cross-seed replay | 1% | 16,777,216 | Planned | — | Pending |

</details>

<details><summary>Research abstracts · every planned run</summary>

| Phase | Seed | Arm | Strength | Training targets | Training and development | Frozen test | Flatness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pilot | 0 | [Third derivative](../results/abstracts-pilot-s00-third-r03-fp64/) | 3% | 65,536 | Complete | — | Complete |
| control | 0 | [Initial checkpoint](../results/abstracts-control-s00-initial-r00/) | 0% | 0 | Complete | — | Complete |
| control | 0 | [Unigram](../results/abstracts-control-s00-unigram-r00/) | 0% | 0 | Complete | — | Complete |
| pilot | 0 | [Ordinary AdamW](../results/abstracts-pilot-s00-ce-r00/) | 0% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/abstracts-pilot-s00-trace-r01-fp64/) | 1% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/abstracts-pilot-s00-trace-r03-fp64/) | 3% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Hessian trace](../results/abstracts-pilot-s00-trace-r10-fp64/) | 10% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Third derivative](../results/abstracts-pilot-s00-third-r01-fp64/) | 1% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Third derivative](../results/abstracts-pilot-s00-third-r10-fp64/) | 10% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Squared Hessian norm](../results/abstracts-pilot-s00-hessian_norm-r03-fp64/) | 3% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Randomized gradient signs](../results/abstracts-pilot-s00-sham-r01-fp64/) | 1% | 65,536 | Complete | — | Complete |
| pilot | 0 | [Trace + third derivative](../results/abstracts-pilot-s00-combined-r01-fp64/) | 1% | 65,536 | Complete | — | Complete |
| confirm | 1 | [Third derivative](../results/abstracts-confirm-s01-third-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 1 | [Ordinary AdamW](../results/abstracts-confirm-s01-ce-r00/) | 0% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 1 | [Hessian trace](../results/abstracts-confirm-s01-trace-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 2 | [Third derivative](../results/abstracts-confirm-s02-third-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 2 | [Ordinary AdamW](../results/abstracts-confirm-s02-ce-r00/) | 0% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 2 | [Hessian trace](../results/abstracts-confirm-s02-trace-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 3 | [Third derivative](../results/abstracts-confirm-s03-third-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 3 | [Ordinary AdamW](../results/abstracts-confirm-s03-ce-r00/) | 0% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 3 | [Hessian trace](../results/abstracts-confirm-s03-trace-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 4 | [Third derivative](../results/abstracts-confirm-s04-third-r01-fp64/) | 1% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 4 | [Ordinary AdamW](../results/abstracts-confirm-s04-ce-r00/) | 0% | 524,288 | Complete | Awaiting freeze | Complete |
| confirm | 4 | Hessian trace | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 5 | Third derivative | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 5 | Ordinary AdamW | 0% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 5 | Hessian trace | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 6 | Third derivative | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 6 | Ordinary AdamW | 0% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 6 | Hessian trace | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 7 | Third derivative | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 7 | Ordinary AdamW | 0% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 7 | Hessian trace | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 8 | Third derivative | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 8 | Ordinary AdamW | 0% | 524,288 | Planned | Awaiting freeze | Pending |
| confirm | 8 | Hessian trace | 1% | 524,288 | Planned | Awaiting freeze | Pending |
| diagnostic | 0 | [Third derivative](../results/abstracts-pilot-s00-third-r03/) | 3% | 65,536 | Complete | — | Complete |

</details>

<!-- RUNS:END -->

| Stage | Trainable coordinates | Data | Confirmatory target tokens | Effective windows per update |
|---|---|---|---:|---:|
| stories | Four causal blocks, width 192, four heads, gated SiLU MLP width 512, tied embeddings and 4,096 tokens | TinyStories | 16,777,216 | 32 |
| abstracts | Pythia-410M with rank-eight QKV LoRA in every block, scale alpha 16 | 2024 arXiv abstracts | 524,288 | 8 |

AdamW peaks at 0.0003 for stories and 0.0001 for adapters, with betas 0.9 and 0.95, weight decay 0.1 on matrices, gradient norm clip 1, 5% warmup and cosine decay to 10% of peak. Use full-precision parameter derivatives and eager attention. Physical microbatching can change to fit GPU memory while preserving the effective batch and two-window derivative estimate. Data order and optimizer settings are paired. These are experimental design choices.

| Phase | Seed | Arms and budget |
|---|---:|---|
| Untrained controls | 0 | Evaluate initial checkpoint and training-token unigram on development text. |
| Pilot and development | 0 | Run third-order 3% first. Run ordinary AdamW and both derivative baselines on the same initial one-eighth of the stage horizon. Complete the equal 1%, 3%, 10% grid for trace and third order. Measure cost before confirmatory training. |
| Secondary controls | 0 | Squared Hessian norm at 3%, sign-scrambled third-order update, combined selected trace and third order. Use the development horizon and report them as pilot comparisons. |
| Confirmation | 1–8 | Ordinary, signed trace, and third order at the selected strength, each at the full stage horizon. |

Evaluate seed-paired final test predictions only when the stage has all planned confirmatory checkpoints. Preserve every development candidate. The one-week allocation prioritizes the two registered stages and their controls. The first 14 hours target a real one-seed pilot with its untrained controls. [Protocol](preregistration.md)

## Registered hybrid follow-up

The full queue completes both stages’ pilots and trained controls before additional seed replication. Both families receive a full-budget first seed before the remaining primary confirmations. The remaining hybrid seeds and cyclic replay follow the original test evaluations. The dedicated seed-sensitivity analysis runs last. [Execution order and descriptive statistics](amendments/seed-sensitivity-last.md)

The six TinyStories arms share eight paired seeds. Five branch from a common trace-trained checkpoint and one uses both penalties from initialization. Directional width is measured at three token counts. The curvature rule, replay donors, cap, stronger-trace calibration and decision threshold were fixed before follow-up outcomes. [Hybrid run matrix and decision rule](hybrid/preregistration.md) · [Research question](plan.md#curvature-dependent-penalty-weight)

## Secondary flatness measurements

Measure the saved AdamW, Hessian-trace and third-order checkpoints at the selected pilot horizon and the full confirmatory horizon in each stage. Include the three fitted pilot controls. Each evaluation records training-window perturbation widths and Hessian curvature in that stage’s trainable coordinates. This analysis was specified after early development results. [Measurement design](amendments/checkpoint-flatness.md) · [Measured statistics](flatness.md)

The coverage extension also measures every other pilot strength, all hybrid arms and shared trunks, the two initial predictors and both unigram references. A common output-score perturbation is defined for all of them. The numerical diagnostic retains its separate label. [All-model flatness protocol](amendments/all-model-flatness.md)
