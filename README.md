# Third derivatives in language-model training

Does a language model predict unseen tokens better when training penalizes rapid changes in the curvature of its loss? This project compares ordinary AdamW, Hessian-trace regularization, and a penalty on every third partial derivative of token cross-entropy with respect to the trainable weights. Its two experiments cover full-weight training on short stories and low-rank adaptation on research abstracts. The primary evidence is held-out loss at equal training tokens.

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
