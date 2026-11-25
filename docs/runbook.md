# Reproducing the study

Install Python 3.12 and [uv](https://docs.astral.sh/uv/). The lock targets Windows AMD64 and Linux x86_64 with an NVIDIA driver supporting the CUDA 13.2 PyTorch wheel. Scratch training and ordinary adapter updates use float32. Adapter derivatives use float64. Make a project-local environment and install all locked dependencies with `uv sync --locked`. Copy `.env.example` to `.env` and optionally set `THIRDLOSS_STORAGE` to a directory with room for corpora, CUDA checkpoints and Hub downloads. Use the existing GitHub CLI and Hugging Face login for publication.

```sh
uv run thirdloss verify
uv run thirdloss prepare --stage stories
uv run thirdloss train --stage stories --method third --phase pilot --seed 0 --ratio 0.03
uv run thirdloss dashboard --port 18765
```

In another terminal, open the printed dashboard URL. The public explorer reads the last published results. The local dashboard reads running records. Accuracy is top-one token accuracy and NLL is in nats per target token. The training-time column excludes data preparation, checks, validation, checkpoint serialization and publication.

Use `uv run --locked thirdloss study --with-hybrid` for the two original stages plus the registered six-arm TinyStories follow-up. Once the TinyStories selection and calibration exist, `uv run --locked thirdloss hybrid` runs the follow-up alone. Add `--publish` to mirror each completed arm, optimizer state, unabridged logs, directional-width brackets and report to the project’s GitHub and Hugging Face repositories. Restart with the identical command. Branches inherit the same full-horizon AdamW moments, data position and lagged monitor. Select **hybrid** in the explorer and choose **Directional width** or **Third-derivative coefficient** to inspect a run. [Hybrid preregistration](../reports/hybrid/preregistration.md) · [Per-seed results](../reports/hybrid/results.md)

Run `uv run thirdloss study` to execute both stages, select strengths on development data, freeze all confirmatory checkpoints, and evaluate them. The owner's publishing workflow uses `uv run thirdloss study --publish`. This uploads fitted coordinates after each run and the study record after each training/evaluation. A local clone can omit the publishing flag. Repeating the same command resumes the last saved optimization step and skips completed runs. Checkpoints include optimizer state, random state and data cursor. The corpus manifests and run configuration must match. [Data and leakage checks](data.md) · [Preregistered run matrix](../reports/planned-runs.md)

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

## Hugging Face publication and verification

`uv run thirdloss publish` mirrors the committed Git tree, PDF, raw results, timestamped logs, interactive Space, packed corpora, audit indices, fitted weights and restart states to one collection. Each corpus card identifies its upstream license and changes. The test binary for each stage joins its dataset when the timing projection and stage freeze are committed. Model scoring then verifies the same test digest. [Full archive](https://huggingface.co/BurnyCoder/thirdloss-study) · [Runnable Space](https://huggingface.co/spaces/BurnyCoder/thirdloss-explorer)

Run `uv run thirdloss audit-hub` at the Git revision in `publication.json` to verify every published object against its Git blob or large-file digest, including all tracked files. The archive uses committed bytes so Windows checkout line endings and local configuration cannot change the mirrored source. [Public verification receipt](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/publication.json)

With `study --publish`, the local trainer sends active loss, accuracy, probe estimates, calibration progress and examples to the public explorer about every two minutes. GitHub Pages and the Hugging Face Space read that feed between full releases. The local dashboard reads the training records directly. [Public live feed](https://huggingface.co/BurnyCoder/thirdloss-study/resolve/main/live.json)
