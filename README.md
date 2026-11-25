# Third derivatives in language-model training

Does a language model predict unseen tokens better when training penalizes rapid changes in the curvature of its loss? This project compares ordinary AdamW, Hessian-trace regularization, and a penalty on every third partial derivative of token cross-entropy with respect to the trainable weights. Its two experiments cover full-weight training on short stories and low-rank adaptation on research abstracts. The primary evidence is held-out loss at equal training tokens.

## Flat minima, Hessians and third derivatives in earlier work

| Setting | What the researchers used the derivatives for | Original papers and projects |
|---|---|---|
| Origin of flat-minimum search | Hochreiter and Schmidhuber searched for connected regions of weights where training error changes little. Their journal paper describes a search algorithm using second derivatives. | [Original NeurIPS paper, 1994](https://proceedings.neurips.cc/paper/1994/hash/01882513d5fa7c329e940dda99b12147-Abstract.html) · [Flat Minima, Neural Computation, 1997](https://people.idsia.ch/~juergen/fm/) |
| Hessians in language models | Sophia uses stochastic curvature estimates to precondition GPT training updates. Liu et al. measure Hessian trace and study downstream behavior of language models. Liu, Yu and Lin explicitly add trace to the objective in WikiText-2 LSTM and GRU experiments. | [Sophia paper](https://arxiv.org/pdf/2305.14342) · [Sophia code](https://github.com/Liuhong99/Sophia) · [Language-model flatness study](https://proceedings.mlr.press/v202/liu23ao.html) · [Explicit Hessian penalty, §5.2](https://arxiv.org/pdf/2208.05924) |
| Hessians outside language modeling | Layerwise Hessian-trace penalties have been tested in image classification. Reparameterization studies explain why a curvature measurement alone cannot establish predictive generalization. | [Sankar et al.](https://arxiv.org/pdf/2012.03801) · [Dinh et al.](https://proceedings.mlr.press/v70/dinh17b.html) |
| Third derivatives in pretrained language models | Zhang and Wang report a third-order Taylor correction in activation-patching experiments. The derivative follows the direction of a hidden-activation intervention in a frozen model. They report that a cubic correction can fail for large perturbations. | [Zhang and Wang, §4 and supplement](https://arxiv.org/pdf/2606.09899) |
| Third derivatives outside LLMs | Wolinski projects third derivatives of the **weight-space loss** to regularize a local optimization model. Lellmann et al. study third **spatial** derivatives of terrain surfaces. Duchon gives the general squared-derivative roughness formulation. | [Projected parameter derivatives](https://arxiv.org/pdf/2312.03885) · [Third-order terrain reconstruction](https://www.lellmann.net/work/_media/lellmann_ssvm13.pdf) · [Spline roughness](https://doi.org/10.1007/BFb0086566) |

These papers motivate a distinct experiment here: putting the squared norm of the **third derivative of next-token loss with respect to trainable weights** directly in the training objective. The reviewed studies leave its effect on held-out next-token loss open.

The third-order term measures how the Hessian changes as weights move. Two independent random sign vectors estimate its squared Frobenius norm. Differentiating the estimate gives the optimizer a fourth-derivative contribution. This combines an order-three roughness density with matrix-free norm estimation. [Duchon](https://doi.org/10.1007/BFb0086566) · [Bujanović and Kressner](https://arxiv.org/pdf/2004.06433) · [Hessian comparator](https://arxiv.org/pdf/2208.05924)

**Study record.** The protocol and run matrix precede model execution. Experiments, scientific conclusions, and generated examples will be recorded from raw artifacts here. [Preregistration](reports/preregistration.md) · [Run matrix](reports/planned-runs.md) · [Literature](reports/literature-review.md) · [State of the art](reports/state-of-the-art-review.md) · [Progress](reports/progress.md)

<!-- RESULTS:START -->
The preregistration is the first milestone. Model outcomes are pending.
<!-- RESULTS:END -->

## Reproduce the study

Use Python 3.12, uv, and an NVIDIA GPU for the full study. The implementation will supply a single CLI for preparation, training, evaluation and report generation. Use a project-local virtual environment. Store datasets, resumable checkpoints and download caches outside Git. The repository will carry split manifests, lockfiles, scripts and portable result records.

The pipeline pins the source texts, splits by document, learns the stories tokenizer using training documents, and freezes the evaluation definition. Identical initializations and document orders pair the competing objectives. The smaller model trains all weights. The pretrained model trains only attention adapters. Examine both improvement and deterioration across seeds and both computational budgets. [TinyStories](https://arxiv.org/pdf/2305.07759) · [Pythia](https://huggingface.co/EleutherAI/pythia-410m) · [Common Pile](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered) · [LoRA](https://arxiv.org/pdf/2106.09685)

## Milestones

- Publish the protocol, references and analysis decisions.
- Verify the scalar objective and its training gradient on analytical functions and a small Transformer.
- Train the pilot, publish throughput and establish feasibility on the local GPU.
- Complete controls, development selection, paired confirmations and a reproducible report.
