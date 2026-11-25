# Flatness at saved checkpoints

Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)

## Registered TinyStories hybrids

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23 | 15.143 | 13.157 | 13.048–13.215 | 12.984–13.368 | 0/96 |
| Fixed late hybrid | 21, 22, 23 | 15.143 | 13.215 | 13.103–13.268 | 13.036–13.411 | 0/96 |
| Hessian trace | 21, 22, 23 | 15.143 | 13.154 | 13.046–13.215 | 12.984–13.366 | 0/96 |
| Stronger trace | 21, 22, 23 | 15.143 | 13.175 | 13.069–13.233 | 13.002–13.387 | 0/96 |
| Cross-seed replay | 22, 23 | 15.198 | 13.133 | 13.047–13.218 | 12.933–13.431 | 0/64 |
| Always-on hybrid | 21, 22, 23 | 15.256 | 13.229 | 13.060–13.334 | 13.085–13.390 | 0/96 |

The seed range and directional spread describe variability. The rays at the limit give measurement coverage. Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)

## Every variant and baseline

Parentheses give measured / planned seeds. A unigram has only the common score-space measurement. [Shared score perturbations](amendments/all-model-flatness.md)

**TinyStories · all model weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | 90.633 (1/1) | 0.43979 (1/1) | 0.921 (1/1) |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.915 (1/1) |
| Ordinary AdamW | 2,097,152 | 0 | 15.579 (1/1) | 0.45329 (1/1) | 0.989 (1/1) |
| Hessian trace (1%) | 2,097,152 | 0 | 15.686 (1/1) | 0.44772 (1/1) | 0.989 (1/1) |
| Third derivative (1%) | 2,097,152 | 0 | 15.640 (1/1) | 0.44739 (1/1) | 0.989 (1/1) |
| Squared Hessian norm (3%) | 2,097,152 | 0 | 15.901 (1/1) | 0.42958 (1/1) | 0.989 (1/1) |
| Randomized gradient signs (1%) | 2,097,152 | 0 | 15.571 (1/1) | 0.4536 (1/1) | 0.989 (1/1) |
| Trace + third derivative (1%) | 2,097,152 | 0 | 15.741 (1/1) | 0.44132 (1/1) | 0.989 (1/1) |
| Ordinary AdamW · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Hessian trace · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Third derivative · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Shared trace checkpoint | 8,388,608 | 21–28 | 15.143 (3/8) | Pending | Pending |
| Curvature-dependent hybrid · hybrid study | 16,777,216 | 21–28 | 13.157 (3/8) | Pending | Pending |
| Fixed late hybrid · hybrid study | 16,777,216 | 21–28 | 13.215 (3/8) | Pending | Pending |
| Hessian trace · hybrid study | 16,777,216 | 21–28 | 13.154 (3/8) | Pending | Pending |
| Stronger trace · hybrid study | 16,777,216 | 21–28 | 13.175 (3/8) | Pending | Pending |
| Cross-seed replay · hybrid study | 16,777,216 | 21–28 | 13.133 (2/8) | Pending | Pending |
| Always-on hybrid · hybrid study | 16,777,216 | 21–28 | 13.229 (3/8) | Pending | Pending |

<details><summary>TinyStories · all model weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 2,097,152 | 0 | 15.898 (1/1) | 0.43612 (1/1) | 0.989 (1/1) |
| Hessian trace (10%) | 2,097,152 | 0 | 16.444 (1/1) | 0.41261 (1/1) | 0.988 (1/1) |
| Third derivative (3%) | 2,097,152 | 0 | 15.777 (1/1) | 0.43692 (1/1) | 0.989 (1/1) |
| Third derivative (10%) | 2,097,152 | 0 | 16.219 (1/1) | 0.41607 (1/1) | 0.988 (1/1) |

</details>

