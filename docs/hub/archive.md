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
| TinyStories pretraining · dev | one development pilot seed | 0.000045 lower | 0.000338 lower | 65.7% slower |
| Pythia-410M adapters · dev | one development pilot seed | 0.000300 higher | 0.000273 higher | 88.6% slower |

**Adaptive vs fixed-ramp hybrid** · 3/8 paired seeds. Adaptive development NLL was 0.000204 lower. It retained 0.0542 less directional width after the switch. Median final widths were 13.157 (adaptive) and 13.215 (fixed). More width is better for the registered geometry test. Whether more width improves prediction is unknown.

Both primary test decisions are pending. Each stage requires eight paired test seeds and superiority over both baselines under Holm correction.

[Side-by-side scores, accuracy, speed and memory](#side-by-side-comparisons) · [Flatness by variant and baseline](#all-variants-and-baselines) · [Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Paired tests and intervals](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

## Side-by-side comparisons

Each row states which direction is better for that metric. Bold highlights the best observed value at the displayed precision. A tie means the paired difference rounds to zero. NLL is negative log-likelihood in nats per target. Accuracy differences use percentage points (pp).

### TinyStories pretraining

**Full development split · one development pilot seed · 2,097,152 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. The pilot also selected the derivative strengths. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/stories.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | 3.876976 | 3.877269 | **3.876931** | 0.000045 lower | 0.000338 lower |
| Dev top-1 accuracy<br>↑ Higher is better | **32.337%** | 32.329% | 32.326% | 0.011 pp lower | 0.003 pp lower |
| Equal-time probe NLL<br>↓ Lower is better | **3.82905** | 4.04765 | 4.95277 | 1.12372 higher | 0.90512 higher |
| Training speed (targets/s)<br>↑ Higher is better | **123,871** | 73,185 | 42,481 | 65.7% slower | 42.0% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 608.2 | 608.2 | 608.2 | Tie | Tie |

These early TinyStories pilots share the initialization seed and identical first-update token count, loss, accuracy and gradient norm. Initial weight digests were first recorded in later runs. [First-update records](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

The common training-time cutoff had a median of 16.9 seconds. The furthest checkpoint used for this row was 2.3 seconds before its cutoff.

Awaiting paired test results (0 of 8 full-horizon training triplets).

### Pythia-410M adapters

**Full development split · one development pilot seed · 65,536 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. The pilot also selected the derivative strengths. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/abstracts.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **3.113948** | 3.113974 | 3.114247 | 0.000300 higher | 0.000273 higher |
| Dev top-1 accuracy<br>↑ Higher is better | **41.321%** | **41.321%** | 41.315% | 0.006 pp lower | 0.006 pp lower |
| Training speed (targets/s)<br>↑ Higher is better | **1,659** | 435 | 189 | 88.6% slower | 56.5% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 2,346.3 | 2,346.3 | 2,346.3 | Tie | Tie |

An equal-time NLL comparison is pending because at least one arm lacks a recorded development checkpoint at or before the shared cutoff.

Peak host memory (lower uses less RAM) was AdamW 3.78 GiB, Hessian trace 10.28 GiB, Third order 13.09 GiB. This measure includes earlier work in each interpreter.

Awaiting paired test results (0 of 8 full-horizon training triplets).

The equal-time row uses the last available fixed-window development score at or before the fastest run’s finish time in each seed. Full-split NLL uses every development target. Training speed includes regularizer probes. Adapter derivatives use CPU float64 with one GPU reserved. [Timing definitions and checkpoint lags](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

### Flatness of the trained checkpoints

How far can the weights move before next-token loss rises by 0.1 nats on eight fixed training windows? We add the crossing distances on both sides of each of 16 unit directions, then take their median. **Wider is flatter** in these coordinates. Establishing a local minimum would also require a stationarity test. [Flat-minima paper](https://people.idsia.ch/~juergen/fm/node1.html) · [Coordinate dependence](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2)

**TinyStories hybrids** · Each row names the completed seeds. Switch and final widths are medians over those seeds. The final seed range shows the smallest and largest seed widths. The middle 50% column gives the medians of the within-seed directional quartiles. Spread has no preferred direction. A ray at the search limit supplies a lower bound.

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23 | 15.143 | 13.157 | 13.048–13.215 | 12.984–13.368 | 0/96 |
| Fixed late hybrid | 21, 22, 23 | 15.143 | 13.215 | 13.103–13.268 | 13.036–13.411 | 0/96 |
| Hessian trace | 21, 22, 23 | 15.143 | 13.154 | 13.046–13.215 | 12.984–13.366 | 0/96 |
| Stronger trace | 21, 22, 23 | 15.143 | 13.175 | 13.069–13.233 | 13.002–13.387 | 0/96 |
| Cross-seed replay | 22, 23 | 15.198 | 13.133 | 13.047–13.218 | 12.933–13.431 | 0/64 |
| Always-on hybrid | 21, 22, 23 | 15.256 | 13.229 | 13.060–13.334 | 13.085–13.390 | 0/96 |

#### All variants and baselines

Each row uses the same fixed training windows and probe directions within its stage. Parentheses give measured / planned seeds for that cell. Targets count next-token examples used for optimizer updates in this study. The unigram uses counts from the full training split, and initial Pythia retains its pretrained backbone. Compare rows with matching targets and seeds. Larger **weight width** means greater tolerance to moving the model’s trainable parameters. Larger **common score width** means that all token scores can tolerate a larger shared bias before NLL rises by 0.1 nats, measured in RMS logit units. The unigram has zero trainable model weights and shares the score test with every neural predictor. Both widths have an unknown relationship to better held-out prediction. [All-model measurement design](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/amendments/all-model-flatness.md)

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
| Shared trace checkpoint | 8,388,608 | 21–28 | 15.172 (4/8) | 0.44445 (4/8) | 1.062 (4/8) |
| Curvature-dependent hybrid · hybrid study | 16,777,216 | 21–28 | 13.157 (3/8) | 0.585 (3/8) | 1.083 (3/8) |
| Fixed late hybrid · hybrid study | 16,777,216 | 21–28 | 13.215 (3/8) | 0.5776 (3/8) | 1.082 (3/8) |
| Hessian trace · hybrid study | 16,777,216 | 21–28 | 13.154 (3/8) | 0.5854 (3/8) | 1.083 (3/8) |
| Stronger trace · hybrid study | 16,777,216 | 21–28 | 13.175 (3/8) | 0.58362 (3/8) | 1.083 (3/8) |
| Cross-seed replay · hybrid study | 16,777,216 | 21–28 | 13.133 (2/8) | 0.5891 (2/8) | 1.082 (2/8) |
| Always-on hybrid · hybrid study | 16,777,216 | 21–28 | 13.229 (3/8) | 0.57089 (3/8) | 1.082 (3/8) |

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
| Initial checkpoint | 0 | 0 | 21.890 (1/1) | 0.69058 (1/1) | 1.086 (1/1) |
| Unigram | 0 | 0 | N/A · no weights | N/A · no weights | 0.915 (1/1) |
| Ordinary AdamW | 65,536 | 0 | 19.784 (1/1) | 1.2868 (1/1) | 1.093 (1/1) |
| Hessian trace (1%) | 65,536 | 0 | 19.751 (1/1) | 1.1818 (1/1) | 1.093 (1/1) |
| Third derivative (1%) | 65,536 | 0 | 19.922 (1/1) | 0.58227 (1/1) | 1.093 (1/1) |
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

**TinyStories pretraining · development pilots · seeds 0 · 2,097,152 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 15.579 | 15.686 | 15.640 |
| Final width range across seeds<br>Descriptive spread | One seed | One seed | One seed |
| Middle 50% of directions<br>Descriptive spread | 15.297–16.037 | 15.431–16.102 | 15.382–16.118 |
| Rays at limit / tested<br>Measurement coverage | 0/32 | 0/32 | 0/32 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 3.84335 | 3.84501 | 3.84377 |
| RMS Hessian curvature<br>↓ Lower means less local bending | 0.453288 | 0.447721 | 0.447394 |
| Signed Hessian trace / parameter<br>No general better direction | +0.0036281 | +0.00356145 | +0.00357761 |

**Pythia-410M adapters · development pilots · seeds 0 · 65,536 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 19.784 | 19.751 | 19.922 |
| Final width range across seeds<br>Descriptive spread | One seed | One seed | One seed |
| Middle 50% of directions<br>Descriptive spread | 19.185–20.320 | 19.179–20.260 | 19.400–20.421 |
| Rays at limit / tested<br>Measurement coverage | 0/32 | 0/32 | 0/32 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 2.91035 | 2.91018 | 2.91090 |
| RMS Hessian curvature<br>↓ Lower means less local bending | 1.28684 | 1.18181 | 0.582266 |
| Signed Hessian trace / parameter<br>No general better direction | +0.00312322 | +0.00404879 | +0.00146738 |

For the primary comparison, TinyStories uses all weights and Pythia uses the LoRA factors. Compare widths within each model. The link gives every run, directional bracket and Hessian probe. [Flatness statistics and raw files](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/flatness.md) · [Secondary measurement design](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/amendments/checkpoint-flatness.md)

### TinyStories hybrid schedules

**Adaptive vs fixed ramp · 3/8 paired seeds · 16,777,216 targets per run.** Both arms resume the same trace-trained checkpoint. Width change is final width minus width at the switch. A larger change means more width retained at the fixed loss tolerance. For two negative changes, the one closer to zero lost less width.

| Metric | Adaptive | Fixed ramp | vs Fixed ramp |
| --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **2.545908** | 2.546113 | 0.000204 lower |
| Dev top-1 accuracy<br>↑ Higher is better | 46.256% | **46.258%** | 0.001 pp lower |
| Width change after switch<br>↑ More retained is better for the width test | -1.9854 | **-1.9272** | 0.0542 less retained |
| Training speed (targets/s)<br>↑ Higher is better | 37,992 | **40,662** | 3.9% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 617.3 | 617.3 | Tie |

The remaining controls are paired independently. Each row uses only seeds that finished both arms. The always-on arm has its own measured width at the switch.

| Adaptive versus | Paired seeds | Adaptive NLL<br>↓ Lower is better | Adaptive width change<br>↑ More retained is better for the width test | Adaptive speed<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| Cross-seed replay | 2/8 | 0.000001 higher | 0.0010 less retained | 5.4% faster |
| Hessian trace | 3/8 | 0.000004 higher | 0.0020 more retained | 36.3% slower |
| Stronger trace | 3/8 | 0.000094 lower | 0.0181 less retained | 37.0% slower |
| Always-on hybrid | 3/8 | 0.000015 lower | 0.0417 more retained | 44.2% faster |

**Registered width decision** · Awaiting eight paired width measurements. Width probes use fixed training windows. [Every width, training-fit flag, replay and paired difference](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/hybrid/results.md)

**Training diagnostics have no established better direction for held-out prediction.** A smaller derivative penalty meets its training objective more closely. The raw Hessian trace, third-derivative estimate, gradient norm and penalty strength describe the training process. Their predictive value is assessed separately by held-out NLL. [Objectives and endpoints](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/preregistration.md)

<details><summary>Squared-Hessian, scrambled-gradient, combined and untrained controls</summary>

**TinyStories pretraining** · Pilot seed, 2,097,152 training targets.

| Metric | Third order | Squared Hessian | Scrambled signs | Trace + third |
| --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **3.876931** | 3.878680 | 3.877253 | 3.877172 |
| Dev top-1 accuracy<br>↑ Higher is better | 32.326% | 32.299% | **32.331%** | 32.317% |
| Training speed (targets/s)<br>↑ Higher is better | 42,481 | **83,790** | 50,914 | 41,030 |
| Peak GPU allocation (MiB)<br>↓ Lower is better | **608.2** | **608.2** | 608.6 | 619.3 |

**Pythia-410M adapters** · Secondary pilot comparisons are pending.

**Zero-update references** · The unigram uses training-split frequencies. Initial Pythia uses its pretrained weights.

| Stage | Initial NLL<br>↓ Lower is better | Unigram NLL<br>↓ Lower is better | Initial accuracy<br>↑ Higher is better | Unigram accuracy<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| TinyStories pretraining | 8.343680 | 6.003555 | 0.312% | 7.151% |
| Pythia-410M adapters | 3.251674 | 7.330611 | 39.911% | 6.023% |

</details>

### Same-prompt continuations

Each panel shows the first saved prompt and full continuations from the lowest matched seed. These examples have no quality rating. The method names link to the raw generations.

<details><summary>TinyStories pretraining · same prompt, seed 0</summary>

**Prompt** <samp>Once upon a time, there was a clever little dog named Max. Max loved</samp>

| [AdamW](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-pilot-s00-ce-r00/samples.jsonl) | [Hessian trace](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-pilot-s00-trace-r01/samples.jsonl) | [Third order](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-pilot-s00-third-r01/samples.jsonl) |
| --- | --- | --- |
| <samp> to play on the cat.</samp> | <samp> to play on the cat.</samp> | <samp> to play on the cat.</samp> |

</details>

<details><summary>Pythia-410M adapters · same prompt, seed 0</summary>

**Prompt** <samp>One of the central objectives of contemporary neuroimaging research is to<br>create predictive models</samp>

| [AdamW](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-pilot-s00-ce-r00/samples.jsonl) | [Hessian trace](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-pilot-s00-trace-r01-fp64/samples.jsonl) | [Third order](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/abstracts-pilot-s00-third-r01-fp64/samples.jsonl) |
| --- | --- | --- |
| <samp> that will accurately predict the behavior of<br>patient-specific neurological disorders such as epilepsy. In this paper, we<br>present a novel dataset of EEG data recorded from children with focal<br>subcortical epilepsy</samp> | <samp> that will be used to assess the cognitive<br>performance of neurological disorders. We will focus on three major areas:<br>(1) the nervous system as a whole, (2) the brain regions that</samp> | <samp> that will accurately predict the behavior of<br>patient-specific neurological disorders such as epilepsy. In this paper, we<br>present a novel dataset of EEG data recorded from children with focal<br>subcortical epilepsy</samp> |

</details>

<details><summary>TinyStories hybrid schedules · same prompt, seed 21</summary>

**Prompt** <samp>Once upon a time, there was a clever little dog named Max. Max loved</samp>

| [Adaptive](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-hybrid-s21-adaptive-r01/samples.jsonl) | [Fixed ramp](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/stories-hybrid-s21-late-r01/samples.jsonl) |
| --- | --- |
| <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his house</samp> | <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his mail</samp> |

</details>

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
