# Research plan

<!-- STATUS:START -->

## Current evidence

**Snapshot at 2026-11-26T09:32:34+00:00** · 200/305 experimental milestones complete.

**Recorded activity** · Between recorded training and scoring updates.

**Next scheduled work** · Research abstracts · Third derivative · confirm seed 5 (1%).

The measured remaining-time scenarios are 18.87–19.51 machine-hours.

**TinyStories.** The registered test of superiority over both baselines was inconclusive. Third order had lower test NLL in 4/8 pairs against AdamW (Holm p = 0.63672) and 8/8 against Hessian trace (Holm p = 0.00781).

**Research abstracts.** Awaiting paired test results (4 of 8 full-horizon training triplets).

TinyStories hybrid follow-up: 23 of 48 full runs and 5 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements. [Hybrid results](hybrid/results.md)

[Execution matrix](planned-runs.md#current-evidence-and-remaining-runs) · [Flatness ledger](flatness.md)

<!-- STATUS:END -->

Hochreiter and Schmidhuber hypothesized that, at comparable training loss, a model in a broad region of acceptable weights may need fewer bits to describe and may generalize better. This study asks whether penalizing variation in token-loss curvature improves held-out predictions at equal training tokens. It compares methods within a small decoder trained from scratch and within the trainable attention adapters of a pretrained decoder on a second corpus. [*Flat Minima*, §1](https://people.idsia.ch/~juergen/fm/node1.html) · [Preregistration](preregistration.md) · [Run matrix and optimizer settings](planned-runs.md)

| Phase | Deliverable and release criterion |
|---|---|
| Prior work and registration | Publish the comparison with earlier Hessian penalties, directional weight derivatives and spline roughness, the full run matrix, and the decision rule before observing model scores. [Literature review](literature-review.md) · [State of the art](state-of-the-art-review.md) |
| Implementation and verification | Publish the locked source and tests. Verify both the sampled penalty and its training gradient analytically, numerically on a Transformer, and through optimizer updates. Verify restart fidelity and adapter export. [Checks](../results/verification/tests.json) · [Numerical review](reviews/adapter-verification.md) |
| Data preparation | Pin source revisions, deduplicate documents, audit cross-split word-shingle overlap, and record token-stream digests. Reserve the official stories validation split and June abstracts for the final evaluation. [Preparation guide](../docs/data.md) · [Manifests](../results/datasets) |
| Pilot and controls | Start with third-order training and the untrained model and unigram comparisons. Calibrate on training gradients, finish equal-budget strength searches and select on development NLL. Compare signed trace, squared Hessian norm, randomized third-order gradient signs, and the combined objective. [Run matrix](planned-runs.md) · [Selections](../results/selection) |
| Feasibility | Target the first pilot and free controls within fourteen hours. Use observed token throughput, validation time and peak allocated memory to project the week’s work before opening either test set. [Progress and timing](progress.md) |
| Confirmation | Use eight paired seeds per stage for ordinary AdamW, Hessian trace, and the selected third-order penalty. Freeze all stage checkpoints and the test digest before scoring. Report seed-level differences, median intervals, both Holm-adjusted sign tests, development results at matched training time, and compute costs. [Analysis decisions](preregistration.md) |
| Publication | After each completed run or evaluation, update the research archive, model card, experiment log, learnings, paper and explorer from the same raw observations. [Experiment ledger](experiments/experiments.md) · [Paper](paper.pdf) · [Explorer](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/) |

The dated progress record gives completed milestones and outstanding work. Source code, token-stream digests, restartable checkpoint settings and reload instructions are available from the reproduction guide. [Progress](progress.md) · [Reproduction guide](../docs/runbook.md)

Seed sensitivity is the final analysis. Complete all single-seed variants and controls in both model families, run the first full-budget paired seed in each, finish the registered primary studies and their frozen tests, and then finish the pending hybrid replications. After every checkpoint has its geometry, seal the inputs and summarize variability across seeds. [Execution-order amendment](amendments/seed-sensitivity-last.md) · [Final report](seed-sensitivity.md)

## Late third-derivative regularization

The fixed late ramp, curvature-dependent rule, cross-seed replay and controls are now registered for execution. [Hybrid preregistration and run matrix](hybrid/preregistration.md)

- [x] Preregister the trace-first TinyStories experiment. The token switch, ramp, cap and stronger-trace matching procedure were published before the first branch. [Frozen specification](hybrid/preregistration.md) · [Run ledger](hybrid/results.md)

One candidate is a linear ramp. If $n_t$ is the number of training tokens before update $t$, $n_0$ is the switch and $R>0$ is the ramp length in tokens, set $s_t=\min(1,\max(0,(n_t-n_0)/R))$ and $\lambda_{3,t}=\lambda_{\max}s_t$. Use the same cap for the curvature-dependent comparison. [Objective, schedules and width equations in the paper’s final appendix](paper.pdf)

**Rationale.** Near a smooth minimum, the trace favors low average curvature. If curvature starts changing faster as weights move toward the edge of a flat region, the third-derivative penalty grows and its gradient can oppose that movement. Delaying the penalty gives the trace time to act and saves the early fourth-derivative computations. A stronger trace alone could explain any benefit. For $L(w)=w^4$, the two penalties are proportional and can produce exactly the same pull. In a related CIFAR-10 experiment, switching from SGD to sharpness-aware minimization late gave nearly the same test error as using it throughout. [Worked examples](../docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum) · [Zhou et al., Figure 1](https://proceedings.iclr.cc/paper_files/paper/2025/file/35d5ad984cc0ddd84c6f1c177a2066e5-Paper-Conference.pdf#page=2)

**Comparisons.** For each seed, branch from the same trace-trained weights and AdamW state. Continue with trace alone, increase trace alone, or add the third-derivative term. Use the same ramp for both increases. On training batches, match the norm of the extra trace gradient to that of the added penalty gradient before clipping. Compare timing against a fourth run using both penalties from the start. Match initialization, data order and training tokens across runs.

**Readouts.** At the switch and at prespecified later checkpoints, perturb the weights both ways along fixed unit vectors. Measure the width between the first points where unregularized next-token loss on fixed training examples rises by a prespecified amount. For each seed, compare the change in median width between arms. If stronger trace preserves as much width, the result weakens the case for a distinct third-derivative effect. Compare held-out development loss at equal tokens. A width gain accompanied by lower development loss at comparable training fit would be consistent with the flat-minima hypothesis. A width gain alone would support only the geometric prediction. [Width definition](../docs/third-derivative-penalty.md#from-a-local-penalty-to-basin-width)

### Curvature-dependent penalty weight

- [x] Preregister the curvature-dependent alternative to the fixed-token switch. Each seed branches from the same trace-trained weights and AdamW state. After the low-loss criterion is met, falling RMS curvature can increase the squared third-derivative coefficient. The cap and running maximum preserve the strongest penalty reached. [Frozen rule and controls](hybrid/preregistration.md) · [Coefficient rule and quartic counterexample](../docs/third-derivative-penalty.md#weighting-the-penalty-by-curvature)

**Measurement.** Use past training-only Hessian-vector probes to estimate root-mean-square curvature in the TinyStories weight coordinates. Signed trace can be small when positive and negative eigenvalues cancel. Freeze the warm-up, loss criterion, probe interval, averaging window, curvature threshold and coefficient cap before comparing runs. Treat the coefficient as constant during each gradient update. Record the coefficient, curvature, training loss and gradient norm, including seeds where the coefficient stays zero. [Existing probe](../src/thirdloss/penalties.py)

**Test of the rationale.** Compare against trace alone, stronger trace and the fixed-token schedule at equal training tokens with the same monitoring budget. To test whether adapting to each run matters, replay the adaptive coefficient histories across seeds using a permutation fixed in advance. This preserves the set of coefficient histories while breaking their link to the receiving run's curvature. The geometric prediction is better retention of median directional width from the shared checkpoint at comparable training fit. Equal or narrower widths than the fixed or replayed schedules weaken that claim. Evaluate held-out development NLL separately for predictive benefit. [Width and timing comparisons](#late-third-derivative-regularization)
