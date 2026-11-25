---
language: [en]
tags: [scientific-research, causal-language-modeling]
---

# Third derivatives in language-model training

Does penalizing changes in loss curvature improve next-token prediction? The study compares ordinary AdamW, Hessian-trace regularization and the squared Frobenius norm of the third derivative with respect to trainable weights. Every trial, including the excluded numerical diagnostic, has a public record. [Paper](research/reports/paper.pdf) · [Current results](research/reports/summary.md) · [Interactive explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer) · [Collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378)

| Material | Hugging Face location |
|---|---|
| Complete Git tree, locked environment, tests and instructions | [Research tree](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research) · [README](research/README.md) |
| Literature, preregistration, raw observations and reviews | [Reports](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research/reports) · [Raw results](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/research/results) |
| Timestamped training output, full prompts and completions, operator transcripts | [Log archive](https://huggingface.co/BurnyCoder/thirdloss-study/tree/main/logs) |
| Fitted models, model cards, optimizer moments, data cursor and random state | [Full-weight models](https://huggingface.co/BurnyCoder/thirdloss-stories) · [Pythia adapters](https://huggingface.co/BurnyCoder/thirdloss-pythia-410m-adapters) · [Pinned pretrained backbone](https://huggingface.co/EleutherAI/pythia-410m/tree/9879c9b5f8bea9051dcb0e68dff21493d67e9d4f) |
| Prepared training and evaluation data, tokenizers and overlap audits | [TinyStories](https://huggingface.co/datasets/BurnyCoder/thirdloss-tinystories-tokens) · [arXiv abstracts](https://huggingface.co/datasets/BurnyCoder/thirdloss-arxiv-abstracts-2024-tokens) |

The publication receipt binds the Git commit to the verified file hashes across the collection. Run `uv run thirdloss audit-hub` from that checkout to independently compare the published objects. Log files are snapshots at publication time. Operational transcripts redact transport credentials and local account paths. [File digests and Git revision](publication.json)
