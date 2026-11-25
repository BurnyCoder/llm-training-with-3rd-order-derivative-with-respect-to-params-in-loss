# Flatness at saved checkpoints

Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)

## Registered TinyStories hybrids

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23, 24 | 15.172 | 13.103 | 13.001–13.215 | 12.933–13.331 | 0/128 |
| Fixed late hybrid | 21, 22, 23, 24 | 15.172 | 13.159 | 13.056–13.268 | 12.984–13.380 | 0/128 |
| Hessian trace | 21, 22, 23, 24 | 15.172 | 13.100 | 13.001–13.215 | 12.932–13.330 | 0/128 |
| Stronger trace | 21, 22, 23, 24 | 15.172 | 13.122 | 13.023–13.233 | 12.951–13.351 | 0/128 |
| Cross-seed replay | 22, 23 | 15.198 | 13.133 | 13.047–13.218 | 12.933–13.431 | 0/64 |
| Always-on hybrid | 21, 22, 23 | 15.256 | 13.229 | 13.060–13.334 | 13.085–13.390 | 0/96 |

The seed range and directional spread describe variability. The rays at the limit give measurement coverage. Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)

## Every variant and baseline

Parentheses give measured / planned seeds. A unigram has only the common score-space measurement. [Shared score perturbations](amendments/all-model-flatness.md)

**TinyStories · all model weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | 90.633 (1/1) | 0.43979 (1/1) | 0.9214 (1/1) |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.9152 (1/1) |
| Ordinary AdamW | 2,097,152 | 0 | 15.579 (1/1) | 0.45329 (1/1) | 0.9891 (1/1) |
| Hessian trace (1%) | 2,097,152 | 0 | 15.686 (1/1) | 0.44772 (1/1) | 0.9891 (1/1) |
| Third derivative (1%) | 2,097,152 | 0 | 15.640 (1/1) | 0.44739 (1/1) | 0.9891 (1/1) |
| Squared Hessian norm (3%) | 2,097,152 | 0 | 15.901 (1/1) | 0.42958 (1/1) | 0.9890 (1/1) |
| Randomized gradient signs (1%) | 2,097,152 | 0 | 15.571 (1/1) | 0.4536 (1/1) | 0.9892 (1/1) |
| Trace + third derivative (1%) | 2,097,152 | 0 | 15.741 (1/1) | 0.44132 (1/1) | 0.9891 (1/1) |
| Ordinary AdamW · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Hessian trace · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Third derivative · confirmation | 16,777,216 | 1–8 | Pending | Pending | Pending |
| Shared trace checkpoint | 8,388,608 | 21–28 | 15.172 (4/8) | 0.44445 (4/8) | 1.0618 (4/8) |
| Curvature-dependent hybrid · hybrid study | 16,777,216 | 21–28 | 13.103 (4/8) | 0.57782 (4/8) | 1.0824 (4/8) |
| Fixed late hybrid · hybrid study | 16,777,216 | 21–28 | 13.159 (4/8) | 0.57064 (4/8) | 1.0822 (4/8) |
| Hessian trace · hybrid study | 16,777,216 | 21–28 | 13.100 (4/8) | 0.57802 (4/8) | 1.0824 (4/8) |
| Stronger trace · hybrid study | 16,777,216 | 21–28 | 13.122 (4/8) | 0.57648 (4/8) | 1.0824 (4/8) |
| Cross-seed replay · hybrid study | 16,777,216 | 21–28 | 13.133 (2/8) | 0.5891 (2/8) | 1.0824 (2/8) |
| Always-on hybrid · hybrid study | 16,777,216 | 21–28 | 13.229 (3/8) | 0.57089 (3/8) | 1.0821 (3/8) |

<details><summary>TinyStories · all model weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 2,097,152 | 0 | 15.898 (1/1) | 0.43612 (1/1) | 0.9889 (1/1) |
| Hessian trace (10%) | 2,097,152 | 0 | 16.444 (1/1) | 0.41261 (1/1) | 0.9878 (1/1) |
| Third derivative (3%) | 2,097,152 | 0 | 15.777 (1/1) | 0.43692 (1/1) | 0.9891 (1/1) |
| Third derivative (10%) | 2,097,152 | 0 | 16.219 (1/1) | 0.41607 (1/1) | 0.9884 (1/1) |

