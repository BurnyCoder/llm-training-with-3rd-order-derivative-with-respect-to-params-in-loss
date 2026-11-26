# Reproducing the study

Install Python 3.12 and [uv](https://docs.astral.sh/uv/). The lock targets Windows AMD64 and Linux x86_64 with an NVIDIA driver supporting the CUDA 13.2 PyTorch wheel. Scratch training and ordinary adapter updates use float32. Adapter derivatives use float64. Make a project-local environment and install all locked dependencies with `uv sync --locked`. Copy `.env.example` to `.env` and optionally set `THIRDLOSS_STORAGE` to a directory with room for corpora, CUDA checkpoints and Hub downloads. Use the existing GitHub CLI and Hugging Face login for publication.

```sh
uv run thirdloss verify
uv run thirdloss prepare --stage stories
uv run thirdloss train --stage stories --method third --phase pilot --seed 0 --ratio 0.03
uv run thirdloss dashboard --port 18765
```

Open the printed dashboard URL to follow the local run. The two public explorers combine the published results with the live training feed. The README, paper and run matrix show the time of their last result snapshot. The flatness table near the top of the README uses seeds with measurements for all three main methods. Detailed tables include the other variants and controls. Accuracy is top-one token accuracy and NLL is in nats per target token. The training-time column excludes data preparation, checks, validation, checkpoint serialization and publication. [Headline flatness](../README.md#flatness-at-a-glance) · [Every finished, current and planned run](../reports/planned-runs.md#current-evidence-and-remaining-runs)

Use `uv run --locked thirdloss study --with-hybrid` for the two original stages plus the registered six-arm TinyStories follow-up. Once the TinyStories selection and calibration exist, `uv run --locked thirdloss hybrid` runs the follow-up alone. Add `--publish` to mirror each completed arm, optimizer state, unabridged logs, directional-width brackets and report to the project’s GitHub and Hugging Face repositories. Restart with the identical command. Branches inherit the same full-horizon AdamW moments, data position and lagged monitor. Select **hybrid** in the explorer and choose **Directional width** or **Third-derivative coefficient** to inspect a run. [Hybrid preregistration](../reports/hybrid/preregistration.md) · [Per-seed results](../reports/hybrid/results.md)

Run `uv run --locked thirdloss study` for the two primary stages, including strength selection on development data, freezing all confirmatory checkpoints and evaluating them. The full published study uses `uv run --locked thirdloss study --with-hybrid --with-flatness --publish`. This uploads fitted coordinates after each run and the study record after each training or evaluation. A local clone can omit the publishing flag. Repeating the same command resumes the last saved optimization step and skips completed runs. Checkpoints include optimizer state, random state and data cursor. The corpus manifests and run configuration must match. [Data and leakage checks](data.md) · [Preregistered run matrix](../reports/planned-runs.md)

Use `uv run thirdloss report` to regenerate the README results, PDF, figures, experiment notes, progress and explorer from `results/`. Use `uv run thirdloss progress` for current status. `uv run thirdloss evaluate RUN_ID` verifies the registered weight digest and test split before scoring a frozen run. Both tokenizers are stored alongside their stage data. Full untruncated generated token IDs, prompts, reference continuations and outputs are in each run's `samples.jsonl`. Timestamped session logs are stored locally under `logs/`.

After preparing abstracts, `uv run thirdloss verify --pretrained --device cuda` also compares both implementations of the penalty and its entire training gradient on the same pair of training windows, adapter initialization and sign probes. The diagnostic materializes the original joint graph for comparison. Its GPU allocation exceeded 10 GiB during the original replay. The ordinary adapter training path processes the two windows sequentially. `--device cpu` runs the optional comparison in host memory. [Adapter verification](../reports/reviews/adapter-verification.md)

`uv run thirdloss verify --reference --device cpu` repeats the full-size FP64 calculation using the archived pilot’s CUDA probe stream. The production study uses `THIRDLOSS_ADAPTER_DERIVATIVE_DEVICE=cpu` on the laptop, six host math threads (`OMP_NUM_THREADS=6`, `MKL_NUM_THREADS=6`), and the GPU for cross-entropy, optimizer updates, generation and scoring. The derivative device, arithmetic, calibration and per-update host time are recorded. The `-fp64` suffix identifies amended adapter runs. [Protocol amendment](../reports/amendments/adapter-precision.md)

## Load a published checkpoint

All models are indexed in the [Hugging Face collection](https://huggingface.co/collections/BurnyCoder/third-derivatives-in-language-model-training-6b067fb7d5ae3eca49ebb378). The run name identifies its objective, phase, seed and penalty strength. Replace the example run name with the desired published checkpoint. Run from a clone with the locked environment.

```python
from pathlib import Path
from huggingface_hub import snapshot_download
from safetensors.torch import load_file
from tokenizers import Tokenizer
from thirdloss.models import StoryTransformer

run_id = "stories-pilot-s00-third-r03"
snapshot = snapshot_download("BurnyCoder/thirdloss-stories", allow_patterns=f"runs/{run_id}/*")
folder = Path(snapshot) / "runs" / run_id
model = StoryTransformer()
model.load_state_dict(load_file(str(folder / "model.safetensors")))
model.eval()
tokenizer = Tokenizer.from_file(str(folder / "tokenizer.json"))
```

For adapter snapshots use `AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-410m", revision="9879c9b5f8bea9051dcb0e68dff21493d67e9d4f")` and load the adapter directory with `PeftModel.from_pretrained(base, folder)`. The published stage repo is `BurnyCoder/thirdloss-pythia-410m-adapters`. [PEFT](https://huggingface.co/docs/peft/en/package_reference/lora)

Each fitted run also publishes `training_state.pt` and `restart.json`. The manifest identifies the SHA-256 digest and next data step. This PyTorch checkpoint includes the fitted weights, AdamW state, RNG states and run configuration. Local interruptions resume from `THIRDLOSS_STORAGE/checkpoints/RUN_ID/latest.pt`. To recover a published state on a new machine, regenerate the identical stage data, verify the downloaded checkpoint against `restart.json`, and put it at that location. A completed checkpoint retains the state of the last scheduled update. [Checkpoint and restoration code](../src/thirdloss/train.py)

After an operating-system restart, rerun the same study command in the project directory. When the pre- and post-restart logs contain overlapping updates, `uv run --locked thirdloss audit-restart RUN_ID` compares the losses, gradient norms, probe estimates, learning rates and schedule coefficients. The canonical trajectory counts each update once. Both original attempt logs stay archived on Hugging Face under `thirdloss-study/logs/`. [Verified TinyStories restart](../results/verification/hybrid-s21-system-restart.json)

## Hugging Face publication and verification

`uv run thirdloss publish` mirrors the committed Git tree, PDF, raw results, timestamped logs, interactive Space, packed corpora, audit indices, fitted weights and restart states to one collection. Each corpus card identifies its upstream license and changes. The test binary for each stage joins its dataset when the timing projection and stage freeze are committed. Model scoring then verifies the same test digest. [Full archive](https://huggingface.co/BurnyCoder/thirdloss-study) · [Runnable Space](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer)

Run `uv run thirdloss audit-hub` at the Git revision in `publication.json` to verify every published object against its Git blob or large-file digest, including all tracked files. The archive uses committed bytes so Windows checkout line endings and local configuration cannot change the mirrored source. [Public verification receipt](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/publication.json)

With `study --publish`, the local trainer sends active loss, accuracy, probe estimates, calibration progress and examples to the public explorer about every two minutes. GitHub Pages and the Hugging Face Space read that feed between full releases. The local dashboard reads the training records directly. [Public live feed](https://huggingface.co/BurnyCoder/thirdloss-study/resolve/main/live.json)

## Execution order

The complete study defers seed sensitivity to the end. Both stages’ pilot variants and controls and a full-budget first seed per stage come first. The remaining primary comparisons, frozen test scores, hybrid replications and all checkpoint geometry precede the final seed analysis. `uv run --locked thirdloss seed-sensitivity` reruns that final stage from a complete checkout. Once the inputs are sealed, `uv run --locked thirdloss report` also regenerates the seed summaries. For a standalone hybrid example use `thirdloss hybrid --cohort example`. The deferred replay uses its registered donor. [Ordering and prerequisites](../reports/amendments/seed-sensitivity-last.md)

## Checkpoint flatness

Run `uv run --locked thirdloss flatness --stage both --phase pilot --publish` for all pilot strengths and zero-update controls. Use `--phase hybrid` for the shared trunks and six hybrid arms, `--phase confirm` for the eight-seed primary runs, or `--phase all` for the complete research ledger. `--run-id RUN` restricts the command to one checkpoint. Every predictor receives the common logit test, including the empirical unigram. Neural predictors also receive the weight-space width and Hessian tests. Each call checks the training stream and exported weights and resumes from its saved probe files. Run it between timed training runs on a shared GPU. Run `uv run --locked thirdloss report` to rebuild the comparisons. [Weight probes](../reports/amendments/checkpoint-flatness.md) · [All-model comparison](../reports/amendments/all-model-flatness.md) · [Results and raw probes](../reports/flatness.md)

For a complete sequential run, use `uv run --locked thirdloss study --with-hybrid --with-flatness --publish`. After each fitted checkpoint or reference is recorded, a separate process measures flatness before the next timed run. The final pass picks up any outstanding diagnostic checkpoints. The explorer’s measurement menu includes weight width, checkpoint curvature and the common score width for every predictor. [Live explorer](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer)

Each fitted model and zero-update reference also has its own Hugging Face card with the measurement units, their interpretation and links to the raw probes. The collection scorecard compares them at matching training budgets. [TinyStories cards](https://huggingface.co/BurnyCoder/thirdloss-stories/tree/main/runs) · [Pythia and abstracts reference cards](https://huggingface.co/BurnyCoder/thirdloss-pythia-410m-adapters/tree/main/runs) · [Compare every variant](https://huggingface.co/BurnyCoder/thirdloss-study#all-variants-and-baselines)

For comparisons in a replicated study, use one width-probe backend within each model family. PyTorch can produce different random directions on CPU and CUDA from the same seed. The report checks training-window and backend provenance for the controls as well as the primary arms. A hybrid evaluated on a different backend remeasures its supplementary width. Its registered width file continues to identify the original measurement. [PyTorch reproducibility notes](https://docs.pytorch.org/docs/stable/notes/randomness.html)
