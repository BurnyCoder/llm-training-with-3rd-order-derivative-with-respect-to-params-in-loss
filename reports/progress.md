# Study progress

Updated 2026-11-25T17:11:28+00:00.

21 training/control records and 0 final evaluations are complete. This is 17.5% of 120 planned model milestones.

## Current record

**stories** has 12 completed runs. The next milestone is determined by the run matrix.

Pilot rates project 1.69 remaining confirmation GPU-hours, excluding validation, exports and uploads.

Statistical status: pending. Awaiting confirmatory runs.

**abstracts** has 9 completed runs. Current records: abstracts-pilot-s00-hessian_norm-r03-fp64 (queued after hybrid follow-up, 1,024 targets).

Pilot rates project 9.54 remaining confirmation GPU-hours, excluding validation, exports and uploads.

Statistical status: pending. Awaiting confirmatory runs.

## One-week feasibility

At the pre-test check on 2026-11-25T10:33:28+00:00, pilot timings projected 22.50 hours for all confirmatory training and scoring, with 141.73 hours of the week available for secondary pilots, setup, publication and interruptions. [Timing and GPU memory by method](../results/feasibility/one-week.json)

## TinyStories hybrid follow-up

17 of 48 full runs and 3 of 8 shared checkpoints complete. awaiting eight paired width measurements. [Per-seed widths and development scores](hybrid/results.md)

The first measured set of hybrid arms projects 33.68 further hours from that checkpoint, including the eight replays. With the original confirmations and final scoring, the projected remaining work at the check was 56.18 hours with 159.49 hours left in the week. [Wall-time assumptions, measured memory and inputs](../results/feasibility/hybrid-week.json)

The first seed included 4.11 hours between the last pre-restart update and the first resumed update. Excluding repetitions of that gap projects 4.91 hours of remaining hybrid work and 27.40 hours with the original confirmations and scoring. Both forecasts use actual observed wall time and apply from the first-seed checkpoint. [Restart-adjusted timing](../results/feasibility/hybrid-uptime.json)

## Monitoring

Inspect runs lasting over 10, 30 and 60 minutes at 5, 15 and 30 minute intervals respectively. The live dashboard refreshes between those checks. [Study design](plan.md) · [Run matrix](planned-runs.md) · [Experiment ledger](experiments/experiments.md)
