# Third derivatives in language-model training

Does a language model predict unseen tokens better when training penalizes rapid changes in the curvature of its loss? This project compares ordinary AdamW, Hessian-trace regularization, and a penalty on the squared third derivatives of next-token loss. It trains a TinyStories decoder from scratch and fine-tunes Pythia-410M’s low-rank attention adapters on research abstracts. [Study design](reports/planned-runs.md)

## Can the penalty favor a wider minimum?

A minimum is **wide** if the weights can move a long way before the loss rises by a chosen amount. Near a smooth minimum, the Hessian trace predicts the average loss increase from a small nudge in a uniformly random direction. The third derivative measures **how curvature changes** as weights move. If curvature starts small and changes slowly nearby, the loss can stay low over a larger distance. [Basin width, Definition 1](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2) · [Hessian and random perturbations, equation 4](https://arxiv.org/pdf/2306.08553#page=5)

The penalty can help weights **stay** near a flat bottom. For $L(w)=w^4$, nudging the weight to either side makes the penalty rise, so a small descent step pulls it back. A steep quadratic such as $L(w)=100w^2$ has constant curvature and receives zero third-derivative penalty everywhere. [Worked examples](docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum)

In the language models, an active update measures curvature change for the next-token cross-entropy of **two text windows**, with respect to all decoder weights for TinyStories or only the adapter weights for Pythia. Differentiating this penalty gives AdamW a fourth-derivative contribution. Whether the models **find wider minima** is a hypothesis. The registered comparison tests whether they predict held-out tokens better at equal training-token counts. [Training update](docs/third-derivative-penalty.md#the-actual-training-update) · [Preregistration](reports/preregistration.md)

![One-weight loss and penalty curves. At the asymmetric minimum the trace pushes left and the third-derivative penalty pushes right. In the quartic both pull displaced weights back. In the steep quadratic both penalty curves are constant.](docs/figures/penalty-directions.png)

*Analytic examples. The circles mark the ordinary loss minima. Arrows show downhill directions for the two penalties. Each panel has its own vertical scale.*

## Flat minima, Hessians and third derivatives in earlier work

| Setting | What the researchers used the derivatives for | Original papers and projects |
|---|---|---|
| Origin of flat-minimum search | Hochreiter and Schmidhuber searched for connected regions of weights where training error changes little. Their journal paper describes a search algorithm using second derivatives. | [Original NeurIPS paper, 1994](https://proceedings.neurips.cc/paper/1994/hash/01882513d5fa7c329e940dda99b12147-Abstract.html) · [Flat Minima, Neural Computation, 1997](https://people.idsia.ch/~juergen/fm/) |
| Hessian penalties in language models | Zhang, Li and Ju approximate a Hessian-trace penalty with symmetric weight perturbations when fine-tuning GPT-2 on CommonsenseQA and StrategyQA. Liu, Yu and Lin propose a signed trace objective and report WikiText-2 LSTM and GRU experiments. | [GPT-2 experiments, Table 5](https://arxiv.org/pdf/2306.08553#page=12) · [Noise stability optimization code](https://github.com/VirtuosoResearch/Noise-stability-optimization) · [Recurrent LM penalty, §5.2](https://arxiv.org/pdf/2208.05924) |
| Other uses of Hessians in LLMs | Sophia uses stochastic curvature estimates to precondition GPT training updates. Liu et al. measure Hessian trace and study the downstream behavior of pretrained language models. | [Sophia paper](https://arxiv.org/pdf/2305.14342) · [Sophia code](https://github.com/Liuhong99/Sophia) · [Language-model flatness study](https://proceedings.mlr.press/v202/liu23ao.html) |
| Hessians outside language modeling | Layerwise Hessian-trace penalties have been tested in image classification. Reparameterization studies explain why a curvature measurement alone cannot establish predictive generalization. | [Sankar et al.](https://arxiv.org/pdf/2012.03801) · [Dinh et al.](https://proceedings.mlr.press/v70/dinh17b.html) |
| Third derivatives in language models | Yang et al. approximate third derivatives of the **training loss with respect to weights** to predict what happens when training batches are reordered. McGee et al. fit a cubic along a fine-tuning update to select a step size. Zhang and Wang test cubic corrections along hidden-activation interventions in a frozen model and report failures for large perturbations. | [FUT++, §5.1 and Appendix A.1](https://arxiv.org/pdf/2505.22042) · [Step selection, Appendix C.1.1](https://arxiv.org/pdf/2610.02190#page=28) · [Activation patching, §4 and supplement](https://arxiv.org/pdf/2606.09899) |
| Third derivatives outside LLMs | Wolinski projects third derivatives of the **weight-space loss** to regularize a local optimization model. Lellmann et al. study third **spatial** derivatives of terrain surfaces. Duchon gives the general squared-derivative roughness formulation. | [Projected parameter derivatives](https://arxiv.org/pdf/2312.03885) · [Third-order terrain reconstruction](https://www.lellmann.net/work/_media/lellmann_ssvm13.pdf) · [Spline roughness](https://doi.org/10.1007/BFb0086566) |
| Third derivatives in image classifiers | Grad-CAM++ uses diagonal third derivatives of a class score with respect to convolutional feature activations to locate image regions that contribute to a prediction. | [Chattopadhyay et al., equation 10](https://arxiv.org/pdf/1710.11063#page=4) · [Authors’ implementation](https://github.com/adityac94/Grad_CAM_plus_plus) |

Two independent random sign vectors estimate the squared Frobenius norm of the minibatch third derivative, including mixed partials between different weights. [Estimator derivation](docs/third-derivative-penalty.md#why-two-independent-sign-vectors-work-for-any-smooth-loss) · [Duchon](https://doi.org/10.1007/BFb0086566) · [Bujanović and Kressner](https://arxiv.org/pdf/2004.06433)

The protocol and run matrix were published before model execution. The scores, comparisons and continuations below are regenerated from each run’s raw records. [Preregistration](reports/preregistration.md) · [Run matrix](reports/planned-runs.md) · [Literature](reports/literature-review.md) · [State of the art](reports/state-of-the-art-review.md) · [Progress](reports/progress.md)

A same-probe check on pretrained Pythia found that single-precision arithmetic materially changed the third-order training gradient. The first adapter pilot is archived as a numerical diagnostic. The corrected adapter arms evaluate derivatives in double precision while ordinary training and prediction use the GPU. [Pre-test precision amendment](reports/amendments/adapter-precision.md) · [Full-model numerical checks](results/verification)

<!-- RESULTS:START -->
[Explore the results](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss/) · [Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)

Recorded 17 runs, including 17 with a completed summary.

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**TinyStories development pilot.** At 2,097,152 training targets, the third-order run recorded 0.00004 nats per target token lower against Ordinary AdamW, 0.00024 nats per target token lower against Trace + third derivative, 0.00175 nats per target token lower against Squared Hessian norm, 0.00032 nats per target token lower against Randomized gradient signs, 0.00034 nats per target token lower against Hessian trace. These are single-seed descriptions using selected on development.

**Research abstracts development pilot.** At 65,536 training targets, the third-order run recorded 0.00091 nats per target token higher against Ordinary AdamW. These are single-seed descriptions using initial pilot strengths.

### Measured scores

| Stage | Phase | Method | Ratio | Tokens/run | Runs | Median dev NLL | Median test NLL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | control | Initial checkpoint | 0.000 | 0 | 1 | 3.2517 | — |
| Research abstracts | control | Unigram | 0.000 | 0 | 1 | 7.3306 | — |
| Research abstracts | pilot | Ordinary AdamW | 0.000 | 65,536 | 1 | 3.1139 | — |
| Research abstracts | diagnostic | Third derivative | 0.030 | 65,536 | 1 | 3.1168 | — |
| Research abstracts | pilot | Third derivative | 0.030 | 65,536 | 1 | 3.1149 | — |
| TinyStories | control | Initial checkpoint | 0.000 | 0 | 1 | 8.3437 | — |
| TinyStories | control | Unigram | 0.000 | 0 | 1 | 6.0036 | — |
| TinyStories | pilot | Ordinary AdamW | 0.000 | 2,097,152 | 1 | 3.8770 | — |
| TinyStories | pilot | Trace + third derivative | 0.010 | 2,097,152 | 1 | 3.8772 | — |
| TinyStories | pilot | Squared Hessian norm | 0.030 | 2,097,152 | 1 | 3.8787 | — |
| TinyStories | pilot | Randomized gradient signs | 0.010 | 2,097,152 | 1 | 3.8773 | — |
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

<details><summary>Research abstracts · Initial checkpoint</summary>

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     that will be used by neuroscience researchers to
    identify cases of a disease or to select appropriate therapeutic intervention.
    
    The research of Peter Seager and colleagues has demonstrated that the brain
    can

</details>

<details><summary>Research abstracts · Unigram</summary>

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     neural. is novel In used describe sacrific the theruction
     To their
    zo than chronic current the the factor an( simultaneouslyrelated
    exchange
    purpose,) was} standards
     of
     radio.

</details>

<details><summary>Research abstracts · Ordinary AdamW</summary>

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     that will accurately predict the behavior of
    patient-specific neurological disorders such as epilepsy. In this paper, we
    present a novel dataset of EEG data recorded from children with focal
    subcortical epilepsy

</details>

<details><summary>Research abstracts · Third derivative</summary>

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     that will accurately predict the behavior of
    patient-specific neurological disorders such as epilepsy. In this paper, we
    present a novel dataset of EEG data recorded from children with focal
    subcortical epilepsy

</details>

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

<details><summary>TinyStories · Trace + third derivative</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Squared Hessian norm</summary>

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Randomized gradient signs</summary>

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

Use Python 3.12, uv, and an NVIDIA GPU for the full study. Install with `uv sync --locked`, run `uv run thirdloss verify`, then use `uv run thirdloss study`. In another terminal run `uv run thirdloss dashboard --port 18765` for live accuracy and loss. Regenerate the paper, plots and score tables with `uv run thirdloss report`. [Setup, checkpoints and CLI](docs/runbook.md) · [Document splits](docs/data.md) · [Model collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

The pipeline pins the source texts, splits by document, learns the stories tokenizer using training documents, and freezes the evaluation definition. Identical initializations and document orders pair the competing objectives. The smaller model trains all weights. The pretrained model trains only attention adapters. Examine both improvement and deterioration across seeds and both computational budgets. [TinyStories](https://arxiv.org/pdf/2305.07759) · [Pythia](https://huggingface.co/EleutherAI/pythia-410m) · [Common Pile](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered) · [LoRA](https://arxiv.org/pdf/2106.09685)

## Milestones

- Publish the protocol, references and analysis decisions.
- Verify the scalar objective and its training gradient on analytical functions and a small Transformer.
- Train the pilot, publish throughput and establish feasibility on the local GPU.
- Complete controls, development selection, paired confirmations and a reproducible report.