</details>

**Pythia-410M · adapter weights**

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Initial checkpoint | 0 | 0 | 21.890 (1/1) | 0.69058 (1/1) | 1.0859 (1/1) |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.9150 (1/1) |
| Ordinary AdamW | 65,536 | 0 | 19.784 (1/1) | 1.2868 (1/1) | 1.0930 (1/1) |
| Hessian trace (1%) | 65,536 | 0 | 19.751 (1/1) | 1.1818 (1/1) | 1.0929 (1/1) |
| Third derivative (1%) | 65,536 | 0 | 19.922 (1/1) | 0.58227 (1/1) | 1.0928 (1/1) |
| Squared Hessian norm (3%) | 65,536 | 0 | Pending | Pending | Pending |
| Randomized gradient signs (1%) | 65,536 | 0 | Pending | Pending | Pending |
| Trace + third derivative (1%) | 65,536 | 0 | Pending | Pending | Pending |
| Ordinary AdamW · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |
| Hessian trace · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |
| Third derivative · confirmation | 524,288 | 1–8 | Pending | Pending | Pending |

<details><summary>Pythia-410M · adapter weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 65,536 | 0 | 19.775 (1/1) | 0.58335 (1/1) | 1.0929 (1/1) |
| Hessian trace (10%) | 65,536 | 0 | 19.856 (1/1) | 0.77214 (1/1) | 1.0930 (1/1) |
| Third derivative (3%) | 65,536 | 0 | 19.968 (1/1) | 0.56999 (1/1) | 1.0927 (1/1) |
| Third derivative (10%) | 65,536 | 0 | 19.997 (1/1) | 0.56095 (1/1) | 1.0926 (1/1) |
| Third derivative (3%) · excluded precision diagnostic | 65,536 | 0 | 19.885 (1/1) | 0.58797 (1/1) | 1.0932 (1/1) |

</details>

## Per-run checkpoint measurements

