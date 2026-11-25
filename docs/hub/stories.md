---
language: [en]
license: cdla-sharing-1.0
source_datasets: [roneneldan/TinyStories]
task_categories: [text-generation]
pretty_name: TinyStories token streams for the third-derivative study
---

# TinyStories research splits

These are modified files derived from TinyStories by Ronen Eldan and Yuanzhi Li. Libor “Burny” Burian’s study split, normalized, deduplicated and tokenized documents and appended an end-of-sequence token after each document. The packed files, document index and tokenizer are distributed with attribution under the Community Data License Agreement – Sharing, version 1.0. [Pinned source](https://huggingface.co/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64) · [Original paper](https://arxiv.org/abs/2305.07759) · [License terms](https://cdla.dev/sharing-1-0/)

Read each `.bin` as a flat array of little-endian unsigned 16-bit integers. The training-only tokenizer defines the IDs. The development documents come from the original training source. The official validation source supplies the final test documents. The index gives each accepted source ID, normalized document hash, split, token offset and length. The rejection ledger records exact and cross-split near duplicates. [Split counts, byte lengths and SHA-256 digests](manifest.json) · [Executable preparation](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/research/src/thirdloss/data.py)
