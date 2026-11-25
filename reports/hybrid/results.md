# Hybrid schedules on TinyStories

TinyStories hybrid follow-up: 23 of 48 full runs and 5 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements.

[Frozen protocol and decision rule](preregistration.md) · [Interactive measurement and run selector](../../docs/index.html#curves)

Two-sided directional width is measured in the original Euclidean weight coordinates at a fixed increase of 0.1 nats per target. Each linked JSON contains all 32 rays and their brackets. A missing upper bound means that the search reached its maximum radius before crossing. The five shared-checkpoint arms reuse the trunk’s switch measurement and its recorded probe time.

## Width observations

| Seed | Arm | Step | Width | Lower | Upper | Censored rays | Training probe NLL | Probe seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | [2048](../../results/stories-branch-s21-trunk-r01/width-2048.json) | 15.14258 | 15.14160 | 15.14355 | 0 | 2.77694 | 5.28 |
| 22 | Shared trace checkpoint | [2048](../../results/stories-branch-s22-trunk-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 23 | Shared trace checkpoint | [2048](../../results/stories-branch-s23-trunk-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 24 | Shared trace checkpoint | [2048](../../results/stories-branch-s24-trunk-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 25 | Shared trace checkpoint | [2048](../../results/stories-branch-s25-trunk-r01/width-2048.json) | 15.39355 | 15.39258 | 15.39453 | 0 | 2.80412 | 8.23 |
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
| 22 | Always-on hybrid | [2048](../../results/stories-hybrid-s22-always-r01/width-2048.json) | 15.45825 | 15.45703 | 15.45947 | 0 | 2.81592 | 7.13 |
| 22 | Always-on hybrid | [3072](../../results/stories-hybrid-s22-always-r01/width-3072.json) | 14.03955 | 14.03857 | 14.04053 | 0 | 2.65258 | 7.40 |
| 22 | Always-on hybrid | [4096](../../results/stories-hybrid-s22-always-r01/width-4096.json) | 13.33447 | 13.33350 | 13.33545 | 0 | 2.60446 | 7.15 |
| 22 | Fixed late hybrid | [2048](../../results/stories-hybrid-s22-late-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Fixed late hybrid | [3072](../../results/stories-hybrid-s22-late-r01/width-3072.json) | 13.98975 | 13.98877 | 13.99072 | 0 | 2.65451 | 5.89 |
| 22 | Fixed late hybrid | [4096](../../results/stories-hybrid-s22-late-r01/width-4096.json) | 13.26758 | 13.26660 | 13.26855 | 0 | 2.60476 | 5.90 |
| 22 | Cross-seed replay | [2048](../../results/stories-hybrid-s22-replay-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Cross-seed replay | [3072](../../results/stories-hybrid-s22-replay-r01/width-3072.json) | 13.95166 | 13.95068 | 13.95264 | 0 | 2.65427 | 7.07 |
| 22 | Cross-seed replay | [4096](../../results/stories-hybrid-s22-replay-r01/width-4096.json) | 13.21777 | 13.21680 | 13.21875 | 0 | 2.60450 | 6.94 |
| 22 | Stronger trace | [2048](../../results/stories-hybrid-s22-strong-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Stronger trace | [3072](../../results/stories-hybrid-s22-strong-r01/width-3072.json) | 13.96240 | 13.96143 | 13.96338 | 0 | 2.65431 | 6.13 |
| 22 | Stronger trace | [4096](../../results/stories-hybrid-s22-strong-r01/width-4096.json) | 13.23291 | 13.23193 | 13.23389 | 0 | 2.60456 | 6.56 |
| 22 | Hessian trace | [2048](../../results/stories-hybrid-s22-trace-r01/width-2048.json) | 15.40259 | 15.40137 | 15.40381 | 0 | 2.81658 | 5.80 |
| 22 | Hessian trace | [3072](../../results/stories-hybrid-s22-trace-r01/width-3072.json) | 13.94922 | 13.94824 | 13.95020 | 0 | 2.65428 | 5.98 |
| 22 | Hessian trace | [4096](../../results/stories-hybrid-s22-trace-r01/width-4096.json) | 13.21484 | 13.21387 | 13.21582 | 0 | 2.60448 | 5.89 |
| 23 | Curvature-dependent hybrid | [2048](../../results/stories-hybrid-s23-adaptive-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 23 | Curvature-dependent hybrid | [3072](../../results/stories-hybrid-s23-adaptive-r01/width-3072.json) | 13.89697 | 13.89600 | 13.89795 | 0 | 2.64069 | 6.27 |
| 23 | Curvature-dependent hybrid | [4096](../../results/stories-hybrid-s23-adaptive-r01/width-4096.json) | 13.04834 | 13.04736 | 13.04932 | 0 | 2.59710 | 6.49 |
| 23 | Always-on hybrid | [2048](../../results/stories-hybrid-s23-always-r01/width-2048.json) | 15.05615 | 15.05518 | 15.05713 | 0 | 2.80374 | 4.80 |
| 23 | Always-on hybrid | [3072](../../results/stories-hybrid-s23-always-r01/width-3072.json) | 13.92969 | 13.92871 | 13.93066 | 0 | 2.63984 | 4.69 |
| 23 | Always-on hybrid | [4096](../../results/stories-hybrid-s23-always-r01/width-4096.json) | 13.05957 | 13.05859 | 13.06055 | 0 | 2.59574 | 5.08 |
| 23 | Fixed late hybrid | [2048](../../results/stories-hybrid-s23-late-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 23 | Fixed late hybrid | [3072](../../results/stories-hybrid-s23-late-r01/width-3072.json) | 13.92383 | 13.92285 | 13.92480 | 0 | 2.64046 | 5.92 |
| 23 | Fixed late hybrid | [4096](../../results/stories-hybrid-s23-late-r01/width-4096.json) | 13.10254 | 13.10156 | 13.10352 | 0 | 2.59694 | 5.37 |
| 23 | Cross-seed replay | [2048](../../results/stories-hybrid-s23-replay-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 23 | Cross-seed replay | [3072](../../results/stories-hybrid-s23-replay-r01/width-3072.json) | 13.89600 | 13.89502 | 13.89697 | 0 | 2.64070 | 6.36 |
| 23 | Cross-seed replay | [4096](../../results/stories-hybrid-s23-replay-r01/width-4096.json) | 13.04736 | 13.04639 | 13.04834 | 0 | 2.59711 | 6.60 |
| 23 | Stronger trace | [2048](../../results/stories-hybrid-s23-strong-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 23 | Stronger trace | [3072](../../results/stories-hybrid-s23-strong-r01/width-3072.json) | 13.91357 | 13.91260 | 13.91455 | 0 | 2.64074 | 5.01 |
| 23 | Stronger trace | [4096](../../results/stories-hybrid-s23-strong-r01/width-4096.json) | 13.06885 | 13.06787 | 13.06982 | 0 | 2.59718 | 5.36 |
| 23 | Hessian trace | [2048](../../results/stories-hybrid-s23-trace-r01/width-2048.json) | 14.99414 | 14.99316 | 14.99512 | 0 | 2.80132 | 7.17 |
| 23 | Hessian trace | [3072](../../results/stories-hybrid-s23-trace-r01/width-3072.json) | 13.89600 | 13.89502 | 13.89697 | 0 | 2.64070 | 5.17 |
| 23 | Hessian trace | [4096](../../results/stories-hybrid-s23-trace-r01/width-4096.json) | 13.04639 | 13.04541 | 13.04736 | 0 | 2.59711 | 6.03 |
| 24 | Curvature-dependent hybrid | [2048](../../results/stories-hybrid-s24-adaptive-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 24 | Curvature-dependent hybrid | [3072](../../results/stories-hybrid-s24-adaptive-r01/width-3072.json) | 13.85303 | 13.85205 | 13.85400 | 0 | 2.66510 | 6.14 |
| 24 | Curvature-dependent hybrid | [4096](../../results/stories-hybrid-s24-adaptive-r01/width-4096.json) | 13.00146 | 13.00049 | 13.00244 | 0 | 2.61916 | 5.90 |
| 24 | Always-on hybrid | [2048](../../results/stories-hybrid-s24-always-r01/width-2048.json) | 15.29785 | 15.29639 | 15.29932 | 0 | 2.79781 | 5.46 |
| 24 | Always-on hybrid | [3072](../../results/stories-hybrid-s24-always-r01/width-3072.json) | 13.95947 | 13.95850 | 13.96045 | 0 | 2.66264 | 5.10 |
| 24 | Always-on hybrid | [4096](../../results/stories-hybrid-s24-always-r01/width-4096.json) | 13.09277 | 13.09180 | 13.09375 | 0 | 2.61682 | 4.85 |
| 24 | Fixed late hybrid | [2048](../../results/stories-hybrid-s24-late-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 24 | Fixed late hybrid | [3072](../../results/stories-hybrid-s24-late-r01/width-3072.json) | 13.88916 | 13.88818 | 13.89014 | 0 | 2.66526 | 6.18 |
| 24 | Fixed late hybrid | [4096](../../results/stories-hybrid-s24-late-r01/width-4096.json) | 13.05566 | 13.05469 | 13.05664 | 0 | 2.61935 | 6.12 |
| 24 | Cross-seed replay | [2048](../../results/stories-hybrid-s24-replay-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 24 | Cross-seed replay | [3072](../../results/stories-hybrid-s24-replay-r01/width-3072.json) | 13.85449 | 13.85352 | 13.85547 | 0 | 2.66512 | 4.97 |
| 24 | Cross-seed replay | [4096](../../results/stories-hybrid-s24-replay-r01/width-4096.json) | 13.00391 | 13.00293 | 13.00488 | 0 | 2.61917 | 4.85 |
| 24 | Stronger trace | [2048](../../results/stories-hybrid-s24-strong-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 24 | Stronger trace | [3072](../../results/stories-hybrid-s24-strong-r01/width-3072.json) | 13.86426 | 13.86328 | 13.86523 | 0 | 2.66519 | 5.65 |
| 24 | Stronger trace | [4096](../../results/stories-hybrid-s24-strong-r01/width-4096.json) | 13.02344 | 13.02246 | 13.02441 | 0 | 2.61948 | 6.53 |
| 24 | Hessian trace | [2048](../../results/stories-hybrid-s24-trace-r01/width-2048.json) | 15.20142 | 15.20020 | 15.20264 | 0 | 2.79983 | 6.09 |
| 24 | Hessian trace | [3072](../../results/stories-hybrid-s24-trace-r01/width-3072.json) | 13.85254 | 13.85156 | 13.85352 | 0 | 2.66510 | 5.89 |
| 24 | Hessian trace | [4096](../../results/stories-hybrid-s24-trace-r01/width-4096.json) | 13.00146 | 13.00049 | 13.00244 | 0 | 2.61916 | 6.25 |

![Median directional width by seed and training arm](../../docs/figures/hybrid_width.png)

## Full development and resource measurements

| Seed | Arm | Dev NLL | Accuracy | Reference RMS | Steps at zero λ₃ | Final λ₃ | Targets/s | Allocated GPU MiB | Process peak MiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21 | Shared trace checkpoint | 2.757685 | 0.43346 | 0.44853 | [2048](../../results/stories-branch-s21-trunk-r01/schedule.json) | 0 | 69,581 | 608.2 | 2,025.9 |
| 22 | Shared trace checkpoint | 2.757325 | 0.43399 | 0.40627 | [2048](../../results/stories-branch-s22-trunk-r01/schedule.json) | 0 | 61,905 | 608.2 | 2,077.5 |
| 23 | Shared trace checkpoint | 2.752497 | 0.43492 | 0.45587 | [2048](../../results/stories-branch-s23-trunk-r01/schedule.json) | 0 | 54,841 | 608.2 | 2,090.3 |
| 24 | Shared trace checkpoint | 2.763870 | 0.43259 | 0.41159 | [2048](../../results/stories-branch-s24-trunk-r01/schedule.json) | 0 | 60,780 | 608.2 | 2,040.6 |
| 25 | Shared trace checkpoint | 2.762062 | 0.43342 | 0.42858 | [2048](../../results/stories-branch-s25-trunk-r01/schedule.json) | 0 | 45,520 | 608.2 | 3,043.0 |
| 21 | Curvature-dependent hybrid | 2.545908 | 0.46154 | 0.44853 | [2176](../../results/stories-hybrid-s21-adaptive-r01/schedule.json) | 1.38036e-15 | 43,973 | 617.3 | 2,072.2 |
| 21 | Always-on hybrid | 2.545923 | 0.46156 | 0.44052 | [0](../../results/stories-hybrid-s21-always-r01/schedule.json) | 3.01905e-14 | 30,503 | 621.3 | 2,001.6 |
| 21 | Fixed late hybrid | 2.546113 | 0.46158 | 0.44853 | [2049](../../results/stories-hybrid-s21-late-r01/schedule.json) | 3.01905e-14 | 41,141 | 617.3 | 2,078.0 |
| 21 | Stronger trace | 2.546010 | 0.46155 | 0.44853 | [4096](../../results/stories-hybrid-s21-strong-r01/schedule.json) | 0 | 66,667 | 608.2 | 2,073.2 |
| 21 | Hessian trace | 2.545904 | 0.46154 | 0.44853 | [4096](../../results/stories-hybrid-s21-trace-r01/schedule.json) | 0 | 64,342 | 608.2 | 2,057.7 |
| 22 | Curvature-dependent hybrid | 2.546305 | 0.46256 | 0.40627 | [2064](../../results/stories-hybrid-s22-adaptive-r01/schedule.json) | 1.2558e-16 | 37,992 | 617.3 | 2,081.5 |
| 22 | Always-on hybrid | 2.545968 | 0.46273 | 0.40084 | [0](../../results/stories-hybrid-s22-always-r01/schedule.json) | 3.01905e-14 | 25,017 | 621.3 | 2,090.3 |
| 22 | Fixed late hybrid | 2.546448 | 0.46258 | 0.40627 | [2049](../../results/stories-hybrid-s22-late-r01/schedule.json) | 3.01905e-14 | 39,514 | 617.3 | 2,083.8 |
| 22 | Cross-seed replay | 2.546307 | 0.46256 | 0.40627 | [2176](../../results/stories-hybrid-s22-replay-r01/schedule.json) | 1.38036e-15 | 36,853 | 617.3 | 2,090.3 |
| 22 | Stronger trace | 2.546388 | 0.46254 | 0.40627 | [4096](../../results/stories-hybrid-s22-strong-r01/schedule.json) | 0 | 60,263 | 608.2 | 2,090.3 |
| 22 | Hessian trace | 2.546305 | 0.46257 | 0.40627 | [4096](../../results/stories-hybrid-s22-trace-r01/schedule.json) | 0 | 61,689 | 608.2 | 2,088.9 |
| 23 | Curvature-dependent hybrid | 2.542260 | 0.46318 | 0.45587 | [2064](../../results/stories-hybrid-s23-adaptive-r01/schedule.json) | 1.00616e-15 | 37,872 | 617.3 | 2,090.3 |
| 23 | Always-on hybrid | 2.542886 | 0.46314 | 0.44585 | [0](../../results/stories-hybrid-s23-always-r01/schedule.json) | 3.01905e-14 | 32,400 | 621.3 | 2,095.6 |
| 23 | Fixed late hybrid | 2.542464 | 0.46313 | 0.45587 | [2049](../../results/stories-hybrid-s23-late-r01/schedule.json) | 3.01905e-14 | 40,662 | 617.3 | 2,090.3 |
| 23 | Cross-seed replay | 2.542257 | 0.46318 | 0.45587 | [2064](../../results/stories-hybrid-s23-replay-r01/schedule.json) | 1.2558e-16 | 35,140 | 617.3 | 2,100.0 |
| 23 | Stronger trace | 2.542354 | 0.46314 | 0.45587 | [4096](../../results/stories-hybrid-s23-strong-r01/schedule.json) | 0 | 60,806 | 608.2 | 2,089.5 |
| 23 | Hessian trace | 2.542257 | 0.46318 | 0.45587 | [4096](../../results/stories-hybrid-s23-trace-r01/schedule.json) | 0 | 59,471 | 608.2 | 2,034.6 |
| 24 | Curvature-dependent hybrid | 2.554469 | 0.46067 | 0.41159 | [2064](../../results/stories-hybrid-s24-adaptive-r01/schedule.json) | 3.36329e-17 | 41,647 | 617.3 | 3,043.0 |
| 24 | Always-on hybrid | 2.554199 | 0.46050 | 0.40492 | [0](../../results/stories-hybrid-s24-always-r01/schedule.json) | 3.01905e-14 | 33,941 | 621.3 | 3,043.0 |
| 24 | Fixed late hybrid | 2.554672 | 0.46061 | 0.41159 | [2049](../../results/stories-hybrid-s24-late-r01/schedule.json) | 3.01905e-14 | 42,225 | 617.3 | 3,043.0 |
| 24 | Cross-seed replay | 2.554472 | 0.46067 | 0.41159 | [2064](../../results/stories-hybrid-s24-replay-r01/schedule.json) | 1.00616e-15 | 46,104 | 617.3 | 3,043.0 |
| 24 | Stronger trace | 2.554562 | 0.46062 | 0.41159 | [4096](../../results/stories-hybrid-s24-strong-r01/schedule.json) | 0 | 63,357 | 608.2 | 3,043.0 |
| 24 | Hessian trace | 2.554469 | 0.46067 | 0.41159 | [4096](../../results/stories-hybrid-s24-trace-r01/schedule.json) | 0 | 63,221 | 608.2 | 3,043.0 |

## Stronger trace at the common checkpoint

| Seed | Draws | Additional trace coefficient | Seconds | Calibration record |
| --- | --- | --- | --- | --- |
| 21 | 16 | 4.557361e-08 | 12.07 | [Per-draw gradient norms](../../results/hybrid/calibration/seed-21.json) |
| 22 | 16 | 3.697337e-08 | 13.16 | [Per-draw gradient norms](../../results/hybrid/calibration/seed-22.json) |
| 23 | 16 | 4.530499e-08 | 11.47 | [Per-draw gradient norms](../../results/hybrid/calibration/seed-23.json) |
| 24 | 16 | 5.147323e-08 | 12.28 | [Per-draw gradient norms](../../results/hybrid/calibration/seed-24.json) |

## Adaptive minus comparator per seed

Positive Δwidth favors the adaptive schedule. Negative ΔNLL favors its prediction. Comparable fit uses the frozen 0.02-nat training threshold.

| Seed | Comparator | Δwidth gain | Δdev NLL | Δtrain NLL | Comparable fit |
| --- | --- | --- | --- | --- | --- |
| 21 | Fixed late hybrid | -0.058105 | -0.000205 | -0.000104 | yes |
| 22 | Fixed late hybrid | -0.052734 | -0.000143 | -0.000277 | yes |
| 23 | Fixed late hybrid | -0.054199 | -0.000204 | 0.000159 | yes |
| 24 | Fixed late hybrid | -0.054199 | -0.000203 | -0.000192 | yes |
| 22 | Cross-seed replay | -0.002930 | -0.000002 | -0.000018 | yes |
| 23 | Cross-seed replay | 0.000977 | 0.000003 | -0.000008 | yes |
| 24 | Cross-seed replay | -0.002441 | -0.000003 | -0.000006 | yes |
| 21 | Hessian trace | 0.002930 | 0.000005 | 0.000008 | yes |
| 22 | Hessian trace | 0.000000 | 0.000000 | 0.000003 | yes |
| 23 | Hessian trace | 0.001953 | 0.000004 | -0.000010 | yes |
| 24 | Hessian trace | 0.000000 | 0.000000 | 0.000000 | yes |
| 21 | Stronger trace | -0.017578 | -0.000102 | -0.000018 | yes |
| 22 | Stronger trace | -0.018066 | -0.000083 | -0.000074 | yes |
| 23 | Stronger trace | -0.020508 | -0.000094 | -0.000076 | yes |
| 24 | Stronger trace | -0.021973 | -0.000093 | -0.000321 | yes |
| 21 | Always-on hybrid | 0.041748 | -0.000015 | -0.000061 | yes |
| 22 | Always-on hybrid | -0.063965 | 0.000337 | 0.000030 | yes |
| 23 | Always-on hybrid | 0.050781 | -0.000626 | 0.001359 | yes |
| 24 | Always-on hybrid | 0.005127 | 0.000270 | 0.002343 | yes |

The completed branches reused 125,829,120 targets of optimization compared with independently training each branch from initialization. The replay permutation couples different seeds through their coefficient histories. The sign-test reference for this comparison assumes exchangeable independent pair signs. Shared donor histories make that assumption approximate. All raw pairs are reported for inspection.
