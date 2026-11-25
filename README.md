# Third derivatives in language-model training

Does a language model predict unseen tokens better when training penalizes rapid changes in the curvature of its loss? This project compares ordinary AdamW, Hessian-trace regularization, and a penalty on every third partial derivative of token cross-entropy with respect to the trainable weights. Its two experiments cover full-weight training on short stories and low-rank adaptation on research abstracts. The primary evidence is held-out loss at equal training tokens.

## Flat minima, Hessians and third derivatives in earlier work

| Setting | What the researchers used the derivatives for | Original papers and projects |
|---|---|---|
| Origin of flat-minimum search | Hochreiter and Schmidhuber searched for connected regions of weights where training error changes little. Their journal paper describes a search algorithm using second derivatives. | [Original NeurIPS paper, 1994](https://proceedings.neurips.cc/paper/1994/hash/01882513d5fa7c329e940dda99b12147-Abstract.html) · [Flat Minima, Neural Computation, 1997](https://people.idsia.ch/~juergen/fm/) |
| Hessians in language models | Sophia uses stochastic curvature estimates to precondition GPT training updates. Liu et al. measure Hessian trace and study downstream behavior of language models. Liu, Yu and Lin explicitly add trace to the objective in WikiText-2 LSTM and GRU experiments. | [Sophia paper](https://arxiv.org/pdf/2305.14342) · [Sophia code](https://github.com/Liuhong99/Sophia) · [Language-model flatness study](https://proceedings.mlr.press/v202/liu23ao.html) · [Explicit Hessian penalty, §5.2](https://arxiv.org/pdf/2208.05924) |
| Hessians outside language modeling | Layerwise Hessian-trace penalties have been tested in image classification. Reparameterization studies explain why a curvature measurement alone cannot establish predictive generalization. | [Sankar et al.](https://arxiv.org/pdf/2012.03801) · [Dinh et al.](https://proceedings.mlr.press/v70/dinh17b.html) |
| Third derivatives in language models | Yang et al. approximate third derivatives of the **training loss with respect to weights** to predict what happens when training batches are reordered. McGee et al. fit a cubic along a fine-tuning update to select a step size. Zhang and Wang test cubic corrections along hidden-activation interventions in a frozen model and report failures for large perturbations. | [FUT++, §5.1 and Appendix A.1](https://arxiv.org/pdf/2505.22042) · [Step selection, Appendix C.1.1](https://arxiv.org/pdf/2610.02190#page=28) · [Activation patching, §4 and supplement](https://arxiv.org/pdf/2606.09899) |
| Third derivatives outside LLMs | Wolinski projects third derivatives of the **weight-space loss** to regularize a local optimization model. Lellmann et al. study third **spatial** derivatives of terrain surfaces. Duchon gives the general squared-derivative roughness formulation. | [Projected parameter derivatives](https://arxiv.org/pdf/2312.03885) · [Third-order terrain reconstruction](https://www.lellmann.net/work/_media/lellmann_ssvm13.pdf) · [Spline roughness](https://doi.org/10.1007/BFb0086566) |

These papers motivate a distinct experiment here: putting the squared norm of the **third derivative of next-token loss with respect to trainable weights** directly in the training objective. The reviewed studies leave its effect on held-out next-token loss open.

The third-order term measures how the Hessian changes as weights move. Two independent random sign vectors estimate its squared Frobenius norm. Differentiating the estimate gives the optimizer a fourth-derivative contribution. This combines an order-three roughness density with matrix-free norm estimation. [Duchon](https://doi.org/10.1007/BFb0086566) · [Bujanović and Kressner](https://arxiv.org/pdf/2004.06433) · [Hessian comparator](https://arxiv.org/pdf/2208.05924)

**Study record.** The protocol and run matrix precede model execution. Experiments, scientific conclusions, and generated examples will be recorded from raw artifacts here. [Preregistration](reports/preregistration.md) · [Run matrix](reports/planned-runs.md) · [Literature](reports/literature-review.md) · [State of the art](reports/state-of-the-art-review.md) · [Progress](reports/progress.md)

<!-- RESULTS:START -->
[Explore the results](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss/) · [Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)

Recorded 9 runs, including 9 with a completed summary.

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**TinyStories development pilot.** At 2,097,152 training targets, the third-order run recorded 0.00080 nats per target token higher against Ordinary AdamW, 0.00247 nats per target token lower against Hessian trace. These are single-seed descriptions using initial pilot strengths.

### Measured scores

| Stage | Phase | Method | Ratio | Tokens/run | Runs | Median dev NLL | Median test NLL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | control | Initial checkpoint | 0.000 | 0 | 1 | 8.3437 | — |
| TinyStories | control | Unigram | 0.000 | 0 | 1 | 6.0036 | — |
| TinyStories | pilot | Ordinary AdamW | 0.000 | 2,097,152 | 1 | 3.8770 | — |
| TinyStories | pilot | Third derivative | 0.010 | 2,097,152 | 1 | 3.8769 | — |
| TinyStories | pilot | Third derivative | 0.030 | 2,097,152 | 1 | 3.8778 | — |
| TinyStories | pilot | Third derivative | 0.100 | 2,097,152 | 1 | 3.8827 | — |
| TinyStories | pilot | Hessian trace | 0.010 | 2,097,152 | 1 | 3.8773 | — |
| TinyStories | pilot | Hessian trace | 0.030 | 2,097,152 | 1 | 3.8802 | — |
| TinyStories | pilot | Hessian trace | 0.100 | 2,097,152 | 1 | 3.8979 | — |

![Parameter-space computation graph](docs/figures/architecture.png)

![Development NLL](docs/figures/curves.png)

### Recorded predictions

First archived sample in run-ID order per stage and method. [All continuations](reports/experiments/experiments.md)

<details><summary>TinyStories · Initial checkpoint</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     break painted pleaseerp gif neat lead bro comfort rid shr search impressedosairs try ants oss note daughter woodLater rest independent stars stonesiver mixaybe Le spoon readMe fingersiew embar bached mail

</details>

<details><summary>TinyStories · Unigram</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     it said her mom girlan he said that fell flut back's hard. a them into work protectt hug?" his and little teeth "What sky some Timmy and on 
     down As's
     very

</details>

<details><summary>TinyStories · Ordinary AdamW</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Third derivative</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Hessian trace</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>
<!-- RESULTS:END -->

## Reproduce the study

Use Python 3.12, uv, and an NVIDIA GPU for the full study. Install with `uv sync --locked`, run `uv run pytest -q`, then use `uv run thirdloss study`. In another terminal run `uv run thirdloss dashboard` for live accuracy and loss. Regenerate the paper, plots and score tables with `uv run thirdloss report`. [Setup, checkpoints and CLI](docs/runbook.md) · [Document splits](docs/data.md) · [Model collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

The pipeline pins the source texts, splits by document, learns the stories tokenizer using training documents, and freezes the evaluation definition. Identical initializations and document orders pair the competing objectives. The smaller model trains all weights. The pretrained model trains only attention adapters. Examine both improvement and deterioration across seeds and both computational budgets. [TinyStories](https://arxiv.org/pdf/2305.07759) · [Pythia](https://huggingface.co/EleutherAI/pythia-410m) · [Common Pile](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered) · [LoRA](https://arxiv.org/pdf/2106.09685)

## Milestones

- Publish the protocol, references and analysis decisions.
- Verify the scalar objective and its training gradient on analytical functions and a small Transformer.
- Train the pilot, publish throughput and establish feasibility on the local GPU.
- Complete controls, development selection, paired confirmations and a reproducible report.
