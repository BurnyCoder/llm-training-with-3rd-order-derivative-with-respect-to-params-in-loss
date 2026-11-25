# Study summary

Recorded 51 runs, including 50 with a completed summary.

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

TinyStories hybrid follow-up: 23 of 48 full runs and 5 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements. [Hybrid outcomes](hybrid/results.md)

[Interactive explorer](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/) · [Per-run ledger](experiments/experiments.md) · [Final seed sensitivity](seed-sensitivity.md) · [Preregistration](preregistration.md) · [Paper](paper.pdf)

## Development observations

**TinyStories development pilot.** At 2,097,152 training targets, the third-order run recorded 0.00004 nats per target token lower against Ordinary AdamW, 0.00024 nats per target token lower against Trace + third derivative, 0.00175 nats per target token lower against Squared Hessian norm, 0.00032 nats per target token lower against Randomized gradient signs, 0.00034 nats per target token lower against Hessian trace. These are single-seed descriptions using strengths selected on development.

**Research abstracts development pilot.** At 65,536 training targets, the third-order run recorded 0.00030 nats per target token higher against Ordinary AdamW, 0.00027 nats per target token higher against Hessian trace. These are single-seed descriptions using strengths selected on development.

## Measured scores

| Stage | Phase | Method | Ratio | Tokens/run | Runs | Median dev NLL | Median test NLL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | control | Initial checkpoint | 0.000 | 0 | 1 | 3.2517 | — |
| Research abstracts | control | Unigram | 0.000 | 0 | 1 | 7.3306 | — |
| Research abstracts | pilot | Ordinary AdamW | 0.000 | 65,536 | 1 | 3.1139 | — |
| Research abstracts | pilot | Third derivative | 0.010 | 65,536 | 1 | 3.1142 | — |
| Research abstracts | diagnostic | Third derivative | 0.030 | 65,536 | 1 | 3.1168 | — |
| Research abstracts | pilot | Third derivative | 0.030 | 65,536 | 1 | 3.1149 | — |
| Research abstracts | pilot | Third derivative | 0.100 | 65,536 | 1 | 3.1163 | — |
| Research abstracts | pilot | Hessian trace | 0.010 | 65,536 | 1 | 3.1140 | — |
| Research abstracts | pilot | Hessian trace | 0.030 | 65,536 | 1 | 3.1141 | — |
| Research abstracts | pilot | Hessian trace | 0.100 | 65,536 | 1 | 3.1143 | — |
| TinyStories | branch | Shared trace checkpoint | 0.010 | 8,388,608 | 5 | 2.7577 | — |
| TinyStories | control | Initial checkpoint | 0.000 | 0 | 1 | 8.3437 | — |
| TinyStories | control | Unigram | 0.000 | 0 | 1 | 6.0036 | — |
| TinyStories | hybrid | Curvature-dependent hybrid | 0.010 | 16,777,216 | 4 | 2.5461 | — |
| TinyStories | hybrid | Always-on hybrid | 0.010 | 16,777,216 | 4 | 2.5459 | — |
| TinyStories | hybrid | Fixed late hybrid | 0.010 | 16,777,216 | 4 | 2.5463 | — |
| TinyStories | hybrid | Stronger trace | 0.010 | 16,777,216 | 4 | 2.5462 | — |
| TinyStories | hybrid | Hessian trace | 0.010 | 16,777,216 | 4 | 2.5461 | — |
| TinyStories | hybrid | Cross-seed replay | 0.010 | 16,777,216 | 3 | 2.5463 | — |
| TinyStories | pilot | Ordinary AdamW | 0.000 | 2,097,152 | 1 | 3.8770 | — |
| TinyStories | pilot | Trace + third derivative | 0.010 | 2,097,152 | 1 | 3.8772 | — |
| TinyStories | pilot | Squared Hessian norm | 0.030 | 2,097,152 | 1 | 3.8787 | — |
| TinyStories | pilot | Randomized gradient signs | 0.010 | 2,097,152 | 1 | 3.8773 | — |
| TinyStories | pilot | Third derivative | 0.010 | 2,097,152 | 1 | 3.8769 | — |
| TinyStories | pilot | Third derivative | 0.030 | 2,097,152 | 1 | 3.8778 | — |
| TinyStories | pilot | Third derivative | 0.100 | 2,097,152 | 1 | 3.8827 | — |
| TinyStories | pilot | Hessian trace | 0.010 | 2,097,152 | 1 | 3.8773 | — |
| TinyStories | pilot | Hessian trace | 0.030 | 2,097,152 | 1 | 3.8802 | — |
| TinyStories | pilot | Hessian trace | 0.100 | 2,097,152 | 1 | 3.8979 | — |

![Computation graph](../docs/figures/architecture.png)

![Development trajectories](../docs/figures/curves.png)
