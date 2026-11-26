# Study progress

Updated 2026-11-26T01:12:36+00:00.

51 training/control records and 0 final evaluations are complete. This is 42.5% of 120 planned model milestones.

## Current record

**stories** has 36 completed runs. The next milestone is determined by the run matrix.

Pilot rates project 0.00 remaining confirmation GPU-hours, excluding validation, exports and uploads.

Statistical status: incomplete. Awaiting the complete frozen set of final test scores.

**abstracts** has 15 completed runs. The next milestone is determined by the run matrix.

Pilot rates project 8.35 remaining confirmation GPU-hours, excluding validation, exports and uploads.

Statistical status: incomplete. All checkpoints must reach 524,288 target tokens.

## One-week feasibility

At the pre-test check on 2026-11-25T10:33:28+00:00, pilot timings projected 22.50 hours for all confirmatory training and scoring, with 141.73 hours of the week available for secondary pilots, setup, publication and interruptions. [Timing and GPU memory by method](../results/feasibility/one-week.json)

## TinyStories hybrid follow-up

23 of 48 full runs and 5 of 8 shared checkpoints complete. awaiting eight paired width measurements. [Per-seed widths and development scores](hybrid/results.md)

The first measured set of hybrid arms projects 33.68 further hours from that checkpoint, including the eight replays. With the original confirmations and final scoring, the projected remaining work at the check was 56.18 hours with 159.49 hours left in the week. [Wall-time assumptions, measured memory and inputs](../results/feasibility/hybrid-week.json)

The first seed included 4.11 hours between the last pre-restart update and the first resumed update. Excluding repetitions of that gap projects 4.91 hours of remaining hybrid work and 27.40 hours with the original confirmations and scoring. Both forecasts use actual observed wall time and apply from the first-seed checkpoint. [Restart-adjusted timing](../results/feasibility/hybrid-uptime.json)

## Flatness coverage

| Stage | Weight geometry | Shared score geometry | Median pilot cycle | Longest pilot cycle |
| --- | --- | --- | --- | --- |
| stories | 63/91 | 64/92 | 34 s | 37 s |
| abstracts | 15/36 | 16/37 | 193 s | 311 s |

Weight geometry covers every neural checkpoint. Score geometry also covers the two unigram references. [All arms and their measurements](flatness.md#every-variant-and-baseline)

Giving each predictor still missing a measurement one complete native pilot cycle projects 1.39 additional hours at each stage’s median or 2.10 hours at its longest observed cycle. These scenarios include the observed reporting and upload time. Existing hybrid widths can be reused. The shared score calculation, archive growth and future interruptions can change the total. [Timestamped pilot measurements](../results/feasibility/flatness-pilot-wall-time.json) · [Archived timing log](https://huggingface.co/BurnyCoder/thirdloss-study/blob/main/logs/checkpoint-flatness-20261125T163331Z.log)

## Overall completion and remaining time

Across training, references, final tests, hybrid runs and flatness evaluations, **159/305 milestones are complete (52.1%)** and 146 remain. Each milestone has equal weight in this count. Data preparation, software and publications are recorded separately.

Projected remaining machine time is **27.80–28.87 hours**, including model publication and geometry. There are 149.58 hours left in the original week. These are two timing scenarios. They use the recorded pilot rates, whole remaining hybrid seed blocks, the longest primary pilot as a proxy for each remaining secondary pilot, and median or slower diagnostic and release cycles. Machine or network interruptions can extend them. [Cost by task](../results/feasibility/remaining-work.json) · [Observed release times](../results/feasibility/checkpoint-publication-time.json)

The registered adapter schedules require 918 host derivative calls across unfinished runs. Scaling the pilot by token count alone gives 560. Pricing the scheduled calls at each method’s measured mean changes the forecast by +4.20 hours. The original pre-test feasibility record retains its initial estimate. [Per-arm counts and observed costs](../results/feasibility/remaining-work.json) · [Training gate](../src/thirdloss/windows.py)

The final seed-sensitivity analysis is pending. The queue completes both stages’ single-seed comparisons and original frozen test evaluations before the remaining hybrid replications. All checkpoint measurements precede the final across-seed analysis. [Queue amendment](amendments/seed-sensitivity-last.md) · [Final report](seed-sensitivity.md)

## Monitoring

Inspect runs lasting over 10, 30 and 60 minutes at 5, 15 and 30 minute intervals respectively. The live dashboard refreshes between those checks. [Study design](plan.md) · [Run matrix](planned-runs.md) · [Experiment ledger](experiments/experiments.md)
