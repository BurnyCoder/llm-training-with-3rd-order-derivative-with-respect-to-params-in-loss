# Third derivatives in language-model training

Does a language model predict unseen tokens better when training penalizes rapid changes in loss curvature? We test this on a TinyStories decoder trained from scratch and on Pythia-410M attention adapters. A second TinyStories experiment compares a fixed late start with a schedule that increases the penalty as measured curvature falls. [Study design](reports/planned-runs.md)

The research background includes flat minima, Hessian measurements and third derivatives in language modeling and other fields. [Original flat-minima paper](https://people.idsia.ch/~juergen/fm/node1.html) · [Hessian regularization in GPT-2](https://arxiv.org/pdf/2306.08553#page=12) · [Hessians in image classification](https://arxiv.org/pdf/2012.03801) · [Third derivatives in language-model training dynamics](https://arxiv.org/pdf/2505.22042) · [Derivative penalties in splines](https://doi.org/10.1007/BFb0086566)

<!-- READOUT:START -->

## Results at a glance

**Lower next-token loss (NLL) is better** because the model assigns more probability to the tokens that actually came next. **Higher top-1 accuracy is better** because the model’s first guess is correct more often. Higher speed means more training targets per second. Lower peak memory uses fewer resources.

| Model and split | Matched evidence | Third-order NLL vs AdamW<br>↓ Lower is better | Third-order NLL vs trace<br>↓ Lower is better | Speed vs AdamW<br>↑ Higher is better |
| --- | --- | --- | --- | --- |
| TinyStories pretraining · dev | 5/8 full-budget seeds | 0.000028 higher | 0.000254 lower | 70.7% slower |
| Pythia-410M adapters · dev | 1/8 full-budget seeds | 0.000058 lower | 0.000024 higher | 91.5% slower |

**Adaptive vs fixed-ramp hybrid** · 4/8 paired seeds. Adaptive development NLL was 0.000203 lower. It retained 0.0542 less directional width after the switch. Median final widths were 13.103 (adaptive) and 13.159 (fixed). More width is better for the registered geometry test. Whether more width improves prediction is unknown.

Both primary test decisions are pending. Each stage requires eight paired test seeds and superiority over both baselines under Holm correction.

[Side-by-side scores, accuracy, speed and memory](#side-by-side-comparisons) · [Flatness by variant and baseline](#all-variants-and-baselines) · [Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Paired tests and intervals](reports/summary.md)

<!-- READOUT:END -->

Sepp Hochreiter and Jürgen Schmidhuber proposed that **among models that fit the training data equally well, those in flatter minima may generalize better to unseen data**. In a flat minimum, many nearby weight settings still fit. If some weights can be rounded more coarsely without spoiling the fit, a good predictor can take fewer bits to describe under a fixed encoding. Their minimum-description-length argument links that shorter description to a lower risk of overfitting. [Hochreiter and Schmidhuber, *Flat Minima* (1997), §1](https://people.idsia.ch/~juergen/fm/node1.html)

**Why did earlier papers use the Hessian?** At a smooth minimum the gradient is zero, whether the valley is sharp or flat. The Hessian gives a quadratic approximation to how much training loss rises when the weights move. For small steps of equal size in uniformly random directions, the predicted average rise is proportional to the **Hessian trace**, the sum of second derivatives along the weight coordinates. The researchers penalized the trace to favor fits that tolerate small weight changes and tested whether those fits generalize better. [Liu, Yu and Lin, §§3.2–3.3](https://arxiv.org/pdf/2208.05924#page=3) · [Zhang, Li and Ju, equation 4](https://arxiv.org/pdf/2306.08553#page=5)

Sankar et al. observed that layerwise traces fell during image-classifier training and tried penalizing them directly. Liu, Yu and Lin drew on a generalization bound for linear classifiers to motivate a stochastic trace penalty and reported WikiText-2 experiments with LSTMs and GRUs. Zhang, Li and Ju paired opposite weight perturbations so the first-order loss changes would cancel, giving them a way to target curvature during GPT-2 fine-tuning for question answering. [Sankar et al., Figure 5 and Table 1](https://arxiv.org/pdf/2012.03801#page=6) · [Liu, Yu and Lin, §5.2](https://arxiv.org/pdf/2208.05924#page=10) · [Zhang, Li and Ju, Table 5](https://arxiv.org/pdf/2306.08553#page=12)

**Why third derivatives?** Two minima can have the same small curvature at the bottom, yet one can steepen much sooner. The third derivatives of next-token loss measure how its Hessian changes as the weights move. The training penalty estimates their sum of squares, so rapid changes of either sign carry a cost. If curvature starts small and changes slowly throughout a neighborhood, the weights can move farther while loss stays low. [Worked examples and width bound](docs/third-derivative-penalty.md#when-can-the-penalty-favor-a-wider-minimum) · [Taylor remainder, equation 22](https://link.springer.com/article/10.1007/s10288-023-00541-9)

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

## Side-by-side comparisons

Each row states which direction is better for that metric. Bold highlights the best observed value at the displayed precision. A tie means the paired difference rounds to zero. NLL is negative log-likelihood in nats per target. Perplexity is exp(NLL), computed for each run before taking medians. Compare it within a corpus and tokenizer. Accuracy differences use percentage points (pp). [Perplexity definition](https://huggingface.co/docs/transformers/perplexity)

### TinyStories pretraining

**Full development split · 5/8 full-budget seeds · 16,777,216 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. [Strength selection](results/selection/stories.json) · [Experiment ledger](reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | **2.543954** | 2.544565 | 2.544363 | 0.000028 higher | 0.000254 lower |
| Development perplexity<br>↓ Lower is better | **12.7299** | 12.7377 | 12.7351 | 0.0004 higher | 0.0032 lower |
| Dev top-1 accuracy<br>↑ Higher is better | **46.243%** | 46.226% | 46.222% | 0.001 pp lower | 0.002 pp higher |
| Equal-time probe NLL<br>↓ Lower is better | **2.54476** | 2.73483 | 2.99045 | 0.44440 higher | 0.27561 higher |
| Training speed (targets/s)<br>↑ Higher is better | **130,533** | 68,581 | 38,410 | 70.7% slower | 43.1% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 608.2 | 608.2 | 608.2 | Tie | Tie |

The common training-time cutoff had a median of 128.5 seconds. The furthest checkpoint used for this row was 10.3 seconds before its cutoff.

Awaiting paired test results (5 of 8 full-horizon training triplets).

### Pythia-410M adapters

**Full development split · 1/8 full-budget seeds · 524,288 training targets per run.** Method columns show medians over the same seeds. The two right columns give the median paired change for third order against each baseline. [Strength selection](results/selection/abstracts.json) · [Experiment ledger](reports/experiments/experiments.md)

| Metric | AdamW | Hessian trace | Third order | vs AdamW | vs Hessian trace |
| --- | --- | --- | --- | --- | --- |
| Development NLL<br>↓ Lower is better | 3.036813 | **3.036731** | 3.036755 | 0.000058 lower | 0.000024 higher |
| Development perplexity<br>↓ Lower is better | 20.8387 | **20.8370** | 20.8375 | 0.0012 lower | 0.0005 higher |
| Dev top-1 accuracy<br>↑ Higher is better | **42.478%** | 42.476% | **42.478%** | Tie | 0.002 pp higher |
| Equal-time probe NLL<br>↓ Lower is better | **3.00554** | 3.04789 | 3.16336 | 0.15782 higher | 0.11547 higher |
| Training speed (targets/s)<br>↑ Higher is better | **1,507** | 350 | 128 | 91.5% slower | 63.4% slower |
| Peak GPU allocation (MiB)<br>↓ Lower is better | 2,346.3 | 2,346.3 | 2,346.3 | Tie | Tie |

The common training-time cutoff had a median of 347.9 seconds. The furthest checkpoint used for this row was 112.1 seconds before its cutoff.

Peak host memory (lower uses less RAM) was AdamW 14.04 GiB, Hessian trace 14.04 GiB, Third order 14.04 GiB. This measure includes earlier work in each interpreter.

Awaiting paired test results (1 of 8 full-horizon training triplets).

The equal-time row uses the last available fixed-window development score at or before the fastest run’s finish time in each seed. Full-split NLL uses every development target. Training speed includes regularizer probes. Adapter derivatives use CPU float64 with one GPU reserved. [Timing definitions and checkpoint lags](reports/summary.md)

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

Each row uses the same fixed training windows and probe directions within its stage. Parentheses give measured / planned seeds for that cell. Targets count next-token examples used for optimizer updates in this study. The unigram uses counts from the full training split, and initial Pythia retains its pretrained backbone. Compare rows with matching targets and seeds. Larger **weight width** means greater tolerance to moving the model’s trainable parameters. Larger **common score width** means that all token scores can tolerate a larger shared bias before NLL rises by 0.1 nats, measured in RMS logit units. The unigram has zero trainable model weights and shares the score test with every neural predictor. Small differences can fall inside the numerical search brackets. Both widths have an unknown relationship to better held-out prediction. [Per-run search brackets](reports/flatness.md#per-run-checkpoint-measurements) · [All-model measurement design](reports/amendments/all-model-flatness.md)

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
| Ordinary AdamW · confirmation | 16,777,216 | 1–8 | 12.846 (6/8) | 0.59276 (6/8) | 1.0813 (6/8) |
| Hessian trace · confirmation | 16,777,216 | 1–8 | 12.974 (5/8) | 0.58448 (5/8) | 1.0815 (5/8) |
| Third derivative · confirmation | 16,777,216 | 1–8 | 12.979 (6/8) | 0.5777 (6/8) | 1.0810 (6/8) |
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
| Ordinary AdamW · confirmation | 524,288 | 1–8 | 20.132 (1/8) | 0.55564 (1/8) | 1.1054 (1/8) |
| Hessian trace · confirmation | 524,288 | 1–8 | 20.270 (1/8) | 0.62496 (1/8) | 1.1057 (1/8) |
| Third derivative · confirmation | 524,288 | 1–8 | 20.313 (1/8) | 0.60575 (1/8) | 1.1055 (1/8) |

<details><summary>Pythia-410M · adapter weights · other pilot strengths and precision diagnostics</summary>

| Variant | Training targets | Seed cohort | Weight width<br>↑ Wider is flatter | RMS weight curvature<br>↓ Less local bending | Common score width<br>↑ More score tolerance |
| --- | --- | --- | --- | --- | --- |
| Hessian trace (3%) | 65,536 | 0 | 19.775 (1/1) | 0.58335 (1/1) | 1.0929 (1/1) |
| Hessian trace (10%) | 65,536 | 0 | 19.856 (1/1) | 0.77214 (1/1) | 1.0930 (1/1) |
| Third derivative (3%) | 65,536 | 0 | 19.968 (1/1) | 0.56999 (1/1) | 1.0927 (1/1) |
| Third derivative (10%) | 65,536 | 0 | 19.997 (1/1) | 0.56095 (1/1) | 1.0926 (1/1) |
| Third derivative (3%) · excluded precision diagnostic | 65,536 | 0 | 19.885 (1/1) | 0.58797 (1/1) | 1.0932 (1/1) |

</details>

**TinyStories pretraining · full-budget checkpoints · seeds 1, 2, 3, 4, 5 · 16,777,216 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 12.909 | 12.974 | 13.036 |
| Final width range across seeds<br>Descriptive spread | 12.542–12.963 | 12.638–13.044 | 12.667–13.101 |
| Middle 50% of directions<br>Descriptive spread | 12.629–13.097 | 12.774–13.183 | 12.770–13.192 |
| Rays at limit / tested<br>Measurement coverage | 0/160 | 0/160 | 0/160 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 2.58830 | 2.58611 | 2.58596 |
| RMS Hessian curvature<br>↓ Lower means less local bending | 0.592477 | 0.584484 | 0.575793 |
| Signed Hessian trace / parameter<br>No general better direction | +0.00468202 | +0.00454272 | +0.00450279 |

**Pythia-410M adapters · full-budget checkpoints · seeds 1 · 524,288 training targets**

| Flatness statistic | AdamW | Hessian trace | Third order |
| --- | --- | --- | --- |
| Directional width<br>↑ Wider is flatter | 20.132 | 20.270 | 20.313 |
| Final width range across seeds<br>Descriptive spread | One seed | One seed | One seed |
| Middle 50% of directions<br>Descriptive spread | 19.362–20.737 | 19.558–20.675 | 19.476–20.931 |
| Rays at limit / tested<br>Measurement coverage | 0/32 | 0/32 | 0/32 |
| Unperturbed probe NLL<br>↓ Lower fits these windows better | 2.84601 | 2.84668 | 2.84606 |
| RMS Hessian curvature<br>↓ Lower means less local bending | 0.555644 | 0.624955 | 0.605748 |
| Signed Hessian trace / parameter<br>No general better direction | +0.00201225 | +0.00159403 | +0.00183383 |

For the primary comparison, TinyStories uses all weights and Pythia uses the LoRA factors. Compare widths within each model. The link gives every run, directional bracket and Hessian probe. [Flatness statistics and raw files](reports/flatness.md) · [Secondary measurement design](reports/amendments/checkpoint-flatness.md)

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

**Registered width decision** · Awaiting eight paired width measurements. Width probes use fixed training windows. [Every width, training-fit flag, replay and paired difference](reports/hybrid/results.md)

**Training diagnostics have no established better direction for held-out prediction.** A smaller derivative penalty meets its training objective more closely. The raw Hessian trace, third-derivative estimate, gradient norm and penalty strength describe the training process. Their predictive value is assessed separately by held-out NLL. [Objectives and endpoints](reports/preregistration.md)

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

| [AdamW](results/stories-confirm-s01-ce-r00/samples.jsonl) | [Hessian trace](results/stories-confirm-s01-trace-r01/samples.jsonl) | [Third order](results/stories-confirm-s01-third-r01/samples.jsonl) |
| --- | --- | --- |
| <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> | <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> | <samp> to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.<br><br>While they were playing, Max found a big hole in the mail</samp> |

</details>

<details><summary>Pythia-410M adapters · same prompt, seed 1</summary>

**Prompt** <samp>One of the central objectives of contemporary neuroimaging research is to<br>create predictive models</samp>

| [AdamW](results/abstracts-confirm-s01-ce-r00/samples.jsonl) | [Hessian trace](results/abstracts-confirm-s01-trace-r01-fp64/samples.jsonl) | [Third order](results/abstracts-confirm-s01-third-r01-fp64/samples.jsonl) |
| --- | --- | --- |
| <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> | <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> | <samp> that will accurately predict the behavior of<br>neuropsychiatric disorders. We hypothesize that the more accurate prediction of<br>behavior based on the nervous system anatomy, the better the prediction<br>precision for clinical diagnosis</samp> |

</details>

<details><summary>TinyStories hybrid schedules · same prompt, seed 21</summary>

**Prompt** <samp>Once upon a time, there was a clever little dog named Max. Max loved</samp>

| [Adaptive](results/stories-hybrid-s21-adaptive-r01/samples.jsonl) | [Fixed ramp](results/stories-hybrid-s21-late-r01/samples.jsonl) |
| --- | --- |
| <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his house</samp> | <samp> to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.<br><br>One day, Max found a big hole in his mail</samp> |

</details>

Seed sensitivity is the final stage, after both primary test evaluations, all hybrid replications and checkpoint flatness. [Final seed-sensitivity report](reports/seed-sensitivity.md)

[Explore the results](https://burnycoder.github.io/llm-training-with-penalizing-rapid-changes-of-curvature-of-its-loss-with-derivative-of-hessian/) · [Hugging Face explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Hugging Face collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378) · [Paper](reports/paper.pdf) · [Run ledger](reports/experiments/experiments.md)

Recorded 73 runs, including 73 with a completed summary.

TinyStories hybrid follow-up: 23 of 48 full runs and 5 of 8 shared checkpoints complete. Geometric decision: awaiting eight paired width measurements. [Width measurements, scores and controls](reports/hybrid/results.md)

[Full score table, strength search and per-seed test differences](reports/summary.md)

![Directional width by TinyStories arm and seed](docs/figures/hybrid_width.png)

![Parameter-space computation graph](docs/figures/architecture.png)

![Development NLL](docs/figures/curves.png)

### Full generations by method

**TinyStories** · [Ordinary AdamW](reports/experiments/stories-confirm-s01-ce-r00/experiment.md#fixed-prompt-generations) · [Third derivative](reports/experiments/stories-confirm-s01-third-r01/experiment.md#fixed-prompt-generations) · [Hessian trace](reports/experiments/stories-confirm-s01-trace-r01/experiment.md#fixed-prompt-generations) · [Initial checkpoint](reports/experiments/stories-control-s00-initial-r00/experiment.md#fixed-prompt-generations) · [Unigram](reports/experiments/stories-control-s00-unigram-r00/experiment.md#fixed-prompt-generations) · [Curvature-dependent hybrid](reports/experiments/stories-hybrid-s21-adaptive-r01/experiment.md#fixed-prompt-generations) · [Always-on hybrid](reports/experiments/stories-hybrid-s21-always-r01/experiment.md#fixed-prompt-generations) · [Fixed late hybrid](reports/experiments/stories-hybrid-s21-late-r01/experiment.md#fixed-prompt-generations) · [Stronger trace](reports/experiments/stories-hybrid-s21-strong-r01/experiment.md#fixed-prompt-generations) · [Cross-seed replay](reports/experiments/stories-hybrid-s22-replay-r01/experiment.md#fixed-prompt-generations) · [Trace + third derivative](reports/experiments/stories-pilot-s00-combined-r01/experiment.md#fixed-prompt-generations) · [Squared Hessian norm](reports/experiments/stories-pilot-s00-hessian_norm-r03/experiment.md#fixed-prompt-generations) · [Randomized gradient signs](reports/experiments/stories-pilot-s00-sham-r01/experiment.md#fixed-prompt-generations)

**Research abstracts** · [Ordinary AdamW](reports/experiments/abstracts-confirm-s01-ce-r00/experiment.md#fixed-prompt-generations) · [Third derivative](reports/experiments/abstracts-confirm-s01-third-r01-fp64/experiment.md#fixed-prompt-generations) · [Hessian trace](reports/experiments/abstracts-confirm-s01-trace-r01-fp64/experiment.md#fixed-prompt-generations) · [Initial checkpoint](reports/experiments/abstracts-control-s00-initial-r00/experiment.md#fixed-prompt-generations) · [Unigram](reports/experiments/abstracts-control-s00-unigram-r00/experiment.md#fixed-prompt-generations) · [Trace + third derivative](reports/experiments/abstracts-pilot-s00-combined-r01-fp64/experiment.md#fixed-prompt-generations) · [Squared Hessian norm](reports/experiments/abstracts-pilot-s00-hessian_norm-r03-fp64/experiment.md#fixed-prompt-generations) · [Randomized gradient signs](reports/experiments/abstracts-pilot-s00-sham-r01-fp64/experiment.md#fixed-prompt-generations)

<!-- RESULTS:END -->

## Reproduce the study

Use Python 3.12, uv, and an NVIDIA GPU. From the repository root, install the locked environment, verify the derivatives and start the study.

```sh
uv sync --locked
uv run --locked thirdloss verify
uv run --locked thirdloss study --with-hybrid --with-flatness
```

This trains both model families, runs the six hybrid variants, evaluates the frozen models, and measures flatness for each checkpoint and reference. Repeating the study command resumes it. To measure existing saved models separately, run `uv run --locked thirdloss flatness --phase all`. In another terminal, `uv run --locked thirdloss dashboard --port 18765` serves live accuracy, loss and curvature. Regenerate the paper, plots and tables with `uv run --locked thirdloss report`. [Setup, checkpoint loading and publication](docs/runbook.md) · [Document splits](docs/data.md) · [Model collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

The pipeline pins the source texts, splits by document, learns the stories tokenizer using training documents, and freezes the evaluation definition. Identical initializations and document orders pair the competing objectives. The smaller model trains all weights. The pretrained model trains only attention adapters. Examine both improvement and deterioration across seeds and both computational budgets. [TinyStories](https://arxiv.org/pdf/2305.07759) · [Pythia](https://huggingface.co/EleutherAI/pythia-410m) · [Common Pile](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered) · [LoRA](https://arxiv.org/pdf/2106.09685)

## Milestones

**Seed sensitivity runs last.** Both stages complete their single-seed variants, controls and first full-budget comparison before the remaining primary confirmations. After the frozen tests, hybrid replications and checkpoint flatness, the final report measures how much the outcomes change across seeds. [Execution order](reports/amendments/seed-sensitivity-last.md) · [Final seed-sensitivity report](reports/seed-sensitivity.md)

The protocol, derivative checks and pilot timing are public. The checklist follows the completed experiment records. [Preregistration](reports/preregistration.md) · [Numerical verification](results/verification) · [One-week feasibility](results/feasibility/one-week.json)

<!-- MILESTONES:START -->

- [x] Finish both development searches and their single-seed trained and untrained controls. [Selection and controls](reports/planned-runs.md)
- [x] Complete the first full-budget AdamW, Hessian-trace and third-order comparison in both model families. [Run ledger](reports/experiments/experiments.md)
- [ ] Evaluate both frozen eight-seed primary test matrices. [Paired test results](reports/summary.md)
- [ ] Finish the late, curvature-dependent and replay experiments with all comparison arms. [Hybrid plan](reports/hybrid/preregistration.md) · [Width and prediction results](reports/hybrid/results.md)
- [ ] Complete the common score-space measurement and each applicable weight-space measurement. [Flatness by checkpoint](reports/flatness.md)
- [ ] Run the final seed-sensitivity analysis on the sealed results. [Across-seed variation](reports/seed-sensitivity.md)

<!-- MILESTONES:END -->
