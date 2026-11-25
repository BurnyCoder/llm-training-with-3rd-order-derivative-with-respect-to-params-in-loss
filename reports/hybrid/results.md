# Hybrid schedules on TinyStories

TinyStories hybrid follow-up: 3 of 48 full runs and 1 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements.

[Frozen protocol and decision rule](preregistration.md) · [Interactive measurement and run selector](../../docs/index.html#curves)

Two-sided directional width is measured in the original Euclidean weight coordinates at a fixed increase of 0.1 nats per target. Each linked JSON contains all 32 rays and their brackets. A missing upper bound means that the search reached its maximum radius before crossing. The five shared-checkpoint arms reuse the trunk’s switch measurement and its recorded probe time.

## Width observations

| Seed | Arm | Step | Width | Lower | Upper | Censored rays | Training probe NLL | Probe seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | [2048](../../results/stories-branch-s21-trunk-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Curvature-dependent hybrid | [2048](../../results/stories-hybrid-s21-adaptive-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Curvature-dependent hybrid | [3072](../../results/stories-hybrid-s21-adaptive-r01/width-3072.json) | 13.95557 | 13.95459 | 13.95654 | 0 | 2.64916 | 5.48 |
| 21 | Curvature-dependent hybrid | [4096](../../results/stories-hybrid-s21-adaptive-r01/width-4096.json) | 13.15723 | 13.15625 | 13.15820 | 0 | 2.59304 | 5.24 |
| 21 | Fixed late hybrid | [2048](../../results/stories-hybrid-s21-late-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Fixed late hybrid | [3072](../../results/stories-hybrid-s21-late-r01/width-3072.json) | 13.98096 | 13.97998 | 13.98193 | 0 | 2.64920 | 5.66 |
| 21 | Fixed late hybrid | [4096](../../results/stories-hybrid-s21-late-r01/width-4096.json) | 13.21533 | 13.21436 | 13.21631 | 0 | 2.59314 | 5.63 |
| 21 | Hessian trace | [2048](../../results/stories-hybrid-s21-trace-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Hessian trace | [3072](../../results/stories-hybrid-s21-trace-r01/width-3072.json) | 13.95410 | 13.95312 | 13.95508 | 0 | 2.64914 | 6.34 |
| 21 | Hessian trace | [4096](../../results/stories-hybrid-s21-trace-r01/width-4096.json) | 13.15430 | 13.15332 | 13.15527 | 0 | 2.59303 | 5.57 |

![Median directional width by seed and training arm](../../docs/figures/hybrid_width.png)

## Full development and resource measurements

| Seed | Arm | Dev NLL | Accuracy | Reference RMS | Steps at zero λ₃ | Final λ₃ | Targets/s | Allocated GPU MiB | Process peak MiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | 2.757685 | 0.43346 | 0.44853 | [2048](../../results/stories-branch-s21-trunk-r01/schedule.json) | 0 | 69,581 | 608.2 | 2,025.9 |
| 21 | Curvature-dependent hybrid | 2.545908 | 0.46154 | 0.44853 | [2176](../../results/stories-hybrid-s21-adaptive-r01/schedule.json) | 1.38036e-15 | 43,973 | 617.3 | 2,072.2 |
| 21 | Fixed late hybrid | 2.546113 | 0.46158 | 0.44853 | [2049](../../results/stories-hybrid-s21-late-r01/schedule.json) | 3.01905e-14 | 41,141 | 617.3 | 2,078.0 |
| 21 | Hessian trace | 2.545904 | 0.46154 | 0.44853 | [4096](../../results/stories-hybrid-s21-trace-r01/schedule.json) | 0 | 64,342 | 608.2 | 2,057.7 |

## Adaptive minus comparator per seed

Positive Δwidth favors the adaptive schedule. Negative ΔNLL favors its prediction. Comparable fit uses the frozen 0.02-nat training threshold.

| Seed | Comparator | Δwidth gain | Δdev NLL | Δtrain NLL | Comparable fit |
| --- | --- | --- | --- | --- | --- |
| 21 | Fixed late hybrid | -0.058105 | -0.000205 | -0.000104 | yes |
| 21 | Hessian trace | 0.002930 | 0.000005 | 0.000008 | yes |

The completed branches reused 16,777,216 targets of optimization compared with independently training each branch from initialization. The replay permutation couples different seeds through their coefficient histories. The sign-test reference for this comparison assumes exchangeable independent pair signs. Shared donor histories make that assumption approximate. All raw pairs are reported for inspection.
