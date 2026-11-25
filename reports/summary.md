# Study summary

Recorded 58 runs, including 58 with a completed summary.

**TinyStories.** Awaiting paired test results (1 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

TinyStories hybrid follow-up: 23 of 48 full runs and 5 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements. [Hybrid outcomes](hybrid/results.md)

[Interactive explorer](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/) · [Per-run ledger](experiments/experiments.md) · [Final seed sensitivity](seed-sensitivity.md) · [Preregistration](preregistration.md) · [Paper](paper.pdf)

## Development observations

**TinyStories development pilot.** At 2,097,152 training targets, the third-order run recorded 0.00004 nats per target token lower against Ordinary AdamW, 0.00024 nats per target token lower against Trace + third derivative, 0.00175 nats per target token lower against Squared Hessian norm, 0.00032 nats per target token lower against Randomized gradient signs, 0.00034 nats per target token lower against Hessian trace. These are single-seed descriptions using strengths selected on development.

**Research abstracts development pilot.** At 65,536 training targets, the third-order run recorded 0.00030 nats per target token higher against Ordinary AdamW, 0.00003 nats per target token lower against Trace + third derivative, 0.00034 nats per target token higher against Squared Hessian norm, 0.00005 nats per target token higher against Randomized gradient signs, 0.00027 nats per target token higher against Hessian trace. These are single-seed descriptions using strengths selected on development.

## Measured scores

| Stage | Phase | Method | Ratio | Tokens/run | Runs | Median dev NLL | Median dev PPL | Median test NLL | Median test PPL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | confirm | Ordinary AdamW | 0.000 | 524,288 | 1 | 3.0368 | 20.8387 | — | — |
| Research abstracts | confirm | Third derivative | 0.010 | 524,288 | 1 | 3.0368 | 20.8375 | — | — |
| Research abstracts | control | Initial checkpoint | 0.000 | 0 | 1 | 3.2517 | 25.8335 | — | — |
| Research abstracts | control | Unigram | 0.000 | 0 | 1 | 7.3306 | 1,526.3141 | — | — |
| Research abstracts | pilot | Ordinary AdamW | 0.000 | 65,536 | 1 | 3.1139 | 22.5097 | — | — |
| Research abstracts | pilot | Trace + third derivative | 0.010 | 65,536 | 1 | 3.1143 | 22.5172 | — | — |
| Research abstracts | pilot | Squared Hessian norm | 0.030 | 65,536 | 1 | 3.1139 | 22.5088 | — | — |
| Research abstracts | pilot | Randomized gradient signs | 0.010 | 65,536 | 1 | 3.1142 | 22.5153 | — | — |
| Research abstracts | pilot | Third derivative | 0.010 | 65,536 | 1 | 3.1142 | 22.5165 | — | — |
| Research abstracts | diagnostic | Third derivative | 0.030 | 65,536 | 1 | 3.1168 | 22.5739 | — | — |
| Research abstracts | pilot | Third derivative | 0.030 | 65,536 | 1 | 3.1149 | 22.5303 | — | — |
| Research abstracts | pilot | Third derivative | 0.100 | 65,536 | 1 | 3.1163 | 22.5630 | — | — |
| Research abstracts | pilot | Hessian trace | 0.010 | 65,536 | 1 | 3.1140 | 22.5103 | — | — |
| Research abstracts | pilot | Hessian trace | 0.030 | 65,536 | 1 | 3.1141 | 22.5136 | — | — |
| Research abstracts | pilot | Hessian trace | 0.100 | 65,536 | 1 | 3.1143 | 22.5172 | — | — |
| TinyStories | branch | Shared trace checkpoint | 0.010 | 8,388,608 | 5 | 2.7577 | 15.7633 | — | — |
| TinyStories | confirm | Ordinary AdamW | 0.000 | 16,777,216 | 1 | 2.5477 | 12.7779 | — | — |
| TinyStories | confirm | Third derivative | 0.010 | 16,777,216 | 1 | 2.5477 | 12.7779 | — | — |
| TinyStories | confirm | Hessian trace | 0.010 | 16,777,216 | 1 | 2.5480 | 12.7811 | — | — |
| TinyStories | control | Initial checkpoint | 0.000 | 0 | 1 | 8.3437 | 4,203.5319 | — | — |
| TinyStories | control | Unigram | 0.000 | 0 | 1 | 6.0036 | 404.8654 | — | — |
| TinyStories | hybrid | Curvature-dependent hybrid | 0.010 | 16,777,216 | 4 | 2.5461 | 12.7573 | — | — |
| TinyStories | hybrid | Always-on hybrid | 0.010 | 16,777,216 | 4 | 2.5459 | 12.7553 | — | — |
| TinyStories | hybrid | Fixed late hybrid | 0.010 | 16,777,216 | 4 | 2.5463 | 12.7596 | — | — |
| TinyStories | hybrid | Stronger trace | 0.010 | 16,777,216 | 4 | 2.5462 | 12.7585 | — | — |
| TinyStories | hybrid | Hessian trace | 0.010 | 16,777,216 | 4 | 2.5461 | 12.7573 | — | — |
| TinyStories | hybrid | Cross-seed replay | 0.010 | 16,777,216 | 3 | 2.5463 | 12.7599 | — | — |
| TinyStories | pilot | Ordinary AdamW | 0.000 | 2,097,152 | 1 | 3.8770 | 48.2780 | — | — |
| TinyStories | pilot | Trace + third derivative | 0.010 | 2,097,152 | 1 | 3.8772 | 48.2875 | — | — |
| TinyStories | pilot | Squared Hessian norm | 0.030 | 2,097,152 | 1 | 3.8787 | 48.3603 | — | — |
| TinyStories | pilot | Randomized gradient signs | 0.010 | 2,097,152 | 1 | 3.8773 | 48.2914 | — | — |
| TinyStories | pilot | Third derivative | 0.010 | 2,097,152 | 1 | 3.8769 | 48.2758 | — | — |
| TinyStories | pilot | Third derivative | 0.030 | 2,097,152 | 1 | 3.8778 | 48.3167 | — | — |
| TinyStories | pilot | Third derivative | 0.100 | 2,097,152 | 1 | 3.8827 | 48.5556 | — | — |
| TinyStories | pilot | Hessian trace | 0.010 | 2,097,152 | 1 | 3.8773 | 48.2921 | — | — |
| TinyStories | pilot | Hessian trace | 0.030 | 2,097,152 | 1 | 3.8802 | 48.4360 | — | — |
| TinyStories | pilot | Hessian trace | 0.100 | 2,097,152 | 1 | 3.8979 | 49.2988 | — | — |

## Paired evidence

### TinyStories at equal training time

| Seed | Common cutoff (s) | Method | Recorded checkpoint (s) | Training tokens | Dev NLL |
| --- | --- | --- | --- | --- | --- |
| 1 | 148.2 | Ordinary AdamW | 148.2 | 16,777,216 | 2.53821 |
| 1 | 148.2 | Hessian trace | 147.7 | 9,961,472 | 2.68115 |
| 1 | 148.2 | Third derivative | 146.2 | 5,767,168 | 2.95676 |

![Computation graph](../docs/figures/architecture.png)

![Development trajectories](../docs/figures/curves.png)