| Stage | Horizon | Seed | Arm | Strength | Weight width ↑ | Weight middle 50% | Weight rays at limit | RMS curvature ↓ | Signed trace / parameter | Score width ↑<br>Search bracket | Score middle 50% | Score rays at limit | Mean score curvature | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abstracts | control | 0 | Initial checkpoint | 0% | 21.890 | 21.676–22.687 | 0/32 | 0.690576 | +0.0011406 | 1.0859<br>[1.08575, 1.08597] | 1.081–1.095 | 0/32 | 0.700479 | [Weight probes](../results/abstracts-control-s00-initial-r00/flatness.json) · [Score probes](../results/abstracts-control-s00-initial-r00/score-flatness.json) |
| abstracts | control | 0 | Unigram | 0% | N/A | N/A | N/A | N/A | N/A | 0.9150<br>[0.91494, 0.91511] | 0.913–0.924 | 0/32 | 0.993798 | [Score probes](../results/abstracts-control-s00-unigram-r00/score-flatness.json) |
| abstracts | pilot | 0 | Ordinary AdamW | 0% | 19.784 | 19.185–20.320 | 0/32 | 1.28684 | +0.00312322 | 1.0930<br>[1.09295, 1.09314] | 1.090–1.100 | 0/32 | 0.69199 | [Weight probes](../results/abstracts-pilot-s00-ce-r00/flatness.json) · [Score probes](../results/abstracts-pilot-s00-ce-r00/score-flatness.json) |
| abstracts | pilot | 0 | Third derivative | 1% | 19.922 | 19.400–20.421 | 0/32 | 0.582266 | +0.00146738 | 1.0928<br>[1.09274, 1.09293] | 1.090–1.100 | 0/32 | 0.692147 | [Weight probes](../results/abstracts-pilot-s00-third-r01-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-third-r01-fp64/score-flatness.json) |
| abstracts | diagnostic | 0 | Third derivative | 3% | 19.885 | 19.294–20.399 | 0/32 | 0.587972 | +0.00187752 | 1.0932<br>[1.09307, 1.09327] | 1.089–1.100 | 0/32 | 0.691916 | [Weight probes](../results/abstracts-pilot-s00-third-r03/flatness.json) · [Score probes](../results/abstracts-pilot-s00-third-r03/score-flatness.json) |
| abstracts | pilot | 0 | Third derivative | 3% | 19.968 | 19.416–20.312 | 0/32 | 0.56999 | +0.00201241 | 1.0927<br>[1.09262, 1.09281] | 1.089–1.100 | 0/32 | 0.692521 | [Weight probes](../results/abstracts-pilot-s00-third-r03-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-third-r03-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Third derivative | 10% | 19.997 | 19.438–20.318 | 0/32 | 0.560945 | +0.00186258 | 1.0926<br>[1.09246, 1.09266] | 1.089–1.099 | 0/32 | 0.692892 | [Weight probes](../results/abstracts-pilot-s00-third-r10-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-third-r10-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Hessian trace | 1% | 19.751 | 19.179–20.260 | 0/32 | 1.18181 | +0.00404879 | 1.0929<br>[1.09283, 1.09302] | 1.090–1.100 | 0/32 | 0.692079 | [Weight probes](../results/abstracts-pilot-s00-trace-r01-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-trace-r01-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Hessian trace | 3% | 19.775 | 19.248–20.317 | 0/32 | 0.583348 | +0.00137939 | 1.0929<br>[1.09277, 1.09296] | 1.090–1.100 | 0/32 | 0.692076 | [Weight probes](../results/abstracts-pilot-s00-trace-r03-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-trace-r03-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Hessian trace | 10% | 19.856 | 19.390–20.556 | 0/32 | 0.772137 | +0.00219866 | 1.0930<br>[1.09286, 1.09305] | 1.089–1.100 | 0/32 | 0.69218 | [Weight probes](../results/abstracts-pilot-s00-trace-r10-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-trace-r10-fp64/score-flatness.json) |
| stories | branch | 21 | Shared trace checkpoint | 1% | 15.143 | 14.868–15.371 | 0/32 | 0.449892 | +0.00343864 | 1.0624<br>[1.06225, 1.06247] | 1.056–1.073 | 0/32 | 0.72934 | [Weight probes](../results/stories-branch-s21-trunk-r01/flatness.json) · [Score probes](../results/stories-branch-s21-trunk-r01/score-flatness.json) |
| stories | branch | 22 | Shared trace checkpoint | 1% | 15.403 | 15.160–15.567 | 0/32 | 0.420382 | +0.00325 | 1.0612<br>[1.06109, 1.06135] | 1.057–1.072 | 0/32 | 0.727319 | [Weight probes](../results/stories-branch-s22-trunk-r01/flatness.json) · [Score probes](../results/stories-branch-s22-trunk-r01/score-flatness.json) |
| stories | branch | 23 | Shared trace checkpoint | 1% | 14.994 | 14.768–15.394 | 0/32 | 0.465344 | +0.00342644 | 1.0611<br>[1.06100, 1.06119] | 1.056–1.071 | 0/32 | 0.731595 | [Weight probes](../results/stories-branch-s23-trunk-r01/flatness.json) · [Score probes](../results/stories-branch-s23-trunk-r01/score-flatness.json) |
| stories | branch | 24 | Shared trace checkpoint | 1% | 15.201 | 14.866–15.438 | 0/32 | 0.439013 | +0.00303131 | 1.0627<br>[1.06259, 1.06281] | 1.058–1.071 | 0/32 | 0.726889 | [Weight probes](../results/stories-branch-s24-trunk-r01/flatness.json) · [Score probes](../results/stories-branch-s24-trunk-r01/score-flatness.json) |
| stories | control | 0 | Initial checkpoint | 0% | 90.633 | 82.412–101.555 | 0/32 | 0.439786 | +0.000336055 | 0.9214<br>[0.92129, 0.92148] | 0.911–0.936 | 0/32 | 0.999976 | [Weight probes](../results/stories-control-s00-initial-r00/flatness.json) · [Score probes](../results/stories-control-s00-initial-r00/score-flatness.json) |
| stories | control | 0 | Unigram | 0% | N/A | N/A | N/A | N/A | N/A | 0.9152<br>[0.91510, 0.91526] | 0.913–0.920 | 0/32 | 0.989727 | [Score probes](../results/stories-control-s00-unigram-r00/score-flatness.json) |
| stories | hybrid | 21 | Curvature-dependent hybrid | 1% | 13.157 | 12.991–13.236 | 0/32 | 0.585004 | +0.00424671 | 1.0836<br>[1.08349, 1.08375] | 1.076–1.095 | 0/32 | 0.699362 | [Weight probes](../results/stories-hybrid-s21-adaptive-r01/flatness.json) · [Score probes](../results/stories-hybrid-s21-adaptive-r01/score-flatness.json) |
| stories | hybrid | 21 | Always-on hybrid | 1% | 13.229 | 13.097–13.390 | 0/32 | 0.57089 | +0.0042312 | 1.0833<br>[1.08322, 1.08344] | 1.076–1.095 | 0/32 | 0.699547 | [Weight probes](../results/stories-hybrid-s21-always-r01/flatness.json) · [Score probes](../results/stories-hybrid-s21-always-r01/score-flatness.json) |
| stories | hybrid | 21 | Fixed late hybrid | 1% | 13.215 | 13.049–13.292 | 0/32 | 0.577598 | +0.00419991 | 1.0833<br>[1.08319, 1.08344] | 1.076–1.095 | 0/32 | 0.699658 | [Weight probes](../results/stories-hybrid-s21-late-r01/flatness.json) · [Score probes](../results/stories-hybrid-s21-late-r01/score-flatness.json) |
| stories | hybrid | 21 | Stronger trace | 1% | 13.175 | 13.006–13.257 | 0/32 | 0.58362 | +0.00423557 | 1.0836<br>[1.08349, 1.08375] | 1.077–1.095 | 0/32 | 0.699349 | [Weight probes](../results/stories-hybrid-s21-strong-r01/flatness.json) · [Score probes](../results/stories-hybrid-s21-strong-r01/score-flatness.json) |
| stories | hybrid | 21 | Hessian trace | 1% | 13.154 | 12.988–13.233 | 0/32 | 0.585403 | +0.00424916 | 1.0836<br>[1.08349, 1.08375] | 1.077–1.095 | 0/32 | 0.699347 | [Weight probes](../results/stories-hybrid-s21-trace-r01/flatness.json) · [Score probes](../results/stories-hybrid-s21-trace-r01/score-flatness.json) |
| stories | hybrid | 22 | Curvature-dependent hybrid | 1% | 13.215 | 12.984–13.494 | 0/32 | 0.570141 | +0.0045186 | 1.0824<br>[1.08224, 1.08246] | 1.076–1.095 | 0/32 | 0.699377 | [Weight probes](../results/stories-hybrid-s22-adaptive-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-adaptive-r01/score-flatness.json) |
| stories | hybrid | 22 | Always-on hybrid | 1% | 13.334 | 13.085–13.553 | 0/32 | 0.559409 | +0.00449892 | 1.0820<br>[1.08193, 1.08216] | 1.076–1.094 | 0/32 | 0.699753 | [Weight probes](../results/stories-hybrid-s22-always-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-always-r01/score-flatness.json) |
| stories | hybrid | 22 | Fixed late hybrid | 1% | 13.268 | 13.036–13.544 | 0/32 | 0.563692 | +0.00448537 | 1.0822<br>[1.08206, 1.08228] | 1.076–1.094 | 0/32 | 0.699535 | [Weight probes](../results/stories-hybrid-s22-late-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-late-r01/score-flatness.json) |
| stories | hybrid | 22 | Cross-seed replay | 1% | 13.218 | 12.987–13.496 | 0/32 | 0.569831 | +0.00451696 | 1.0824<br>[1.08224, 1.08246] | 1.076–1.095 | 0/32 | 0.699382 | [Weight probes](../results/stories-hybrid-s22-replay-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-replay-r01/score-flatness.json) |
| stories | hybrid | 22 | Stronger trace | 1% | 13.233 | 13.002–13.513 | 0/32 | 0.568831 | +0.00450677 | 1.0823<br>[1.08218, 1.08240] | 1.076–1.095 | 0/32 | 0.69936 | [Weight probes](../results/stories-hybrid-s22-strong-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-strong-r01/score-flatness.json) |
| stories | hybrid | 22 | Hessian trace | 1% | 13.215 | 12.984–13.494 | 0/32 | 0.570175 | +0.00451878 | 1.0824<br>[1.08224, 1.08246] | 1.076–1.095 | 0/32 | 0.699377 | [Weight probes](../results/stories-hybrid-s22-trace-r01/flatness.json) · [Score probes](../results/stories-hybrid-s22-trace-r01/score-flatness.json) |
| stories | hybrid | 23 | Curvature-dependent hybrid | 1% | 13.048 | 12.882–13.368 | 0/32 | 0.608105 | +0.00456449 | 1.0825<br>[1.08239, 1.08265] | 1.078–1.092 | 0/32 | 0.700773 | [Weight probes](../results/stories-hybrid-s23-adaptive-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-adaptive-r01/score-flatness.json) |
| stories | hybrid | 23 | Always-on hybrid | 1% | 13.060 | 12.958–13.343 | 0/32 | 0.60123 | +0.00467488 | 1.0821<br>[1.08197, 1.08222] | 1.078–1.092 | 0/32 | 0.700952 | [Weight probes](../results/stories-hybrid-s23-always-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-always-r01/score-flatness.json) |
| stories | hybrid | 23 | Fixed late hybrid | 1% | 13.103 | 12.933–13.411 | 0/32 | 0.600943 | +0.00452572 | 1.0823<br>[1.08215, 1.08240] | 1.077–1.092 | 0/32 | 0.701011 | [Weight probes](../results/stories-hybrid-s23-late-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-late-r01/score-flatness.json) |
| stories | hybrid | 23 | Cross-seed replay | 1% | 13.047 | 12.880–13.366 | 0/32 | 0.608368 | +0.0045658 | 1.0825<br>[1.08239, 1.08265] | 1.078–1.092 | 0/32 | 0.700766 | [Weight probes](../results/stories-hybrid-s23-replay-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-replay-r01/score-flatness.json) |
| stories | hybrid | 23 | Stronger trace | 1% | 13.069 | 12.901–13.387 | 0/32 | 0.606667 | +0.00454891 | 1.0826<br>[1.08245, 1.08271] | 1.078–1.092 | 0/32 | 0.700704 | [Weight probes](../results/stories-hybrid-s23-strong-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-strong-r01/score-flatness.json) |
| stories | hybrid | 23 | Hessian trace | 1% | 13.046 | 12.880–13.366 | 0/32 | 0.608409 | +0.00456602 | 1.0825<br>[1.08239, 1.08265] | 1.078–1.092 | 0/32 | 0.700765 | [Weight probes](../results/stories-hybrid-s23-trace-r01/flatness.json) · [Score probes](../results/stories-hybrid-s23-trace-r01/score-flatness.json) |
| stories | hybrid | 24 | Curvature-dependent hybrid | 1% | 13.001 | 12.639–13.294 | 0/32 | 0.570633 | +0.00455431 | 1.0813<br>[1.08123, 1.08146] | 1.075–1.092 | 0/32 | 0.703527 | [Weight probes](../results/stories-hybrid-s24-adaptive-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-adaptive-r01/score-flatness.json) |
| stories | hybrid | 24 | Fixed late hybrid | 1% | 13.056 | 12.700–13.349 | 0/32 | 0.562815 | +0.00452056 | 1.0811<br>[1.08096, 1.08118] | 1.075–1.091 | 0/32 | 0.703809 | [Weight probes](../results/stories-hybrid-s24-late-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-late-r01/score-flatness.json) |
| stories | hybrid | 24 | Stronger trace | 1% | 13.023 | 12.660–13.315 | 0/32 | 0.569331 | +0.00454192 | 1.0814<br>[1.08126, 1.08149] | 1.075–1.092 | 0/32 | 0.703498 | [Weight probes](../results/stories-hybrid-s24-strong-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-strong-r01/score-flatness.json) |
| stories | hybrid | 24 | Hessian trace | 1% | 13.001 | 12.639–13.294 | 0/32 | 0.570644 | +0.00455437 | 1.0813<br>[1.08123, 1.08146] | 1.075–1.092 | 0/32 | 0.703527 | [Weight probes](../results/stories-hybrid-s24-trace-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-trace-r01/score-flatness.json) |
| stories | pilot | 0 | Ordinary AdamW | 0% | 15.579 | 15.297–16.037 | 0/32 | 0.453288 | +0.0036281 | 0.9891<br>[0.98904, 0.98923] | 0.985–0.996 | 0/32 | 0.843296 | [Weight probes](../results/stories-pilot-s00-ce-r00/flatness.json) · [Score probes](../results/stories-pilot-s00-ce-r00/score-flatness.json) |
| stories | pilot | 0 | Trace + third derivative | 1% | 15.741 | 15.504–16.178 | 0/32 | 0.441322 | +0.00350869 | 0.9891<br>[0.98898, 0.98917] | 0.985–0.996 | 0/32 | 0.843297 | [Weight probes](../results/stories-pilot-s00-combined-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-combined-r01/score-flatness.json) |
| stories | pilot | 0 | Squared Hessian norm | 3% | 15.901 | 15.638–16.320 | 0/32 | 0.429575 | +0.00343614 | 0.9890<br>[0.98889, 0.98908] | 0.985–0.996 | 0/32 | 0.843254 | [Weight probes](../results/stories-pilot-s00-hessian_norm-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-hessian_norm-r03/score-flatness.json) |
| stories | pilot | 0 | Randomized gradient signs | 1% | 15.571 | 15.297–16.031 | 0/32 | 0.453605 | +0.00362814 | 0.9892<br>[0.98907, 0.98926] | 0.985–0.996 | 0/32 | 0.84331 | [Weight probes](../results/stories-pilot-s00-sham-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-sham-r01/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 1% | 15.640 | 15.382–16.118 | 0/32 | 0.447394 | +0.00357761 | 0.9891<br>[0.98904, 0.98923] | 0.985–0.996 | 0/32 | 0.843216 | [Weight probes](../results/stories-pilot-s00-third-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r01/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 3% | 15.777 | 15.530–16.252 | 0/32 | 0.436925 | +0.00348104 | 0.9891<br>[0.98901, 0.98920] | 0.985–0.996 | 0/32 | 0.843304 | [Weight probes](../results/stories-pilot-s00-third-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r03/score-flatness.json) |
| stories | pilot | 0 | Third derivative | 10% | 16.219 | 15.805–16.594 | 0/32 | 0.416066 | +0.00332069 | 0.9884<br>[0.98828, 0.98847] | 0.984–0.996 | 0/32 | 0.844224 | [Weight probes](../results/stories-pilot-s00-third-r10/flatness.json) · [Score probes](../results/stories-pilot-s00-third-r10/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 1% | 15.686 | 15.431–16.102 | 0/32 | 0.447721 | +0.00356145 | 0.9891<br>[0.98901, 0.98920] | 0.985–0.996 | 0/32 | 0.843304 | [Weight probes](../results/stories-pilot-s00-trace-r01/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r01/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 3% | 15.898 | 15.584–16.205 | 0/32 | 0.436119 | +0.0034383 | 0.9889<br>[0.98876, 0.98896] | 0.985–0.996 | 0/32 | 0.843489 | [Weight probes](../results/stories-pilot-s00-trace-r03/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r03/score-flatness.json) |
| stories | pilot | 0 | Hessian trace | 10% | 16.444 | 15.949–16.644 | 0/32 | 0.412606 | +0.00325958 | 0.9878<br>[0.98770, 0.98789] | 0.984–0.995 | 0/32 | 0.845055 | [Weight probes](../results/stories-pilot-s00-trace-r10/flatness.json) · [Score probes](../results/stories-pilot-s00-trace-r10/score-flatness.json) |
