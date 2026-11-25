---
language: [en]
license: cc0-1.0
source_datasets: [common-pile/arxiv_abstracts_filtered]
task_categories: [text-generation]
pretty_name: 2024 arXiv abstract token streams for the third-derivative study
---

# 2024 arXiv abstracts research splits

These packed abstract records derive from the Common Pile filtered arXiv abstracts, using January through April first submissions for training, May for development and June for testing. Common Pile identifies arXiv abstract metadata as CC0. Each document's base arXiv ID in `documents.jsonl` identifies its authors and original record at `https://arxiv.org/abs/ID`. [Pinned corpus](https://huggingface.co/datasets/common-pile/arxiv_abstracts_filtered/tree/dc1ceab4755eb037ec61e49cf1350dab7ceee6e7) · [Upstream collection and license](https://huggingface.co/datasets/common-pile/arxiv_abstracts#description) · [CC0](https://creativecommons.org/publicdomain/zero/1.0/)

The study deduplicated and packed the documents with one end-of-sequence token per document. Read each `.bin` as little-endian unsigned 16-bit token IDs. The included tokenizer is the Pythia tokenizer from the pinned EleutherAI checkpoint distributed under Apache 2.0. The document index contains original IDs, timestamps, normalized hashes and packed offsets. [Tokenizer and its license](https://huggingface.co/EleutherAI/pythia-410m/tree/9879c9b5f8bea9051dcb0e68dff21493d67e9d4f) · [Split counts, byte lengths and SHA-256 digests](manifest.json) · [Preparation code](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/src/thirdloss/data.py)
