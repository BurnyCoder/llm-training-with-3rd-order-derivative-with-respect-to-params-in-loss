# Independent scientific audit

26 November 2026. This review uses the frozen protocols, Git history, checkpoint fingerprints, prepared token streams and individual measurement records. The scope is the next-token prediction experiment and its registered directional-width follow-up. No model was trained, loaded for prediction or scored during this audit. [Primary protocol](../preregistration.md) · [Follow-up protocol](../hybrid/preregistration.md) · [Reproduction instructions](../../docs/runbook.md#reproducing-the-scientific-audit)

<!-- FINDINGS:START -->

Audited run and measurement records through Git `fbed4e55af1235a1ee44100e8e5fb6ee8cda6a0b`. [Machine-readable calculations, checkpoint and split fingerprints](../../results/analysis/scientific-audit.json)

### Frozen predictive endpoints

| Corpus and comparator | Seed wins / ties / losses | Median ΔNLL | Marginal median interval | Coverage | Raw p | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| TinyStories · Ordinary AdamW | 4 / 0 / 4 | +0.000027967 | [-0.000682177, +0.000436282] | 99.21875% | 0.63671875 | 0.63671875 |
| TinyStories · Hessian trace | 8 / 0 / 0 | -0.000221889 | [-0.000587950, -0.000080743] | 99.21875% | 0.00390625 | 0.00781250 |

**TinyStories** has 8 completed full-budget training triplets and 24 final test scores in this snapshot. The freeze commit contained their final weights' digests and unscored summaries. The paired arms used 8 distinct initializations across seeds. The released stream supplies 4,884,130 next-token targets. [Checkpoint freeze](https://github.com/BurnyCoder/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/commit/109d82420a331281159b9c2ef6a9db45d5a7d374) · [First public score commit](https://github.com/BurnyCoder/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/commit/46ec97f2807a6ff65fc29b78db0f8762437528a1)

**Research abstracts** has 4 completed full-budget training triplets and 0 final test scores in this snapshot.

### Passage overlap and actual training exposure

The post-hoc copy check found exact passages of at least 50 tokens in 26 of 21,990 test stories. At the registered training horizon, the sampled windows contained such passages from 3–11 test stories per seed. The archived test losses cover the whole split. Their sensitivity to removing these stories is unknown.

Across the prepared training pool, 29 maximal matching span pairs cover 1,446 distinct positions in the test stream, with 159 distinct starts of matching 50-token windows. The longest spans 81 tokens. Positions count token IDs on either side of the within-window next-token shift. Repeated matches contribute once to the union.

| Seed | Distinct test token positions in qualifying training windows | Affected test stories |
|---:|---:|---:|
| 1 | 410 | 7 |
| 2 | 331 | 6 |
| 3 | 634 | 11 |
| 4 | 343 | 6 |
| 5 | 422 | 7 |
| 6 | 398 | 7 |
| 7 | 521 | 9 |
| 8 | 172 | 3 |

### Width, numerical checks and coverage

Adaptive was narrower than the fixed ramp in 4 bracket-resolved pairs. Even the most favorable completion of the eight planned pairs gives raw p ≥ 0.63671875. The registered joint width-superiority criterion is unreachable.

An interval below zero establishes a narrower measured width gain over the comparator. An interval crossing zero leaves the sign unresolved at the stored search precision.

| Seed | Shared-trunk comparator | Midpoint Δwidth gain | Bounds from ray search | Sign |
|---:|---|---:|---:|---|
| 21 | late | -0.058105469 | [-0.060058594, -0.056152344] | narrower |
| 22 | late | -0.052734375 | [-0.054687500, -0.050781250] | narrower |
| 23 | late | -0.054199219 | [-0.056152344, -0.052246094] | narrower |
| 24 | late | -0.054199219 | [-0.056152344, -0.052246094] | narrower |
| 22 | replay | -0.002929688 | [-0.004882812, -0.000976562] | narrower |
| 23 | replay | +0.000976562 | [-0.000976562, +0.002929688] | unresolved |
| 24 | replay | -0.002441406 | [-0.004394531, -0.000488281] | narrower |

The incomplete run `abstracts-confirm-s05-third-r01-fp64` has a saved restart at update 448 (458,752 targets). The last logged update was 464. [Archived restart receipt](https://huggingface.co/BurnyCoder/thirdloss-pythia-410m-adapters/blob/d67fb076e614e6c8699b85be96ce5475b7e5314a/paused-runs/abstracts-confirm-s05-third-r01-fp64/step-000448-3e1a9558aa99/training_state.pt)

On 32,768 training targets the batch-size benchmark recorded 13,185 correct at batch 2 and 13,184 at batch 16. The aggregate counts leave token-by-token prediction agreement undetermined. The selected-minus-reference NLL difference was -1.8227729e-07 nats per target.

Recomputing the difference from the two archived FP64 derivative arrays gives relative L2 error 1.416496e-05 and cosine 0.999999999903 on the numerical reference case.

Reconciled 89 completed summaries, 85 fitted weight files, 76 terminal full-development log entries and 24 test coverage logs. Also reconstructed 74 follow-up width files, 87 checkpoint weight-space records and 89 score-space records from their directional data. [Run-level evidence](../../results/analysis/scientific-audit.json)

<!-- FINDINGS:END -->

## What the experiments establish

**Prediction.** The third-order intervention produced lower aggregate test NLL than the signed-trace intervention across the paired TinyStories seeds. Ordinary AdamW won as often as it lost. The registered claim required superiority over both comparators. It was inconclusive. An equivalence margin and an equivalence test would be needed to establish practical equality. Effects refer to the fixed, packed test stream, chosen model, development-selected coefficients and training budget. Seeds jointly vary initialization, data order and probe randomness. Tokens and rays within a seed supply no further independent training replications. [Exact sign test](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/signtest.htm) · [Holm adjustment](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html) · [Quantile intervals, equation 30](https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2119.pdf#page=41) · [Individual differences](../../results/analysis/scientific-audit.json)

**Isolation of the test set.** The normalized document hashes and source IDs have empty pairwise split intersections in both prepared corpora. The original filter used whole-document five-word shingles and Jaccard similarity of at least four fifths. Exact copied *passages* survive that rule. The post-hoc search counted contiguous equal token IDs wholly inside documents and then intersected each match with the actual sampled training windows. Windows and exposure are paired across methods within a seed. Shared exposure permits different model responses. The occurrence of a passage establishes neither memorization nor the sign or size of bias in any contrast. The test archive contains aggregate NLLs and coverage records. Removing affected documents requires document-level losses, which were never saved. The June abstract token file stayed sealed. Metadata-only checks cannot rule out passage, paraphrase or upstream pretraining overlap. [Preparation and split definitions](../../docs/data.md) · [Training-order implementation](../../src/thirdloss/windows.py) · [Exact-substring precedent](https://aclanthology.org/2022.acl-long.577/)

**Width and schedule.** The measured endpoint is the median two-sided crossing distance over fixed directions at a specified training-loss increase. It depends on the selected windows, parameterization, tolerance and sampled rays. A checkpoint need not be a local minimum. A sampled radius grid can miss an earlier sub-grid excursion. The numerical contrast bounds propagate the archived brackets and cancel the identical trunk where its checkpoint digest and restart agree. The fixed-ramp observations mathematically preclude the registered joint superiority result even under the most favorable completion. This is a bound on the final decision, without an interim significance or harm test. Remaining pairs still matter for the final effect size and for comparisons with the other schedules. In the replay arm, adjacent contrasts reuse an adaptive donor trajectory. The exact independent-sign reference distribution and nominal median-interval coverage have no demonstrated justification for that comparison. Pilot controls and the hybrid development loss remain descriptive. [Raw ray brackets](../hybrid/results.md) · [Schedule and donor assignment](../hybrid/preregistration.md) · [Independent pairs in the sign test](https://doi.org/10.1080/01621459.1946.10501898) · [Parameterization dependence and volume flatness](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2)

**Numerical amendment.** The FP32 Pythia pilot remains a diagnostic. Agreement of the two FP64 derivative arrays on the archived case supports that calculation at that point. Accuracy of all subsequent gradients cannot be inferred from that case. The scoring benchmark tested absolute differences in the *number correct*. Distinct predicted token IDs can give exactly the same total. This corrects the interpretation of “one top-one prediction” in the historical amendment. Overall benchmark NLL, speed and resource measurements survive this distinction. The archive cannot verify tokenwise agreement or supply a final June generalization verdict. [Pre-test amendment](../amendments/adapter-precision.md) · [Scoring measurements](../../results/verification/pythia-scoring-batches.json) · [Eligibility implementation](../../src/thirdloss/probe_check.py) · [FP64 measurements](../../results/verification/pythia-fp64-agreement.json)

## Evidence for the remaining claim families

The preprocessing rules gave held-out documents priority when filtering duplicates from development and training. Building the corpus therefore consulted held-out document signatures. The freeze chronology verifies when model scoring was published. It leaves the earlier, registered preprocessing access visible. [Split construction](../../docs/data.md) · [Frozen primary protocol](../preregistration.md)

| Published quantity or claim | What was verified and where the evidence ends |
|---|---|
| Objective, gradient and baseline definitions | With fixed minibatch and independent unit-variance sign probes, expanding the squared contraction cancels mixed-index cross terms in expectation. Autograd differentiates through the resulting norm. The trace arm uses the signed trace. The squared-Hessian control measures a different norm. The two-window objective, random gate and gradient clipping limit the interpretation of the applied updates. In particular, the expected squared norm of a minibatch tensor includes minibatch variability. It can differ from the squared norm for the full-corpus loss. [Algebra and exact toy examples](../../docs/third-derivative-penalty.md) · [Implemented contractions](../../src/thirdloss/penalties.py) · [Gradient accumulation](../../src/thirdloss/objectives.py) · [Rank-one estimation](https://arxiv.org/pdf/2004.06433) |
| Sources, parameters and strength selection | The input revisions, effective trainable coordinates, split and checkpoint fingerprints bind the packed inputs and configurations. The selection used the full development NLL of the equal-budget seed-zero grid and independently calibrated coefficients. Search and controls on one seed cannot demonstrate robustness to strength or seed choice. The pretrained base also differs from the full-weight stage in corpus, tokenizer, optimizer horizon and coordinate set. [Raw selections](../../results/selection/) · [Calibration draws](../../results/calibration/) · [LoRA](https://arxiv.org/abs/2106.09685) · [Literature review and release-code qualification](../literature-review.md) |
| Prediction tables and plots | NLL is the mean negative log probability over all valid target positions, in nats. Accuracy is the fraction with a correct top-one ID. Perplexity is the exponential of each run's token-mean NLL. Tables use the median of the displayed per-run measure. Dev learning curves and clock-matched observations use fixed windows. Aggregate recomputation checks identities, counts, and underlying saved summaries. Reconstructing logits or scoring new subsets would require predictions. [Evaluation code](../../src/thirdloss/evaluation.py) · [Log-to-report mapping](../../src/thirdloss/report_records.py) · [Perplexity and context](https://huggingface.co/docs/transformers/perplexity) |
| Time and resources | The two clocks use the latest logged measurement at or before the shortest final time in the triplet. Gaps to the cutoff and token horizons can differ. The supplementary clock subtracts host derivative calls including transfers. It estimates a particular accounting convention. Allocated GPU memory, process high-water memory and wall-time forecasts have distinct denominators. [Per-method timestamps](../../results/analysis/scientific-audit.json) · [Timing implementation](../../src/thirdloss/train.py) · [Forecast assumptions](../../results/feasibility/) |
| Geometry, controls and mechanism | Per-direction endpoints reconstruct width bounds and median widths. Logged probes reconstruct score-space curvature and weight-space estimates where available. RMS weight curvature estimates magnitude including both signs. Signed trace allows cancellation. Score-space probes perturb predictive logits. Samples, sample-wise text quality and geometry do not test causal mediation of held-out loss. Fixed-prompt generations are examples of model output, including any factual errors in their content. [Raw geometry ledger](../flatness.md) · [Weight probes](../../src/thirdloss/checkpoint_flatness.py) · [Score probes](../../src/thirdloss/score_flatness.py) · [Example selection](../../src/thirdloss/report_records.py) |
| Novelty, external precedents and historical records | Earlier studies establish specific objectives or examples in their own settings. The local comparison adapts them and supplies its own evidence. The literature search cannot establish historical priority. Frozen registrations, amendments, raw outputs and earlier reviews document what was originally proposed or observed. Numerical corrections and limitations in this review apply to current interpretation. [Prior work and implementation differences](../state-of-the-art-review.md) · [Liu, Yu and Lin](https://arxiv.org/pdf/2208.05924) · [Zhang, Li and Ju](https://arxiv.org/pdf/2306.08553) · [Machine-learning reporting checklist](https://neurips.cc/public/guides/PaperChecklist) |

The public report now requires the actual stage freeze, checkpoint and initialization digests, corpus manifest, held-out split hash, and correct denominator before issuing a confirmatory verdict. The frozen score file test does not replace auditing the chronology of data access. Git establishes which named records existed in the published history. It cannot certify every private action before publication. [Report validation](../../src/thirdloss/analysis.py) · [Independent calculations](../../src/thirdloss/scientific_audit.py)
