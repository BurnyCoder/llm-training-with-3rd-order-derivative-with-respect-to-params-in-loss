# Planned runs

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
