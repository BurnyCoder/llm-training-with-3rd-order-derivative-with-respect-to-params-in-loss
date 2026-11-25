# Third derivatives in language-model training

Sepp Hochreiter and Jürgen Schmidhuber proposed that **among models that fit the training data equally well, those in flatter minima may generalize better to unseen data**. In a flat minimum, many nearby weight settings still fit. If some weights can be rounded more coarsely without spoiling the fit, a good predictor can take fewer bits to describe under a fixed encoding. Their minimum-description-length argument links that shorter description to a lower risk of overfitting. [Hochreiter and Schmidhuber, *Flat Minima* (1997), §1](https://people.idsia.ch/~juergen/fm/node1.html)

**Why did earlier papers use the Hessian?** At a smooth minimum the gradient is zero, whether the valley is sharp or flat. The Hessian gives a quadratic approximation to how much training loss rises when the weights move. For small steps of equal size in uniformly random directions, the predicted average rise is proportional to the **Hessian trace**, the sum of second derivatives along the weight coordinates. The researchers penalized the trace to favor fits that tolerate small weight changes and tested whether those fits generalize better. [Liu, Yu and Lin, §§3.2–3.3](https://arxiv.org/pdf/2208.05924#page=3) · [Zhang, Li and Ju, equation 4](https://arxiv.org/pdf/2306.08553#page=5)

Sankar et al. observed that layerwise traces fell during image-classifier training and tried penalizing them directly. Liu, Yu and Lin drew on a generalization bound for linear classifiers to motivate a stochastic trace penalty and reported WikiText-2 experiments with LSTMs and GRUs. Zhang, Li and Ju paired opposite weight perturbations so the first-order loss changes would cancel, giving them a way to target curvature during GPT-2 fine-tuning for question answering. [Sankar et al., Figure 5 and Table 1](https://arxiv.org/pdf/2012.03801#page=6) · [Liu, Yu and Lin, §5.2](https://arxiv.org/pdf/2208.05924#page=10) · [Zhang, Li and Ju, Table 5](https://arxiv.org/pdf/2306.08553#page=12)

**Why third derivatives?** Two minima can have the same small curvature at the bottom, yet one can steepen much sooner. The third derivatives of next-token loss measure how its Hessian changes as the weights move. The training penalty estimates their sum of squares, so rapid changes of either sign carry a cost. If curvature starts small and changes slowly throughout a neighborhood, the weights can move farther while loss stays low. [Worked examples and width bound](docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum) · [Taylor remainder, equation 22](https://link.springer.com/article/10.1007/s10288-023-00541-9)

The registered study tests whether this penalty improves prediction on unseen tokens compared with ordinary AdamW and Hessian-trace regularization at equal training-token counts. It trains a TinyStories decoder from scratch and fine-tunes Pythia-410M’s low-rank attention adapters on research abstracts. [Study design](reports/planned-runs.md)

**Why add the third-derivative penalty late?** Even a steep valley can have constant curvature. The registered TinyStories follow-up first trains with the Hessian-trace penalty to favor low average curvature. Its fixed-ramp arm keeps the trace active and gradually adds the third-derivative penalty after the midpoint. If curvature changes faster toward the edge of a flat region, the penalty can increase outward and oppose that movement. Delaying it also avoids early fourth-derivative computations. If the schedule preserves a wider region, its final weights should tolerate larger perturbations than the trace controls at the same allowed increase in unregularized loss. [Timing controls and width measurement](reports/hybrid/preregistration.md) · [Measured widths](reports/hybrid/results.md)

**Should the penalty get stronger as curvature falls?** The TinyStories follow-up keeps the trace active and turns up the **weight on the squared third derivatives** once training loss is low and recent Hessian measurements are small. It retains the highest weight reached, up to a cap. Eight paired seeds compare this rule with a fixed late ramp, another seed’s schedule, trace alone, stronger trace and an always-on hybrid. The endpoints are directional width on fixed training windows and development next-token loss. Direct division can act in the opposite direction. For $L(w)=w^4$, the squared ratio $(L'''/L'')^2=4/w^2$ grows without bound as weights approach the flat bottom. [Derivation](docs/third-derivative-penalty.md#weighting-the-penalty-by-curvature) · [Hybrid preregistration and run matrix](reports/hybrid/preregistration.md)

## Can the penalty favor a wider minimum?

A minimum is **wide** if the weights can move a long way before the loss rises by a chosen amount. [Basin width, Definition 1](https://proceedings.mlr.press/v70/dinh17b/dinh17b.pdf#page=2)

The penalty can help weights **stay** near a flat bottom. For $L(w)=w^4$, nudging the weight to either side makes the penalty rise, so a small descent step pulls it back. A steep quadratic such as $L(w)=100w^2$ has constant curvature and receives zero third-derivative penalty everywhere. [Worked examples](docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum)

In the language models, an active update measures curvature change for the next-token cross-entropy of **two text windows**, with respect to all decoder weights for TinyStories or only the adapter weights for Pythia. Differentiating this penalty gives AdamW a fourth-derivative contribution. The primary comparison tests prediction on held-out tokens at equal training-token counts. The hybrid follow-up measures changes in directional width in fixed weight coordinates, since rescaling weights can change measured sharpness while preserving predictions. [Training update](docs/third-derivative-penalty.md#the-actual-training-update) · [Primary preregistration](reports/preregistration.md) · [Hybrid preregistration](reports/hybrid/preregistration.md) · [Dinh et al.](https://proceedings.mlr.press/v70/dinh17b.html)

![One-weight loss and penalty curves. At the asymmetric minimum the trace pushes left and the third-derivative penalty pushes right. In the quartic both pull displaced weights back. In the steep quadratic both penalty curves are constant.](docs/figures/penalty-directions.png)

*Analytic examples. The circles mark the ordinary loss minima. Arrows show downhill directions for the two penalties. Each panel has its own vertical scale.*

## Flat minima, Hessians and third derivatives in earlier work

| Setting | What the researchers used the derivatives for | Original papers and projects |
|---|---|---|
| Origin of flat-minimum search | Hochreiter and Schmidhuber searched for connected regions of weights where training error changes little. Their flatness penalty depends on the sensitivity of network outputs to the weights. Differentiating that penalty uses second derivatives of the outputs. | [Original NeurIPS paper, 1994](https://proceedings.neurips.cc/paper/1994/hash/01882513d5fa7c329e940dda99b12147-Abstract.html) · [Flat Minima (1997), equations 1–2](https://people.idsia.ch/~juergen/fm/node3.html) |
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
[Explore the results](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/) · [Hugging Face explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Hugging Face collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378) · [Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)

Recorded 29 runs, including 28 with a completed summary.

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

TinyStories hybrid follow-up: 5 of 48 full runs and 1 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements. [Width measurements, scores and controls](reports/hybrid/results.md)

![Directional width by TinyStories arm and seed](docs/figures/hybrid_width.png)

**TinyStories development pilot.** At 2,097,152 training targets, the third-order run recorded 0.00004 nats per target token lower against Ordinary AdamW, 0.00024 nats per target token lower against Trace + third derivative, 0.00175 nats per target token lower against Squared Hessian norm, 0.00032 nats per target token lower against Randomized gradient signs, 0.00034 nats per target token lower against Hessian trace. These are single-seed descriptions using strengths selected on development.

**Research abstracts development pilot.** At 65,536 training targets, the third-order run recorded 0.00030 nats per target token higher against Ordinary AdamW, 0.00027 nats per target token higher against Hessian trace. These are single-seed descriptions using strengths selected on development.

### Measured scores

| Stage | Phase | Method | Ratio | Tokens/run | Runs | Median dev NLL | Median test NLL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | control | Initial checkpoint | 0.000 | 0 | 1 | 3.2517 | — |
| Research abstracts | control | Unigram | 0.000 | 0 | 1 | 7.3306 | — |
| Research abstracts | pilot | Ordinary AdamW | 0.000 | 65,536 | 1 | 3.1139 | — |
| Research abstracts | pilot | Third derivative | 0.010 | 65,536 | 1 | 3.1142 | — |
| Research abstracts | diagnostic | Third derivative | 0.030 | 65,536 | 1 | 3.1168 | — |
| Research abstracts | pilot | Third derivative | 0.030 | 65,536 | 1 | 3.1149 | — |
| Research abstracts | pilot | Third derivative | 0.100 | 65,536 | 1 | 3.1163 | — |
| Research abstracts | pilot | Hessian trace | 0.010 | 65,536 | 1 | 3.1140 | — |
| Research abstracts | pilot | Hessian trace | 0.030 | 65,536 | 1 | 3.1141 | — |
| Research abstracts | pilot | Hessian trace | 0.100 | 65,536 | 1 | 3.1143 | — |
| TinyStories | branch | Shared trace checkpoint | 0.010 | 8,388,608 | 1 | 2.7577 | — |
| TinyStories | control | Initial checkpoint | 0.000 | 0 | 1 | 8.3437 | — |
| TinyStories | control | Unigram | 0.000 | 0 | 1 | 6.0036 | — |
| TinyStories | hybrid | Curvature-dependent hybrid | 0.010 | 16,777,216 | 1 | 2.5459 | — |
| TinyStories | hybrid | Always-on hybrid | 0.010 | 16,777,216 | 1 | 2.5459 | — |
| TinyStories | hybrid | Fixed late hybrid | 0.010 | 16,777,216 | 1 | 2.5461 | — |
| TinyStories | hybrid | Stronger trace | 0.010 | 16,777,216 | 1 | 2.5460 | — |
| TinyStories | hybrid | Hessian trace | 0.010 | 16,777,216 | 1 | 2.5459 | — |
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

First registered checkpoint and sample in run-ID order per stage and method. [All continuations](reports/experiments/experiments.md)

<details><summary>Research abstracts · Initial checkpoint · control, seed 0</summary>

[Recorded sample](results/abstracts-control-s00-initial-r00/samples.jsonl)

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

<details><summary>Research abstracts · Unigram · control, seed 0</summary>

[Recorded sample](results/abstracts-control-s00-unigram-r00/samples.jsonl)

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

<details><summary>Research abstracts · Ordinary AdamW · pilot, seed 0</summary>

[Recorded sample](results/abstracts-pilot-s00-ce-r00/samples.jsonl)

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

<details><summary>Research abstracts · Third derivative · pilot, seed 0</summary>

[Recorded sample](results/abstracts-pilot-s00-third-r01-fp64/samples.jsonl)

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

<details><summary>Research abstracts · Hessian trace · pilot, seed 0</summary>

[Recorded sample](results/abstracts-pilot-s00-trace-r01-fp64/samples.jsonl)

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     that will be used to assess the cognitive
    performance of neurological disorders. We will focus on three major areas:
    (1) the nervous system as a whole, (2) the brain regions that

</details>

<details><summary>TinyStories · Initial checkpoint · control, seed 0</summary>

[Recorded sample](results/stories-control-s00-initial-r00/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     break painted pleaseerp gif neat lead bro comfort rid shr search impressedosairs try ants oss note daughter woodLater rest independent stars stonesiver mixaybe Le spoon readMe fingersiew embar bached mail

</details>

<details><summary>TinyStories · Unigram · control, seed 0</summary>

[Recorded sample](results/stories-control-s00-unigram-r00/samples.jsonl)

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

<details><summary>TinyStories · Curvature-dependent hybrid · hybrid, seed 21</summary>

[Recorded sample](results/stories-hybrid-s21-adaptive-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his house

</details>

<details><summary>TinyStories · Always-on hybrid · hybrid, seed 21</summary>

[Recorded sample](results/stories-hybrid-s21-always-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his mail

</details>

<details><summary>TinyStories · Fixed late hybrid · hybrid, seed 21</summary>

[Recorded sample](results/stories-hybrid-s21-late-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his mail

</details>

<details><summary>TinyStories · Stronger trace · hybrid, seed 21</summary>

[Recorded sample](results/stories-hybrid-s21-strong-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his house

</details>

<details><summary>TinyStories · Hessian trace · hybrid, seed 21</summary>

[Recorded sample](results/stories-hybrid-s21-trace-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his house

</details>

<details><summary>TinyStories · Ordinary AdamW · pilot, seed 0</summary>

[Recorded sample](results/stories-pilot-s00-ce-r00/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Trace + third derivative · pilot, seed 0</summary>

[Recorded sample](results/stories-pilot-s00-combined-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Squared Hessian norm · pilot, seed 0</summary>

[Recorded sample](results/stories-pilot-s00-hessian_norm-r03/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Randomized gradient signs · pilot, seed 0</summary>

[Recorded sample](results/stories-pilot-s00-sham-r01/samples.jsonl)

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

</details>

<details><summary>TinyStories · Third derivative · pilot, seed 0</summary>

[Recorded sample](results/stories-pilot-s00-third-r01/samples.jsonl)

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

Use Python 3.12, uv, and an NVIDIA GPU. Install with `uv sync --locked` and check the implementation with `uv run --locked thirdloss verify`. Run the original experiments and the six-arm follow-up with `uv run --locked thirdloss study --with-hybrid`. Once the TinyStories calibration and pilot selection exist, `uv run --locked thirdloss hybrid` runs the follow-up on its own. In another terminal run `uv run thirdloss dashboard --port 18765` for live accuracy, loss and curvature. Regenerate the paper, plots and tables with `uv run thirdloss report`. [Setup, checkpoints and CLI](docs/runbook.md) · [Document splits](docs/data.md) · [Model collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

The pipeline pins the source texts, splits by document, learns the stories tokenizer using training documents, and freezes the evaluation definition. Identical initializations and document orders pair the competing objectives. The smaller model trains all weights. The pretrained model trains only attention adapters. Examine both improvement and deterioration across seeds and both computational budgets. [TinyStories](https://arxiv.org/pdf/2305.07759) · [Pythia](https://huggingface.co/EleutherAI/pythia-410m) · [Common Pile](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered) · [LoRA](https://arxiv.org/pdf/2106.09685)

## Milestones

- Publish the protocol, references and analysis decisions.
- Verify the scalar objective and its training gradient on analytical functions and a small Transformer.
- Train the pilot, publish throughput and establish feasibility on the local GPU.
- Complete controls, development selection, paired confirmations and a reproducible report.
- [ ] Test whether adding the third-derivative penalty late in Hessian-trace training helps the model stay in a wider low-loss region. [Exploratory plan and rationale](reports/plan.md#late-third-derivative-regularization)
- [ ] Compare a capped third-derivative penalty weight that rises as measured curvature falls with the fixed-token schedule. Test whether it preserves directional width at comparable training fit and whether it improves held-out token prediction. [Curvature-dependent schedule and controls](reports/plan.md#curvature-dependent-penalty-weight)
