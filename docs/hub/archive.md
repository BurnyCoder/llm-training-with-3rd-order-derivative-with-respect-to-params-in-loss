---
language: [en]
tags: [scientific-research, causal-language-modeling]
---

# Third derivatives in language-model training

Does penalizing changes in loss curvature improve next-token prediction? The study compares ordinary AdamW, Hessian-trace regularization and the squared Frobenius norm of the third derivative with respect to trainable weights. Every trial, including the excluded numerical diagnostic, has a public record. [Paper](research/reports/paper.pdf) · [Current results](research/reports/summary.md) · [Interactive explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

<!-- COMPARISONS:START -->

## Results at a glance

**Lower next-token loss (NLL) is better** because the model assigns more probability to the tokens that actually came next. **Higher top-1 accuracy is better** because the model’s first guess is correct more often. Higher speed means more training targets per second. Lower peak memory uses fewer resources.

| Model and split | Matched evidence | Third-order NLL vs AdamW<br>↓ Lower is better | Third-order NLL vs trace<br>↓ Lower is better | Speed vs AdamW<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| TinyStories pretraining · test | 8/8 full-budget seeds | 0.000028 higher | 0.000222 lower | 69.4% slower |
| Pythia-410M adapters · dev | 3/8 full-budget seeds | 0.000008 lower | 0.000118 higher | 92.8% slower |

**Adaptive vs fixed-ramp hybrid** · 4/8 paired seeds. Adaptive development NLL was 0.000203 lower. It retained 0.0542 less directional width after the switch. Median final widths were 13.103 (adaptive) and 13.159 (fixed). More width is better for the registered geometry test. Whether more width improves prediction is unknown.

**TinyStories pretraining** · The registered test of superiority over both baselines was inconclusive. Third order had lower test NLL in 4/8 pairs against AdamW (Holm p = 0.63672) and 8/8 against Hessian trace (Holm p = 0.00781). **Pythia-410M adapters** · Awaiting paired test results (3 of 8 full-horizon training triplets).

[Side-by-side scores, accuracy, speed and memory](#side-by-side-comparisons) · [Flatness by variant and baseline](#all-variants-and-baselines) · [Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Paired tests and intervals](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

### Flatness at a glance

These medians compare the same seeds and training windows within each model family. Weight width measures how far the trainable weights can move before NLL rises by 0.1 nats. Score width applies the corresponding test to token scores in RMS logit units. Their relationship to held-out prediction is unknown.

| Model and matched cohort | Statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- | --- |
| TinyStories pretraining · 8/8 full-budget seeds | Directional width<br>↑ Wider is flatter | 12.807 | 12.899 | 12.913 |
| TinyStories pretraining · 8/8 full-budget seeds | RMS Hessian curvature<br>↓ Less local bending | 0.590453 | 0.581726 | 0.573339 |
| TinyStories pretraining · 8/8 full-budget seeds | Common score width<br>↑ More score tolerance | 1.0815 | 1.0815 | 1.0813 |
| Pythia-410M adapters · 3/8 full-budget seeds | Directional width<br>↑ Wider is flatter | 19.426 | 19.669 | 19.898 |
| Pythia-410M adapters · 3/8 full-budget seeds | RMS Hessian curvature<br>↓ Less local bending | 0.624617 | 0.624955 | 0.612819 |
| Pythia-410M adapters · 3/8 full-budget seeds | Common score width<br>↑ More score tolerance | 1.1047 | 1.1047 | 1.1049 |

[All variants, initial models and unigram references](#all-variants-and-baselines) · [Per-seed widths, search brackets and curvature](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/flatness.md)

### Current and planned runs

**Snapshot at 2026-11-26T07:05:21+00:00** · 195/305 experimental milestones complete.

**Recorded activity** · Between recorded training and scoring updates.

**Next scheduled work** · Research abstracts · Third derivative · confirm seed 4 (1%).

The measured remaining-time scenarios are 21.47–22.19 machine-hours.

[Finished, active and planned experiments](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/planned-runs.md#current-evidence-and-remaining-runs) · [Live measurements](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer)

## Side-by-side comparisons

Each row states which direction is better for that metric. Bold highlights the best observed value at the displayed precision. A tie means the paired difference rounds to zero. NLL is negative log-likelihood in nats per target. Perplexity is exp(NLL), computed for each run before taking medians. Compare it within a corpus and tokenizer. Accuracy differences use percentage points (pp). [Perplexity definition](https://huggingface.co/docs/transformers/perplexity)

### TinyStories pretraining

**Final test · 8/8 full-budget seeds · 16,777,216 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/stories.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Final test NLL<br>↓ Lower is better | **2.544147** | 2.544678 | 2.544355 | 0.000028 higher | 0.000222 lower |
| Final test perplexity<br>↓ Lower is better | **12.7324** | 12.7391 | 12.7350 | 0.0004 higher | 0.0028 lower |
| Final test accuracy<br>↑ Higher is better | **46.298%** | 46.297% | 46.297% | 0.004 pp lower | 0.004 pp higher |
| Development NLL<br>↓ Lower is better | **2.543536** | 2.544168 | 2.543755 | 0.000013 higher | 0.000228 lower |
| Development perplexity<br>↓ Lower is better | **12.7246** | 12.7326 | 12.7274 | 0.0002 higher | 0.0029 lower |
| Dev top-1 accuracy<br>↑ Higher is better | 46.281% | 46.283% | **46.284%** | Tie | 0.002 pp higher |
| Equal-time probe NLL<br>↓ Lower is better | **2.54525** | 2.73158 | 3.01822 | 0.47247 higher | 0.28542 higher |
| Training speed (targets/s)<br>↑ Higher is better | **131,161** | 69,899 | 40,104 | 69.4% slower | 42.4% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 608.2 | 608.2 | 608.2 | Tie | Tie |

The common training-time cutoff had a median of 127.9 seconds. The furthest checkpoint used for this row was 10.9 seconds before its cutoff.

The registered test of superiority over both baselines was inconclusive.

| Against | Paired Δtest NLL | Median interval | Wins/ties/losses | Holm p |
| --- | --- | --- | --- | --- |
| AdamW | +0.000028 | [-0.000682, +0.000436] | 4/0/4 | 0.63672 |
| Hessian trace | -0.000222 | [-0.000588, -0.000081] | 8/0/0 | 0.00781 |

A negative difference favors third order. A positive difference favors the named baseline. The interval shows uncertainty in the median difference. A smaller Holm-adjusted p-value gives stronger evidence for the registered improvement. [Test decision rule](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/preregistration.md)

### Pythia-410M adapters

**Full development split · 3/8 full-budget seeds · 524,288 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/abstracts.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | 3.037085 | **3.036959** | 3.037076 | 0.000008 lower | 0.000118 higher |
| Development perplexity<br>↓ Lower is better | 20.8444 | **20.8418** | 20.8442 | 0.0002 lower | 0.0025 higher |
| Dev top-1 accuracy<br>↑ Higher is better | 42.470% | 42.470% | **42.472%** | Tie | 0.002 pp higher |
| Equal-time probe NLL<br>↓ Lower is better | **3.00597** | 3.04877 | 3.13520 | 0.12923 higher | 0.08161 higher |
| Training speed (targets/s)<br>↑ Higher is better | **1,591** | 328 | 118 | 92.8% slower | 64.0% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 2,346.3 | 2,346.3 | 2,346.3 | Tie | Tie |

The common training-time cutoff had a median of 329.6 seconds. The furthest checkpoint used for this row was 234.1 seconds before its cutoff.

Peak host memory (lower uses less RAM) was AdamW 14.04 GiB, Hessian trace 14.04 GiB, Third order 14.04 GiB. This measure includes earlier work in each interpreter.

Awaiting paired test results (3 of 8 full-horizon training triplets).

The equal-time row uses the last available fixed-window development score at or before the fastest run’s finish time in each seed. Full-split NLL uses every development target. Training speed includes regularizer probes. Adapter derivatives use CPU float64 with one GPU reserved. [Timing definitions and checkpoint lags](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

### Flatness of the trained checkpoints

How far can the weights move before next-token loss rises by 0.1 nats on eight fixed training windows? We add the crossing distances on both sides of each of 16 unit directions, then take their median. **Wider is flatter** in these coordinates. Establishing a local minimum would also require a stationarity test. [Flat-minima paper](https://people.idsia.ch/~juergen/fm/node1.html) · [Coordinate dependence](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2)

**TinyStories hybrids** · Each row names the completed seeds. Switch and final widths are medians over those seeds. The final seed range shows the smallest and largest seed widths. The middle 50% column gives the medians of the within-seed directional quartiles. Spread has no preferred direction. A ray at the search limit supplies a lower bound.

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23, 24 | 15.172 | 13.103 | 13.001–13.215 | 12.933–13.331 | 0/128 |
| Fixed late hybrid | 21, 22, 23, 24 | 15.172 | 13.159 | 13.056–13.268 | 12.984–13.380 | 0/128 |
| Hessian trace | 21, 22, 23, 24 | 15.172 | 13.100 | 13.001–13.215 | 12.932–13.330 | 0/128 |
| Stronger trace | 21, 22, 23, 24 | 15.172 | 13.122 | 13.023–13.233 | 12.951–13.351 | 0/128 |
| Cross-seed replay | 22, 23, 24 | 15.201 | 13.047 | 13.004–13.218 | 12.880–13.366 | 0/96 |
| Always-on hybrid | 21, 22, 23, 24 | 15.277 | 13.161 | 13.060–13.334 | 13.022–13.389 | 0/128 |

#### All variants and baselines

Each row uses the same fixed training windows and probe directions within its stage. Parentheses give measured / planned seeds for that cell. Targets count next-token examples used for optimizer updates in this study. The unigram uses counts from the full training split, and initial Pythia retains its pretrained backbone. Compare rows with matching targets and seeds. Larger **weight width** means greater tolerance to moving the model’s trainable parameters. Larger **common score width** means that all token scores can tolerate a larger shared bias before NLL rises by 0.1 nats, measured in RMS logit units. The unigram has zero trainable model weights and shares the score test with every neural predictor. Small differences can fall inside the numerical search brackets. Both widths have an unknown relationship to better held-out prediction. [Per-run search brackets](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/flatness.md#per-run-checkpoint-measurements) · [All-model measurement design](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/amendments/all-model-flatness.md)

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
| Ordinary AdamW · confirmation | 524,288 | 1–8 | 19.426 (3/8) | 0.62462 (3/8) | 1.1047 (3/8) |
| Hessian trace · confirmation | 524,288 | 1–8 | 19.669 (3/8) | 0.62496 (3/8) | 1.1047 (3/8) |
| Third derivative · confirmation | 524,288 | 1–8 | 19.898 (3/8) | 0.61282 (3/8) | 1.1049 (3/8) |

<details><summary>Pythia-410M · adapter weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 65,536 | 0 | 19.775 (1/1) | 0.58335 (1/1) | 1.0929 (1/1) |
| Hessian trace (10%) | 65,536 | 0 | 19.856 (1/1) | 0.77214 (1/1) | 1.0930 (1/1) |
| Third derivative (3%) | 65,536 | 0 | 19.968 (1/1) | 0.56999 (1/1) | 1.0927 (1/1) |
| Third derivative (10%) | 65,536 | 0 | 19.997 (1/1) | 0.56095 (1/1) | 1.0926 (1/1) |
| Third derivative (3%) · excluded precision diagnostic | 65,536 | 0 | 19.885 (1/1) | 0.58797 (1/1) | 1.0932 (1/1) |

</details>

**TinyStories pretraining · full-budget checkpoints · seeds 1, 2, 3, 4, 5, 6, 7, 8 · 16,777,216 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 12.807 | 12.899 | 12.913 |
| Final width range across seeds<br>Descriptive spread | 12.542–12.963 | 12.638–13.044 | 12.667–13.101 |
| Middle 50% of directions<br>Descriptive spread | 12.567–13.040 | 12.684–13.125 | 12.714–13.115 |
| Rays at limit / tested<br>Measurement coverage | 0/256 | 0/256 | 0/256 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 2.58516 | 2.58323 | 2.58409 |
| RMS Hessian curvature<br>↓ Less local bending | 0.590453 | 0.581726 | 0.573339 |
| Signed Hessian trace / parameter<br>No general better direction | +0.00493753 | +0.00494619 | +0.00485706 |
| Common score width<br>↑ More score tolerance | 1.0815 | 1.0815 | 1.0813 |

**Pythia-410M adapters · full-budget checkpoints · seeds 1, 2, 3 · 524,288 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 19.426 | 19.669 | 19.898 |
| Final width range across seeds<br>Descriptive spread | 19.197–20.132 | 19.222–20.270 | 19.342–20.313 |
| Middle 50% of directions<br>Descriptive spread | 18.744–20.119 | 18.967–20.328 | 19.353–20.611 |
| Rays at limit / tested<br>Measurement coverage | 0/96 | 0/96 | 0/96 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 2.84244 | 2.84359 | 2.84535 |
| RMS Hessian curvature<br>↓ Less local bending | 0.624617 | 0.624955 | 0.612819 |
| Signed Hessian trace / parameter<br>No general better direction | +0.00186668 | +0.00159403 | +0.000399434 |
| Common score width<br>↑ More score tolerance | 1.1047 | 1.1047 | 1.1049 |

For the primary comparison, TinyStories uses all weights and Pythia uses the LoRA factors. Compare widths within each model. The link gives every run, directional bracket and Hessian probe. [Flatness statistics and raw files](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/flatness.md) · [Secondary measurement design](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/amendments/checkpoint-flatness.md)

### TinyStories hybrid schedules

**Adaptive vs fixed ramp · 4/8 paired seeds · 16,777,216 targets per run.** Both arms resume the same trace-trained checkpoint. Width change is final width minus width at the switch. A larger change means more width retained at the fixed loss tolerance. For two negative changes, the one closer to zero lost less width.

| Metric | Adaptive | Fixed ramp | vs Fixed ramp |
| --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **2.546107** | 2.546281 | 0.000203 lower |
| Development perplexity<br>↓ Lower is better | **12.7573** | 12.7596 | 0.0026 lower |
| Dev top-1 accuracy<br>↑ Higher is better | 46.205% | **46.208%** | 0.002 pp higher |
| Width change after switch<br>↑ More retained is better for the width test | -2.0865 | **-2.0311** | 0.0542 less retained |
| Training speed (targets/s)<br>↑ Higher is better | 39,820 | **40,902** | 2.6% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 617.3 | 617.3 | Tie |

The remaining controls are paired independently. Each row uses only seeds that finished both arms. The always-on arm has its own measured width at the switch.

| Adaptive versus | Paired seeds | Adaptive NLL<br>↓ Lower is better | Adaptive width change<br>↑ More retained is better for the width test | Adaptive speed<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| Cross-seed replay | 3/8 | 0.000002 lower | 0.0024 less retained | 3.1% faster |
| Hessian trace | 4/8 | 0.000002 higher | 0.0010 more retained | 35.2% slower |
| Stronger trace | 4/8 | 0.000094 lower | 0.0193 less retained | 35.6% slower |
| Always-on hybrid | 4/8 | 0.000127 higher | 0.0234 more retained | 33.4% faster |

**Registered width decision** · Awaiting eight paired width measurements. Width probes use fixed training windows. [Every width, training-fit flag, replay and paired difference](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/hybrid/results.md)

**Training diagnostics have no established better direction for held-out prediction.** A smaller derivative penalty meets its training objective more closely. The raw Hessian trace, third-derivative estimate, gradient norm and penalty strength describe the training process. Their predictive value is assessed separately by held-out NLL. [Objectives and endpoints](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/preregistration.md)

<details><summary>Squared-Hessian, scrambled-gradient, combined and untrained controls</summary>

**TinyStories pretraining** · Pilot seed, 2,097,152 training targets.

| Metric | Third order | Squared Hessian | Scrambled signs | Trace + third |
| --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **3.876931** | 3.878680 | 3.877253 | 3.877172 |
| Development perplexity<br>↓ Lower is better | **48.2758** | 48.3603 | 48.2914 | 48.2875 |
| Dev top-1 accuracy<br>↑ Higher is better | 32.326% | 32.299% | **32.331%** | 32.317% |
| Training speed (targets/s)<br>↑ Higher is better | 42,481 | **83,790** | 50,914 | 41,030 |
| Peak GPU allocation (MiB)<br>↓ Lower is better | **608.2** | **608.2** | 608.6 | 619.3 |

**Pythia-410M adapters** · Pilot seed, 65,536 training targets.

| Metric | Third order | Squared Hessian | Scrambled signs | Trace + third |
| --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | 3.114247 | **3.113905** | 3.114196 | 3.114281 |
| Development perplexity<br>↓ Lower is better | 22.5165 | **22.5088** | 22.5153 | 22.5172 |
| Dev top-1 accuracy<br>↑ Higher is better | 41.315% | **41.321%** | 41.316% | 41.316% |
| Training speed (targets/s)<br>↑ Higher is better | 189 | **413** | 171 | 137 |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 2,346.3 | 2,346.3 | 2,346.3 | 2,346.3 |

**Zero-update references** · The unigram uses training-split frequencies. Initial Pythia uses its pretrained weights.

| Stage | Initial NLL<br>↓ Lower is better | Unigram NLL<br>↓ Lower is better | Initial accuracy<br>↑ Higher is better | Unigram accuracy<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| TinyStories pretraining | 8.343680 | 6.003555 | 0.312% | 7.151% |
| Pythia-410M adapters | 3.251674 | 7.330611 | 39.911% | 6.023% |

</details>

### Same-prompt continuations

Each panel shows the first saved prompt and full continuations from the lowest matched seed. These examples have no quality rating. The method names link to the raw generations.

<details><summary>TinyStories pretraining · same prompt, seed 1</summary>

**Prompt** <samp>Once upon a time, there was a clever little dog named Max. Max loved</samp>

| [AdamW](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-confirm-s01-ce-r00/samples.jsonl) | [Hessian trace](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-confirm-s01-trace-r01/samples.jsonl) | [Third order](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-confirm-s01-third-r01/samples.jsonl) |
| --- | --- | --- |
| <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> | <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> | <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> |

</details>

<details><summary>Pythia-410M adapters · same prompt, seed 1</summary>

**Prompt** <samp>One of the central objectives of contemporary neuroimaging research is to<br>create predictive models</samp>

| [AdamW](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-confirm-s01-ce-r00/samples.jsonl) | [Hessian trace](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-confirm-s01-trace-r01-fp64/samples.jsonl) | [Third order](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-confirm-s01-third-r01-fp64/samples.jsonl) |
| --- | --- | --- |
| <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> | <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> | <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> |

</details>

<details><summary>TinyStories hybrid schedules · same prompt, seed 21</summary>

**Prompt** <samp>Once upon a time, there was a clever little dog named Max. Max loved</samp>

| [Adaptive](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-hybrid-s21-adaptive-r01/samples.jsonl) | [Fixed ramp](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-hybrid-s21-late-r01/samples.jsonl) |
| --- | --- |
| <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his house</samp> | <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his mail</samp> |

</details>

Seed sensitivity is the final stage, after both primary test evaluations, all hybrid replications and checkpoint flatness. [Final seed-sensitivity report](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/seed-sensitivity.md)

<!-- COMPARISONS:END -->

## Research materials

| Material | Hugging Face location |
|---|---|
| Complete Git tree, locked environment, tests and instructions | [Research tree](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research) · [README](research/README.md) |
| Literature, preregistration, raw observations and reviews | [Reports](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research/reports) · [Raw results](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research/results) |
| Timestamped training output, full prompts and completions, operator transcripts | [Log archive](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/logs) |
| Fitted models, model cards, optimizer moments, data cursor and random state | [Full-weight models](https://huggingface.co/BurnyCoder/thirdloss-stories) · [Pythia adapters](https://huggingface.co/BurnyCoder/thirdloss-pythia-410m-adapters) · [Pinned pretrained backbone](https://huggingface.co/EleutherAI/pythia-410m/tree/9879c9b5f8bea9051dcb0e68dff21493d67e9d4f) |
| Prepared training and evaluation data, tokenizers and overlap audits | [TinyStories](https://huggingface.co/datasets/BurnyCoder/thirdloss-tinystories-tokens) · [arXiv abstracts](https://huggingface.co/datasets/BurnyCoder/thirdloss-arxiv-abstracts-2024) |

From the research checkout, `uv run --locked thirdloss study --with-hybrid --with-flatness` reproduces both original stages, the hybrid comparisons and the weight- and score-space measurements. [Installation, data preparation and checkpoint loading](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/docs/runbook.md)

The publication receipt binds the Git commit to the verified file hashes across the collection. Run `uv run thirdloss audit-hub` from that checkout to independently compare the published objects. Log files are snapshots at publication time. Operational transcripts redact transport credentials and local account paths. [File digests and Git revision](publication.json)
