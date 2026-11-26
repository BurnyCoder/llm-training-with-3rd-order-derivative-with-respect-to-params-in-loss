# Flatness at saved checkpoints

Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)

## Registered TinyStories hybrids

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23, 24 | 15.172 | 13.103 | 13.001–13.215 | 12.933–13.331 | 0/128 |
| Fixed late hybrid | 21, 22, 23, 24 | 15.172 | 13.159 | 13.056–13.268 | 12.984–13.380 | 0/128 |
| Hessian trace | 21, 22, 23, 24 | 15.172 | 13.100 | 13.001–13.215 | 12.932–13.330 | 0/128 |
| Stronger trace | 21, 22, 23, 24 | 15.172 | 13.122 | 13.023–13.233 | 12.951–13.351 | 0/128 |
| Cross-seed replay | 22, 23, 24 | 15.201 | 13.047 | 13.004–13.218 | 12.880–13.366 | 0/96 |
| Always-on hybrid | 21, 22, 23, 24 | 15.277 | 13.161 | 13.060–13.334 | 13.022–13.389 | 0/128 |

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
| Ordinary AdamW · confirmation | 16,777,216 | 1–8 | 12.807 (8/8) | 0.59045 (8/8) | 1.0815 (8/8) |
| Hessian trace · confirmation | 16,777,216 | 1–8 | 12.899 (8/8) | 0.58173 (8/8) | 1.0815 (8/8) |
| Third derivative · confirmation | 16,777,216 | 1–8 | 12.913 (8/8) | 0.57334 (8/8) | 1.0813 (8/8) |
| Shared trace checkpoint | 8,388,608 | 21–28 | 15.201 (5/8) | 0.44989 (5/8) | 1.0624 (5/8) |
| Curvature-dependent hybrid · hybrid study | 16,777,216 | 21–28 | 13.103 (4/8) | 0.57782 (4/8) | 1.0824 (4/8) |
| Fixed late hybrid · hybrid study | 16,777,216 | 21–28 | 13.159 (4/8) | 0.57064 (4/8) | 1.0822 (4/8) |
| Hessian trace · hybrid study | 16,777,216 | 21–28 | 13.100 (4/8) | 0.57802 (4/8) | 1.0824 (4/8) |
| Stronger trace · hybrid study | 16,777,216 | 21–28 | 13.122 (4/8) | 0.57648 (4/8) | 1.0824 (4/8) |
| Cross-seed replay · hybrid study | 16,777,216 | 21–28 | 13.047 (3/8) | 0.57032 (3/8) | 1.0824 (3/8) |
| Always-on hybrid · hybrid study | 16,777,216 | 21–28 | 13.161 (4/8) | 0.56515 (4/8) | 1.0821 (4/8) |

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
| Squared Hessian norm (3%) | 65,536 | 0 | 19.853 (1/1) | 1.4535 (1/1) | 1.0927 (1/1) |
| Randomized gradient signs (1%) | 65,536 | 0 | 19.858 (1/1) | 0.73137 (1/1) | 1.0928 (1/1) |
| Trace + third derivative (1%) | 65,536 | 0 | 19.910 (1/1) | 0.6078 (1/1) | 1.0928 (1/1) |
| Ordinary AdamW · confirmation | 524,288 | 1–8 | 20.132 (1/8) | 0.55564 (1/8) | 1.1054 (1/8) |
| Hessian trace · confirmation | 524,288 | 1–8 | 20.270 (1/8) | 0.62496 (1/8) | 1.1057 (1/8) |
| Third derivative · confirmation | 524,288 | 1–8 | 19.828 (2/8) | 0.62651 (2/8) | 1.1043 (2/8) |

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
| abstracts | confirm | 1 | Ordinary AdamW | 0% | 20.132 | 19.362–20.737 | 0/32 | 0.555644 | +0.00201225 | 1.1054<br>[1.10528, 1.10553] | 1.103–1.113 | 0/32 | 0.674904 | [Weight probes](../results/abstracts-confirm-s01-ce-r00/flatness.json) · [Score probes](../results/abstracts-confirm-s01-ce-r00/score-flatness.json) |
| abstracts | confirm | 1 | Third derivative | 1% | 20.313 | 19.476–20.931 | 0/32 | 0.605748 | +0.00183383 | 1.1055<br>[1.10534, 1.10560] | 1.103–1.113 | 0/32 | 0.674805 | [Weight probes](../results/abstracts-confirm-s01-third-r01-fp64/flatness.json) · [Score probes](../results/abstracts-confirm-s01-third-r01-fp64/score-flatness.json) |
| abstracts | confirm | 1 | Hessian trace | 1% | 20.270 | 19.558–20.675 | 0/32 | 0.624955 | +0.00159403 | 1.1057<br>[1.10552, 1.10578] | 1.103–1.113 | 0/32 | 0.674637 | [Weight probes](../results/abstracts-confirm-s01-trace-r01-fp64/flatness.json) · [Score probes](../results/abstracts-confirm-s01-trace-r01-fp64/score-flatness.json) |
| abstracts | confirm | 2 | Third derivative | 1% | 19.342 | 18.818–20.285 | 0/32 | 0.647265 | +0.000399434 | 1.1031<br>[1.10296, 1.10322] | 1.100–1.111 | 0/32 | 0.678266 | [Weight probes](../results/abstracts-confirm-s02-third-r01-fp64/flatness.json) · [Score probes](../results/abstracts-confirm-s02-third-r01-fp64/score-flatness.json) |
| abstracts | control | 0 | Initial checkpoint | 0% | 21.890 | 21.676–22.687 | 0/32 | 0.690576 | +0.0011406 | 1.0859<br>[1.08575, 1.08597] | 1.081–1.095 | 0/32 | 0.700479 | [Weight probes](../results/abstracts-control-s00-initial-r00/flatness.json) · [Score probes](../results/abstracts-control-s00-initial-r00/score-flatness.json) |
| abstracts | control | 0 | Unigram | 0% | N/A | N/A | N/A | N/A | N/A | 0.9150<br>[0.91494, 0.91511] | 0.913–0.924 | 0/32 | 0.993798 | [Score probes](../results/abstracts-control-s00-unigram-r00/score-flatness.json) |
| abstracts | pilot | 0 | Ordinary AdamW | 0% | 19.784 | 19.185–20.320 | 0/32 | 1.28684 | +0.00312322 | 1.0930<br>[1.09295, 1.09314] | 1.090–1.100 | 0/32 | 0.69199 | [Weight probes](../results/abstracts-pilot-s00-ce-r00/flatness.json) · [Score probes](../results/abstracts-pilot-s00-ce-r00/score-flatness.json) |
| abstracts | pilot | 0 | Trace + third derivative | 1% | 19.910 | 19.432–20.434 | 0/32 | 0.607804 | +0.00161838 | 1.0928<br>[1.09271, 1.09290] | 1.090–1.100 | 0/32 | 0.692197 | [Weight probes](../results/abstracts-pilot-s00-combined-r01-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-combined-r01-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Squared Hessian norm | 3% | 19.853 | 19.289–20.268 | 0/32 | 1.45346 | +0.0043099 | 1.0927<br>[1.09265, 1.09284] | 1.089–1.100 | 0/32 | 0.692295 | [Weight probes](../results/abstracts-pilot-s00-hessian_norm-r03-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-hessian_norm-r03-fp64/score-flatness.json) |
| abstracts | pilot | 0 | Randomized gradient signs | 1% | 19.858 | 19.219–20.285 | 0/32 | 0.731368 | +0.000460964 | 1.0928<br>[1.09274, 1.09293] | 1.090–1.100 | 0/32 | 0.692161 | [Weight probes](../results/abstracts-pilot-s00-sham-r01-fp64/flatness.json) · [Score probes](../results/abstracts-pilot-s00-sham-r01-fp64/score-flatness.json) |
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
| stories | branch | 25 | Shared trace checkpoint | 1% | 15.394 | 15.169–15.717 | 0/32 | 0.45922 | +0.00336295 | 1.0706<br>[1.07043, 1.07068] | 1.062–1.081 | 0/32 | 0.718901 | [Weight probes](../results/stories-branch-s25-trunk-r01/flatness.json) · [Score probes](../results/stories-branch-s25-trunk-r01/score-flatness.json) |
| stories | confirm | 1 | Ordinary AdamW | 0% | 12.963 | 12.629–13.082 | 0/32 | 0.561485 | +0.00418601 | 1.0812<br>[1.08111, 1.08136] | 1.074–1.093 | 0/32 | 0.703048 | [Weight probes](../results/stories-confirm-s01-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s01-ce-r00/score-flatness.json) |
| stories | confirm | 1 | Third derivative | 1% | 13.036 | 12.735–13.122 | 0/32 | 0.550424 | +0.0042243 | 1.0807<br>[1.08056, 1.08082] | 1.074–1.092 | 0/32 | 0.70374 | [Weight probes](../results/stories-confirm-s01-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s01-third-r01/score-flatness.json) |
| stories | confirm | 1 | Hessian trace | 1% | 13.044 | 12.774–13.166 | 0/32 | 0.550762 | +0.00413246 | 1.0807<br>[1.08062, 1.08088] | 1.074–1.092 | 0/32 | 0.703135 | [Weight probes](../results/stories-confirm-s01-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s01-trace-r01/score-flatness.json) |
| stories | confirm | 2 | Ordinary AdamW | 0% | 12.933 | 12.747–13.158 | 0/32 | 0.586303 | +0.00421975 | 1.0813<br>[1.08117, 1.08143] | 1.077–1.093 | 0/32 | 0.702252 | [Weight probes](../results/stories-confirm-s02-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s02-ce-r00/score-flatness.json) |
| stories | confirm | 2 | Third derivative | 1% | 13.066 | 12.857–13.192 | 0/32 | 0.570884 | +0.00413326 | 1.0814<br>[1.08123, 1.08149] | 1.077–1.093 | 0/32 | 0.702187 | [Weight probes](../results/stories-confirm-s02-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s02-third-r01/score-flatness.json) |
| stories | confirm | 2 | Hessian trace | 1% | 13.038 | 12.888–13.183 | 0/32 | 0.577657 | +0.00413847 | 1.0815<br>[1.08135, 1.08161] | 1.078–1.093 | 0/32 | 0.702051 | [Weight probes](../results/stories-confirm-s02-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s02-trace-r01/score-flatness.json) |
| stories | confirm | 3 | Ordinary AdamW | 0% | 12.759 | 12.611–13.119 | 0/32 | 0.592477 | +0.00468202 | 1.0806<br>[1.08053, 1.08075] | 1.075–1.092 | 0/32 | 0.702214 | [Weight probes](../results/stories-confirm-s03-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s03-ce-r00/score-flatness.json) |
| stories | confirm | 3 | Third derivative | 1% | 12.923 | 12.770–13.295 | 0/32 | 0.575793 | +0.00450279 | 1.0806<br>[1.08047, 1.08069] | 1.075–1.092 | 0/32 | 0.702466 | [Weight probes](../results/stories-confirm-s03-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s03-third-r01/score-flatness.json) |
| stories | confirm | 3 | Hessian trace | 1% | 12.903 | 12.739–13.233 | 0/32 | 0.584484 | +0.00454272 | 1.0810<br>[1.08090, 1.08112] | 1.075–1.092 | 0/32 | 0.702121 | [Weight probes](../results/stories-confirm-s03-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s03-trace-r01/score-flatness.json) |
| stories | confirm | 4 | Ordinary AdamW | 0% | 12.542 | 12.347–12.837 | 0/32 | 0.593044 | +0.00524858 | 1.0817<br>[1.08163, 1.08185] | 1.076–1.090 | 0/32 | 0.702902 | [Weight probes](../results/stories-confirm-s04-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s04-ce-r00/score-flatness.json) |
| stories | confirm | 4 | Third derivative | 1% | 12.667 | 12.440–12.956 | 0/32 | 0.579597 | +0.00516432 | 1.0813<br>[1.08120, 1.08143] | 1.075–1.090 | 0/32 | 0.703429 | [Weight probes](../results/stories-confirm-s04-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s04-third-r01/score-flatness.json) |
| stories | confirm | 4 | Hessian trace | 1% | 12.638 | 12.393–12.882 | 0/32 | 0.588306 | +0.00526637 | 1.0816<br>[1.08148, 1.08170] | 1.075–1.090 | 0/32 | 0.703512 | [Weight probes](../results/stories-confirm-s04-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s04-trace-r01/score-flatness.json) |
| stories | confirm | 5 | Ordinary AdamW | 0% | 12.909 | 12.736–13.097 | 0/32 | 0.598474 | +0.00489463 | 1.0825<br>[1.08233, 1.08259] | 1.079–1.094 | 0/32 | 0.699181 | [Weight probes](../results/stories-confirm-s05-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s05-ce-r00/score-flatness.json) |
| stories | confirm | 5 | Third derivative | 1% | 13.101 | 12.915–13.294 | 0/32 | 0.580551 | +0.00473987 | 1.0825<br>[1.08233, 1.08259] | 1.079–1.095 | 0/32 | 0.698997 | [Weight probes](../results/stories-confirm-s05-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s05-third-r01/score-flatness.json) |
| stories | confirm | 5 | Hessian trace | 1% | 12.974 | 12.797–13.214 | 0/32 | 0.595544 | +0.00485511 | 1.0825<br>[1.08233, 1.08259] | 1.079–1.095 | 0/32 | 0.698947 | [Weight probes](../results/stories-confirm-s05-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s05-trace-r01/score-flatness.json) |
| stories | confirm | 6 | Ordinary AdamW | 0% | 12.783 | 12.522–12.998 | 0/32 | 0.600867 | +0.00498042 | 1.0797<br>[1.07958, 1.07984] | 1.075–1.092 | 0/32 | 0.702769 | [Weight probes](../results/stories-confirm-s06-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s06-ce-r00/score-flatness.json) |
| stories | confirm | 6 | Third derivative | 1% | 12.863 | 12.552–13.108 | 0/32 | 0.581589 | +0.00501794 | 1.0797<br>[1.07958, 1.07984] | 1.074–1.092 | 0/32 | 0.703612 | [Weight probes](../results/stories-confirm-s06-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s06-third-r01/score-flatness.json) |
| stories | confirm | 6 | Hessian trace | 1% | 12.810 | 12.489–13.084 | 0/32 | 0.593577 | +0.00503727 | 1.0801<br>[1.08001, 1.08027] | 1.075–1.092 | 0/32 | 0.702779 | [Weight probes](../results/stories-confirm-s06-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s06-trace-r01/score-flatness.json) |
| stories | confirm | 7 | Ordinary AdamW | 0% | 12.656 | 12.503–12.934 | 0/32 | 0.58843 | +0.00511004 | 1.0831<br>[1.08294, 1.08317] | 1.078–1.094 | 0/32 | 0.698997 | [Weight probes](../results/stories-confirm-s07-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s07-ce-r00/score-flatness.json) |
| stories | confirm | 7 | Third derivative | 1% | 12.789 | 12.666–13.054 | 0/32 | 0.570517 | +0.00499871 | 1.0831<br>[1.08294, 1.08317] | 1.078–1.094 | 0/32 | 0.698793 | [Weight probes](../results/stories-confirm-s07-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s07-third-r01/score-flatness.json) |
| stories | confirm | 7 | Hessian trace | 1% | 12.765 | 12.622–12.976 | 0/32 | 0.578968 | +0.00509515 | 1.0830<br>[1.08291, 1.08313] | 1.078–1.094 | 0/32 | 0.698973 | [Weight probes](../results/stories-confirm-s07-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s07-trace-r01/score-flatness.json) |
| stories | confirm | 8 | Ordinary AdamW | 0% | 12.832 | 12.517–12.918 | 0/32 | 0.578518 | +0.0051269 | 1.0852<br>[1.08505, 1.08527] | 1.079–1.096 | 0/32 | 0.697695 | [Weight probes](../results/stories-confirm-s08-ce-r00/flatness.json) · [Score probes](../results/stories-confirm-s08-ce-r00/score-flatness.json) |
| stories | confirm | 8 | Third derivative | 1% | 12.903 | 12.692–13.039 | 0/32 | 0.564954 | +0.00497425 | 1.0853<br>[1.08517, 1.08539] | 1.080–1.096 | 0/32 | 0.697584 | [Weight probes](../results/stories-confirm-s08-third-r01/flatness.json) · [Score probes](../results/stories-confirm-s08-third-r01/score-flatness.json) |
| stories | confirm | 8 | Hessian trace | 1% | 12.896 | 12.628–13.021 | 0/32 | 0.570914 | +0.00504401 | 1.0855<br>[1.08541, 1.08564] | 1.080–1.096 | 0/32 | 0.696954 | [Weight probes](../results/stories-confirm-s08-trace-r01/flatness.json) · [Score probes](../results/stories-confirm-s08-trace-r01/score-flatness.json) |
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
| stories | hybrid | 24 | Always-on hybrid | 1% | 13.093 | 12.738–13.388 | 0/32 | 0.556036 | +0.00452124 | 1.0809<br>[1.08078, 1.08100] | 1.074–1.091 | 0/32 | 0.704032 | [Weight probes](../results/stories-hybrid-s24-always-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-always-r01/score-flatness.json) |
| stories | hybrid | 24 | Fixed late hybrid | 1% | 13.056 | 12.700–13.349 | 0/32 | 0.562815 | +0.00452056 | 1.0811<br>[1.08096, 1.08118] | 1.075–1.091 | 0/32 | 0.703809 | [Weight probes](../results/stories-hybrid-s24-late-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-late-r01/score-flatness.json) |
| stories | hybrid | 24 | Cross-seed replay | 1% | 13.004 | 12.641–13.296 | 0/32 | 0.570324 | +0.00455275 | 1.0813<br>[1.08123, 1.08146] | 1.075–1.092 | 0/32 | 0.703536 | [Weight probes](../results/stories-hybrid-s24-replay-r01/flatness.json) · [Score probes](../results/stories-hybrid-s24-replay-r01/score-flatness.json) |
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
