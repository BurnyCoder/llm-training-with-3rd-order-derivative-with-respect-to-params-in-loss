# Hybrid schedules on TinyStories

TinyStories hybrid follow-up: 8 of 48 full runs and 2 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements.

[Frozen protocol and decision rule](preregistration.md) · [Interactive measurement and run selector](../../docs/index.html#curves)

Two-sided directional width is measured in the original Euclidean weight coordinates at a fixed increase of 0.1 nats per target. Each linked JSON contains all 32 rays and their brackets. A missing upper bound means that the search reached its maximum radius before crossing. The five shared-checkpoint arms reuse the trunk’s switch measurement and its recorded probe time.

## Width observations

| Seed | Arm | Step | Width | Lower | Upper | Censored rays | Training probe NLL | Probe seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | [2048](../../results/stories-branch-s21-trunk-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 22 | Shared trace checkpoint | [2048](../../results/stories-branch-s22-trunk-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 21 | Curvature-dependent hybrid | [2048](../../results/stories-hybrid-s21-adaptive-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Curvature-dependent hybrid | [3072](../../results/stories-hybrid-s21-adaptive-r01/width-3072.json) | 13.95557 | 13.95459 | 13.95654 | 0 | 2.64916 | 5.48 |
| 21 | Curvature-dependent hybrid | [4096](../../results/stories-hybrid-s21-adaptive-r01/width-4096.json) | 13.15723 | 13.15625 | 13.15820 | 0 | 2.59304 | 5.24 |
| 21 | Always-on hybrid | [2048](../../results/stories-hybrid-s21-always-r01/width-2048.json) | 15.25562 | 15.25439 | 15.25684 | 0 | 2.77735 | 5.54 |
| 21 | Always-on hybrid | [3072](../../results/stories-hybrid-s21-always-r01/width-3072.json) | 14.00830 | 14.00732 | 14.00928 | 0 | 2.64903 | 5.13 |
| 21 | Always-on hybrid | [4096](../../results/stories-hybrid-s21-always-r01/width-4096.json) | 13.22852 | 13.22754 | 13.22949 | 0 | 2.59310 | 6.16 |
| 21 | Fixed late hybrid | [2048](../../results/stories-hybrid-s21-late-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Fixed late hybrid | [3072](../../results/stories-hybrid-s21-late-r01/width-3072.json) | 13.98096 | 13.97998 | 13.98193 | 0 | 2.64920 | 5.66 |
| 21 | Fixed late hybrid | [4096](../../results/stories-hybrid-s21-late-r01/width-4096.json) | 13.21533 | 13.21436 | 13.21631 | 0 | 2.59314 | 5.63 |
| 21 | Stronger trace | [2048](../../results/stories-hybrid-s21-strong-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Stronger trace | [3072](../../results/stories-hybrid-s21-strong-r01/width-3072.json) | 13.97119 | 13.97021 | 13.97217 | 0 | 2.64923 | 5.09 |
| 21 | Stronger trace | [4096](../../results/stories-hybrid-s21-strong-r01/width-4096.json) | 13.17480 | 13.17383 | 13.17578 | 0 | 2.59306 | 5.83 |
| 21 | Hessian trace | [2048](../../results/stories-hybrid-s21-trace-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 21 | Hessian trace | [3072](../../results/stories-hybrid-s21-trace-r01/width-3072.json) | 13.95410 | 13.95312 | 13.95508 | 0 | 2.64914 | 6.34 |
| 21 | Hessian trace | [4096](../../results/stories-hybrid-s21-trace-r01/width-4096.json) | 13.15430 | 13.15332 | 13.15527 | 0 | 2.59303 | 5.57 |
| 22 | Curvature-dependent hybrid | [2048](../../results/stories-hybrid-s22-adaptive-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Curvature-dependent hybrid | [3072](../../results/stories-hybrid-s22-adaptive-r01/width-3072.json) | 13.94922 | 13.94824 | 13.95020 | 0 | 2.65428 | 5.80 |
| 22 | Curvature-dependent hybrid | [4096](../../results/stories-hybrid-s22-adaptive-r01/width-4096.json) | 13.21484 | 13.21387 | 13.21582 | 0 | 2.60449 | 6.29 |
| 22 | Fixed late hybrid | [2048](../../results/stories-hybrid-s22-late-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Fixed late hybrid | [3072](../../results/stories-hybrid-s22-late-r01/width-3072.json) | 13.98975 | 13.98877 | 13.99072 | 0 | 2.65451 | 5.89 |
| 22 | Fixed late hybrid | [4096](../../results/stories-hybrid-s22-late-r01/width-4096.json) | 13.26758 | 13.26660 | 13.26855 | 0 | 2.60476 | 5.90 |
| 22 | Hessian trace | [2048](../../results/stories-hybrid-s22-trace-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Hessian trace | [3072](../../results/stories-hybrid-s22-trace-r01/width-3072.json) | 13.94922 | 13.94824 | 13.95020 | 0 | 2.65428 | 5.98 |
| 22 | Hessian trace | [4096](../../results/stories-hybrid-s22-trace-r01/width-4096.json) | 13.21484 | 13.21387 | 13.21582 | 0 | 2.60448 | 5.89 |

![Median directional width by seed and training arm](../../docs/figures/hybrid_width.png)

## Full development and resource measurements

| Seed | Arm | Dev NLL | Accuracy | Reference RMS | Steps at zero λ₃ | Final λ₃ | Targets/s | Allocated GPU MiB | Process peak MiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | 2.757685 | 0.43346 | 0.44853 | [2048](../../results/stories-branch-s21-trunk-r01/schedule.json) | 0 | 69,581 | 608.2 | 2,025.9 |
| 22 | Shared trace checkpoint | 2.757325 | 0.43399 | 0.40627 | [2048](../../results/stories-branch-s22-trunk-r01/schedule.json) | 0 | 61,905 | 608.2 | 2,077.5 |
| 21 | Curvature-dependent hybrid | 2.545908 | 0.46154 | 0.44853 | [2176](../../results/stories-hybrid-s21-adaptive-r01/schedule.json) | 1.38036e-15 | 43,973 | 617.3 | 2,072.2 |
| 21 | Always-on hybrid | 2.545923 | 0.46156 | 0.44052 | [0](../../results/stories-hybrid-s21-always-r01/schedule.json) | 3.01905e-14 | 30,503 | 621.3 | 2,001.6 |
| 21 | Fixed late hybrid | 2.546113 | 0.46158 | 0.44853 | [2049](../../results/stories-hybrid-s21-late-r01/schedule.json) | 3.01905e-14 | 41,141 | 617.3 | 2,078.0 |
| 21 | Stronger trace | 2.546010 | 0.46155 | 0.44853 | [4096](../../results/stories-hybrid-s21-strong-r01/schedule.json) | 0 | 66,667 | 608.2 | 2,073.2 |
| 21 | Hessian trace | 2.545904 | 0.46154 | 0.44853 | [4096](../../results/stories-hybrid-s21-trace-r01/schedule.json) | 0 | 64,342 | 608.2 | 2,057.7 |
| 22 | Curvature-dependent hybrid | 2.546305 | 0.46256 | 0.40627 | [2064](../../results/stories-hybrid-s22-adaptive-r01/schedule.json) | 1.2558e-16 | 37,992 | 617.3 | 2,081.5 |
| 22 | Fixed late hybrid | 2.546448 | 0.46258 | 0.40627 | [2049](../../results/stories-hybrid-s22-late-r01/schedule.json) | 3.01905e-14 | 39,514 | 617.3 | 2,083.8 |
| 22 | Hessian trace | 2.546305 | 0.46257 | 0.40627 | [4096](../../results/stories-hybrid-s22-trace-r01/schedule.json) | 0 | 61,689 | 608.2 | 2,088.9 |

## Stronger trace at the common checkpoint

| Seed | Draws | Additional trace coefficient | Seconds | Calibration record |
| --- | --- | --- | --- | --- |
| 21 | 16 | 4.557361e-08 | 12.07 | [Per-draw gradient norms](../../results/hybrid/calibration/seed-21.json) |

## Adaptive minus comparator per seed

Positive Δwidth favors the adaptive schedule. Negative ΔNLL favors its prediction. Comparable fit uses the frozen 0.02-nat training threshold.

| Seed | Comparator | Δwidth gain | Δdev NLL | Δtrain NLL | Comparable fit |
| --- | --- | --- | --- | --- | --- |
| 21 | Fixed late hybrid | -0.058105 | -0.000205 | -0.000104 | yes |
| 22 | Fixed late hybrid | -0.052734 | -0.000143 | -0.000277 | yes |
| 21 | Hessian trace | 0.002930 | 0.000005 | 0.000008 | yes |
| 22 | Hessian trace | 0.000000 | 0.000000 | 0.000003 | yes |
| 21 | Stronger trace | -0.017578 | -0.000102 | -0.000018 | yes |
| 21 | Always-on hybrid | 0.041748 | -0.000015 | -0.000061 | yes |

The completed branches reused 41,943,040 targets of optimization compared with independently training each branch from initialization. The replay permutation couples different seeds through their coefficient histories. The sign-test reference for this comparison assumes exchangeable independent pair signs. Shared donor histories make that assumption approximate. All raw pairs are reported for inspection.
