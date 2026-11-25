---
language: [en]
tags: [scientific-research, causal-language-modeling]
---

# Third derivatives in language-model training

Does penalizing changes in loss curvature improve next-token prediction? The study compares ordinary AdamW, Hessian-trace regularization and the squared Frobenius norm of the third derivative with respect to trainable weights. Every trial, including the excluded numerical diagnostic, has a public record. [Paper](research/reports/paper.pdf) · [Current results](research/reports/summary.md) · [Interactive explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

<!-- COMPARISONS:START -->

## Results at a glance

Lower next-token loss (NLL) means a model assigned more probability to the words that actually came next. Training speed counts target tokens per second.

| Model and split | Matched evidence | Third-order NLL vs AdamW | Third-order NLL vs trace | Speed vs AdamW |
| --- | --- | --- | --- | --- |
| TinyStories pretraining · dev | one development pilot seed | 0.000045 lower | 0.000338 lower | 65.7% slower |
| Pythia-410M adapters · dev | one development pilot seed | 0.000300 higher | 0.000273 higher | 88.6% slower |

**Adaptive vs fixed-ramp hybrid** · 2/8 paired seeds. Adaptive development NLL was 0.000174 lower. It retained 0.0554 less directional width after the switch.

Both primary test decisions are pending. Each stage requires eight paired test seeds and superiority over both baselines under Holm correction.

[Side-by-side scores, accuracy, speed, memory and width](#side-by-side-comparisons) · [Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Paired tests and intervals](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

## Side-by-side comparisons

↓ means lower is preferred. ↑ means higher is preferred. Bold highlights the best observed value when methods differ at the displayed precision. A tie means the paired difference rounds to zero. NLL is negative log-likelihood in nats per target. Accuracy differences use percentage points (pp).

### TinyStories pretraining

**Full development split · one development pilot seed · 2,097,152 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. The pilot also selected the derivative strengths. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/stories.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL ↓ | 3.876976 | 3.877269 | **3.876931** | 0.000045 lower | 0.000338 lower |
| Dev top-1 accuracy ↑ | **32.337%** | 32.329% | 32.326% | 0.011 pp lower | 0.003 pp lower |
| Equal-time probe NLL ↓ | **3.82905** | 4.04765 | 4.95277 | 1.12372 higher | 0.90512 higher |
| Training speed ↑ (targets/s) | **123,871** | 73,185 | 42,481 | 65.7% slower | 42.0% slower |
| Peak GPU allocation ↓ (MiB) | 608.2 | 608.2 | 608.2 | Tie | Tie |

These early TinyStories pilots share the initialization seed and identical first-update token count, loss, accuracy and gradient norm. Initial weight digests were first recorded in later runs. [First-update records](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

The common training-time cutoff had a median of 16.9 seconds. The furthest checkpoint used for this row was 2.3 seconds before its cutoff.

Awaiting paired test results (0 of 8 full-horizon training triplets).

### Pythia-410M adapters

**Full development split · one development pilot seed · 65,536 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. The pilot also selected the derivative strengths. [Strength selection](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/results/selection/abstracts.json) · [Experiment ledger](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL ↓ | **3.113948** | 3.113974 | 3.114247 | 0.000300 higher | 0.000273 higher |
| Dev top-1 accuracy ↑ | **41.321%** | **41.321%** | 41.315% | 0.006 pp lower | 0.006 pp lower |
| Training speed ↑ (targets/s) | **1,659** | 435 | 189 | 88.6% slower | 56.5% slower |
| Peak GPU allocation ↓ (MiB) | 2,346.3 | 2,346.3 | 2,346.3 | Tie | Tie |

An equal-time NLL comparison is pending because at least one arm lacks a recorded development checkpoint at or before the shared cutoff.

Observed host-process memory high-water marks were AdamW 3.78 GiB, Hessian trace 10.28 GiB, Third order 13.09 GiB. This measure includes earlier work in each interpreter.

Awaiting paired test results (0 of 8 full-horizon training triplets).

The equal-time row uses the last available fixed-window development score at or before the fastest run’s finish time in each seed. Full-split NLL uses every development target. Training speed includes regularizer probes. Adapter derivatives use CPU float64 with one GPU reserved. [Timing definitions and checkpoint lags](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/summary.md)

### TinyStories hybrid schedules

**Adaptive vs fixed ramp · 2/8 paired seeds · 16,777,216 targets per run.** Both arms resume the same trace-trained checkpoint. Width change is final width minus width at the switch. A larger change means more width retained at the fixed loss tolerance.

| Metric | Adaptive | Fixed ramp | vs Fixed ramp |
| --- | --- | --- | --- |
| Development NLL ↓ | **2.546107** | 2.546281 | 0.000174 lower |
| Dev top-1 accuracy ↑ | 46.205% | **46.208%** | 0.002 pp lower |
| Width change after switch ↑ | -2.0865 | **-2.0311** | 0.0554 less retained |
| Training speed ↑ (targets/s) | **40,983** | 40,328 | 1.5% faster |
| Peak GPU allocation ↓ (MiB) | 617.3 | 617.3 | Tie |

The remaining controls are paired independently. Each row uses only seeds that finished both arms. The always-on arm has its own measured width at the switch.

| Adaptive versus | Paired seeds | Adaptive NLL | Adaptive width change | Adaptive speed |
| --- | --- | --- | --- | --- |
| Cross-seed replay | 1/8 | 0.000002 lower | 0.0029 less retained | 3.1% faster |
| Hessian trace | 2/8 | 0.000002 higher | 0.0015 more retained | 35.0% slower |
| Stronger trace | 2/8 | 0.000092 lower | 0.0178 less retained | 35.5% slower |
| Always-on hybrid | 2/8 | 0.000161 higher | 0.0111 less retained | 48.0% faster |

**Registered width decision** · Awaiting eight paired width measurements. Width probes use fixed training windows. [Every width, training-fit flag, replay and paired difference](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/reports/hybrid/results.md)

<details><summary>Squared-Hessian, scrambled-gradient, combined and untrained controls</summary>

**TinyStories pretraining** · Pilot seed, 2,097,152 training targets.

| Metric | Third order | Squared Hessian | Scrambled signs | Trace + third |
| --- | --- | --- | --- | --- |
| Development NLL ↓ | **3.876931** | 3.878680 | 3.877253 | 3.877172 |
| Dev top-1 accuracy ↑ | 32.326% | 32.299% | **32.331%** | 32.317% |
| Training speed ↑ (targets/s) | 42,481 | **83,790** | 50,914 | 41,030 |
| Peak GPU allocation ↓ (MiB) | **608.2** | **608.2** | 608.6 | 619.3 |

**Pythia-410M adapters** · Secondary pilot comparisons are pending.

**Untrained references · zero training targets**

| Stage | Initial NLL ↓ | Unigram NLL ↓ | Initial accuracy ↑ | Unigram accuracy ↑ |
| --- | --- | --- | --- | --- |
| TinyStories pretraining | 8.343680 | 6.003555 | 0.312% | 7.151% |
| Pythia-410M adapters | 3.251674 | 7.330611 | 39.911% | 6.023% |

</details>

### Same-prompt continuations

Each panel shows the first saved prompt and full continuations from the lowest matched seed. The method names link to the raw generations.

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
| Prepared training and evaluation data, tokenizers and overlap audits | [TinyStories](https://huggingface.co/datasets/BurnyCoder/thirdloss-tinystories-tokens) · [arXiv abstracts](https://huggingface.co/datasets/BurnyCoder/thirdloss-arxiv-abstracts-2024-tokens) |

The publication receipt binds the Git commit to the verified file hashes across the collection. Run `uv run thirdloss audit-hub` from that checkout to independently compare the published objects. Log files are snapshots at publication time. Operational transcripts redact transport credentials and local account paths. [File digests and Git revision](publication.json)
