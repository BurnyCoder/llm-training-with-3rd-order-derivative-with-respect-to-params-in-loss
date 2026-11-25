# Flatness at saved checkpoints

Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)

## Registered TinyStories hybrids

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23 | 15.143 | 13.157 | 13.048–13.215 | 12.984–13.368 | 0/96 |
| Fixed late hybrid | 21, 22, 23 | 15.143 | 13.215 | 13.103–13.268 | 13.036–13.411 | 0/96 |
| Hessian trace | 21, 22, 23 | 15.143 | 13.154 | 13.046–13.215 | 12.984–13.366 | 0/96 |
| Stronger trace | 21, 22, 23 | 15.143 | 13.175 | 13.069–13.233 | 13.002–13.387 | 0/96 |
| Cross-seed replay | 22 | 15.403 | 13.218 | One seed | 12.987–13.496 | 0/32 |
| Always-on hybrid | 21, 22, 23 | 15.256 | 13.229 | 13.060–13.334 | 13.085–13.390 | 0/96 |

The seed range and directional spread describe variability. The rays at the limit give measurement coverage. Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)

## Every variant and baseline

Parentheses give measured / planned seeds. A unigram has only the common score-space measurement. [Shared score perturbations](amendments/all-model-flatness.md)

**TinyStories · all model weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | Pending | Pending | Pending |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | Pending |
| Ordinary AdamW | 2,097,152 | 0 | 15.579 (1/1) | 0.45329 (1/1) | Pending |
| Hessian trace (1%) | 2,097,152 | 0 | 15.686 (1/1) | 0.44772 (1/1) | Pending |
| Third derivative (1%) | 2,097,152 | 0 | 15.640 (1/1) | 0.44739 (1/1) | Pending |
| Squared Hessian norm (3%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Randomized gradient signs (1%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Trace + third derivative (1%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Ordinary AdamW · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Hessian trace · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Third derivative · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Shared trace checkpoint | 8,388,608 | 21–28 | 15.143 (3/8) | Pending | Pending |
| Curvature-dependent hybrid · hybrid study | 16,777,216 | 21–28 | 13.157 (3/8) | Pending | Pending |
| Fixed late hybrid · hybrid study | 16,777,216 | 21–28 | 13.215 (3/8) | Pending | Pending |
| Hessian trace · hybrid study | 16,777,216 | 21–28 | 13.154 (3/8) | Pending | Pending |
| Stronger trace · hybrid study | 16,777,216 | 21–28 | 13.175 (3/8) | Pending | Pending |
| Cross-seed replay · hybrid study | 16,777,216 | 21–28 | 13.218 (1/8) | Pending | Pending |
| Always-on hybrid · hybrid study | 16,777,216 | 21–28 | 13.229 (3/8) | Pending | Pending |

<details><summary>TinyStories · all model weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Hessian trace (10%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Third derivative (3%) | 2,097,152 | 0 | Pending | Pending | Pending |
| Third derivative (10%) | 2,097,152 | 0 | Pending | Pending | Pending |

</details>

**Pythia-410M · adapter weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | Pending | Pending | Pending |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | Pending |
| Ordinary AdamW | 65,536 | 0 | 19.784 (1/1) | 1.2868 (1/1) | Pending |
| Hessian trace (1%) | 65,536 | 0 | 19.751 (1/1) | 1.1818 (1/1) | Pending |
| Third derivative (1%) | 65,536 | 0 | Pending | Pending | Pending |
| Squared Hessian norm (3%) | 65,536 | 0 | Pending | Pending | Pending |
| Randomized gradient signs (1%) | 65,536 | 0 | Pending | Pending | Pending |
| Trace + third derivative (1%) | 65,536 | 0 | Pending | Pending | Pending |
| Ordinary AdamW · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |
| Hessian trace · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |
| Third derivative · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |

<details><summary>Pythia-410M · adapter weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 65,536 | 0 | Pending | Pending | Pending |
| Hessian trace (10%) | 65,536 | 0 | Pending | Pending | Pending |
| Third derivative (3%) | 65,536 | 0 | Pending | Pending | Pending |
| Third derivative (10%) | 65,536 | 0 | Pending | Pending | Pending |
| Third derivative (3%) · excluded precision diagnostic | 65,536 | 0 | Pending | Pending | Pending |

</details>

## Per-run checkpoint measurements

| Stage | Horizon | Seed | Arm | Strength | Weight width ↑ | Weight middle 50% | Weight rays at limit | RMS curvature ↓ | Signed trace / parameter | Score width ↑ | Score middle 50% | Score rays at limit | Mean score curvature | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abstracts | pilot | 0 | Ordinary AdamW | 0% | 19.784 | 19.185–20.320 | 0/32 | 1.28684 | +0.00312322 | Pending | Pending | Pending | Pending | [Weight probes](../results/abstracts-pilot-s00-ce-r00/flatness.json) |
| abstracts | pilot | 0 | Hessian trace | 1% | 19.751 | 19.179–20.260 | 0/32 | 1.18181 | +0.00404879 | Pending | Pending | Pending | Pending | [Weight probes](../results/abstracts-pilot-s00-trace-r01-fp64/flatness.json) |
| stories | pilot | 0 | Ordinary AdamW | 0% | 15.579 | 15.297–16.037 | 0/32 | 0.453288 | +0.0036281 | Pending | Pending | Pending | Pending | [Weight probes](../results/stories-pilot-s00-ce-r00/flatness.json) |
| stories | pilot | 0 | Third derivative | 1% | 15.640 | 15.382–16.118 | 0/32 | 0.447394 | +0.00357761 | Pending | Pending | Pending | Pending | [Weight probes](../results/stories-pilot-s00-third-r01/flatness.json) |
| stories | pilot | 0 | Hessian trace | 1% | 15.686 | 15.431–16.102 | 0/32 | 0.447721 | +0.00356145 | Pending | Pending | Pending | Pending | [Weight probes](../results/stories-pilot-s00-trace-r01/flatness.json) |