**Pythia-410M · adapter weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | Pending | Pending | Pending |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.915 (1/1) |
| Ordinary AdamW | 65,536 | 0 | 19.784 (1/1) | 1.2868 (1/1) | Pending |
| Hessian trace (1%) | 65,536 | 0 | 19.751 (1/1) | 1.1818 (1/1) | Pending |
| Third derivative (1%) | 65,536 | 0 | 19.922 (1/1) | 0.58227 (1/1) | Pending |
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
| abstracts | control | 0 | Unigram | 0% | N/A | N/A | N/A | N/A | N/A | 0.915 | 0.913–0.924 | 0/32 | 0.993798 | [Score probes](../results/abstracts-control-s00-unigram-r00/score-flatness.json) |
| abstracts | pilot | 0 | Ordinary AdamW | 0% | 19.784 | 19.185–20.320 | 0/32 | 1.28684 | +0.00312322 | Pending | Pending | Pending | Pending | [Weight probes](../results/abstracts-pilot-s00-ce-r00/flatness.json) |
| abstracts | pilot | 0 | Third derivative | 1% | 19.922 | 19.400–20.421 | 0/32 | 0.582266 | +0.00146738 | Pending | Pending | Pending | Pending | [Weight probes](../results/abstracts-pilot-s00-third-r01-fp64/flatness.json) |
| abstracts | pilot | 0 | Hessian trace | 1% | 19.751 | 19.179–20.260 | 0/32 | 1.18181 | +0.00404879 | Pending | Pending | Pending | Pending | [Weight probes](../results/abstracts-pilot-s00-trace-r01-fp64/flatness.json) |
| stories | control | 0 | Initial checkpoint | 0% | 90.633 | 82.412–101.555 | 0/32 | 0.439786 | +0.000336055 | 0.921 | 0.911–0.936 | 0/32 | 0.999976 | [Weight probes](../results/stories-control-s00-initial-r00/flatness.json) · [Score probes](../results/stories-control-s00-initial-r00/score-flatness.json) |
| stories | control | 0 | Unigram | 0% | N/A | N/A | N/A | N/A | N/A | 0.915 | 0.913–0.920 | 0/32 | 0.989727 | [Score probes](../results/stories-control-s00-unigram-r00/score-flatness.json) |
| stories | pilot | 0 | Ordinary AdamW | 0% | 15.579 | 15.297–16.037 | 0/32 | 0.453288 | +0.0036281 | 0.989 | 0.985–0.996 | 0/32 | 0.843296 | [Weight probes](../results/stories-pilot-s00-ce-r00/flatness.json) · [Score probes](../results/stories-pilot-s00-ce-r00/score-flatness.json) |
| stories | pilot | 0 | Trace + third derivative | 1% | 15.741 | 15.504–16.178 | 0/32 | 0.441322 | +0.00350869 | 0.989 | 0.985–0.996 | 0/32 | 0.843297 | [Weight probes](../results/stories-pilot-s00-combined-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-combined-r01/score-flatness.json) |
| stories | pilot | 0 | Squared Hessian norm | 3% | 15.901 | 15.638–16.320 | 0/32 | 0.429575 | +0.00343614 | 0.989 | 0.985–0.996 | 0/32 | 0.843254 | [Weight probes](../results/stories-pilot-s00-hessian_norm-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-hessian_norm-r03/score-flatness.json) |
| stories | pilot | 0 | Randomized gradient signs | 1% | 15.571 | 15.297–16.031 | 0/32 | 0.453605 | +0.00362814 | 0.989 | 0.985–0.996 | 0/32 | 0.84331 | [Weight probes](../results/stories-pilot-s00-sham-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-sham-r01/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 1% | 15.640 | 15.382–16.118 | 0/32 | 0.447394 | +0.00357761 | 0.989 | 0.985–0.996 | 0/32 | 0.843216 | [Weight probes](../results/stories-pilot-s00-third-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r01/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 3% | 15.777 | 15.530–16.252 | 0/32 | 0.436925 | +0.00348104 | 0.989 | 0.985–0.996 | 0/32 | 0.843304 | [Weight probes](../results/stories-pilot-s00-third-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r03/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 10% | 16.219 | 15.805–16.594 | 0/32 | 0.416066 | +0.00332069 | 0.988 | 0.984–0.996 | 0/32 | 0.844224 | [Weight probes](../results/stories-pilot-s00-third-r10/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r10/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 1% | 15.686 | 15.431–16.102 | 0/32 | 0.447721 | +0.00356145 | 0.989 | 0.985–0.996 | 0/32 | 0.843304 | [Weight probes](../results/stories-pilot-s00-trace-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r01/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 3% | 15.898 | 15.584–16.205 | 0/32 | 0.436119 | +0.0034383 | 0.989 | 0.985–0.996 | 0/32 | 0.843489 | [Weight probes](../results/stories-pilot-s00-trace-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r03/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 10% | 16.444 | 15.949–16.644 | 0/32 | 0.412606 | +0.00325958 | 0.988 | 0.984–0.995 | 0/32 | 0.845055 | [Weight probes](../results/stories-pilot-s00-trace-r10/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r10/score-flatness.json) |
