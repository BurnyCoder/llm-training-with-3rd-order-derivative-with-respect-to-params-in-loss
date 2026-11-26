# Experiment ledger

NLL is negative log-likelihood in nats per target token. A smaller value assigns more probability to the observed next tokens. Perplexity (PPL) is the exponential of the full-corpus NLL. Lower is better within a corpus and tokenizer. The ratio sets the pilot regularizer-gradient magnitude relative to cross-entropy.

[Architecture, training algorithms, objectives and planned budgets](../planned-runs.md)

**Snapshot at 2026-11-26T11:46:47+00:00** · 201/305 experimental milestones complete.

**Recorded activity** · Experiments paused by request. The remaining runs have no scheduled start date.

**First run on resumption** · Research abstracts · Third derivative · confirm seed 5 (1%).

The measured remaining-time scenarios are 18.82–19.42 machine-hours.

[Status of every planned run](../planned-runs.md#current-evidence-and-remaining-runs)

| Run | Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [abstracts-confirm-s01-ce-r00](./abstracts-confirm-s01-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | confirm | 1 | 0.000 | 524,288 | 3.0368 | 20.8387 | — | — | 1,507 | complete |
| [abstracts-confirm-s01-third-r01-fp64](./abstracts-confirm-s01-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | confirm | 1 | 0.010 | 524,288 | 3.0368 | 20.8375 | — | — | 128 | complete |
| [abstracts-confirm-s01-trace-r01-fp64](./abstracts-confirm-s01-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | confirm | 1 | 0.010 | 524,288 | 3.0367 | 20.8370 | — | — | 350 | complete |
| [abstracts-confirm-s02-ce-r00](./abstracts-confirm-s02-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | confirm | 2 | 0.000 | 524,288 | 3.0373 | 20.8494 | — | — | 1,591 | complete |
| [abstracts-confirm-s02-third-r01-fp64](./abstracts-confirm-s02-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | confirm | 2 | 0.010 | 524,288 | 3.0376 | 20.8543 | — | — | 107 | complete |
| [abstracts-confirm-s02-trace-r01-fp64](./abstracts-confirm-s02-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | confirm | 2 | 0.010 | 524,288 | 3.0373 | 20.8484 | — | — | 297 | complete |
| [abstracts-confirm-s03-ce-r00](./abstracts-confirm-s03-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | confirm | 3 | 0.000 | 524,288 | 3.0371 | 20.8444 | — | — | 1,647 | complete |
| [abstracts-confirm-s03-third-r01-fp64](./abstracts-confirm-s03-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | confirm | 3 | 0.010 | 524,288 | 3.0371 | 20.8442 | — | — | 118 | complete |
| [abstracts-confirm-s03-trace-r01-fp64](./abstracts-confirm-s03-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | confirm | 3 | 0.010 | 524,288 | 3.0370 | 20.8418 | — | — | 328 | complete |
| [abstracts-confirm-s04-ce-r00](./abstracts-confirm-s04-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | confirm | 4 | 0.000 | 524,288 | 3.0367 | 20.8373 | — | — | 1,610 | complete |
| [abstracts-confirm-s04-third-r01-fp64](./abstracts-confirm-s04-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | confirm | 4 | 0.010 | 524,288 | 3.0369 | 20.8408 | — | — | 128 | complete |
| [abstracts-confirm-s04-trace-r01-fp64](./abstracts-confirm-s04-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | confirm | 4 | 0.010 | 524,288 | 3.0367 | 20.8365 | — | — | 338 | complete |
| [abstracts-confirm-s05-third-r01-fp64](./abstracts-confirm-s05-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | confirm | 5 | 0.010 | 458,752 | — | — | — | — | — | paused |
| [abstracts-control-s00-initial-r00](./abstracts-control-s00-initial-r00/experiment.md) | Research abstracts | Initial checkpoint | control | 0 | 0.000 | 0 | 3.2517 | 25.8335 | — | — | 0 | complete |
| [abstracts-control-s00-unigram-r00](./abstracts-control-s00-unigram-r00/experiment.md) | Research abstracts | Unigram | control | 0 | 0.000 | 0 | 7.3306 | 1,526.3141 | — | — | 0 | complete |
| [abstracts-pilot-s00-ce-r00](./abstracts-pilot-s00-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | pilot | 0 | 0.000 | 65,536 | 3.1139 | 22.5097 | — | — | 1,659 | complete |
| [abstracts-pilot-s00-combined-r01-fp64](./abstracts-pilot-s00-combined-r01-fp64/experiment.md) | Research abstracts | Trace + third derivative | pilot | 0 | 0.010 | 65,536 | 3.1143 | 22.5172 | — | — | 137 | complete |
| [abstracts-pilot-s00-hessian_norm-r03-fp64](./abstracts-pilot-s00-hessian_norm-r03-fp64/experiment.md) | Research abstracts | Squared Hessian norm | pilot | 0 | 0.030 | 65,536 | 3.1139 | 22.5088 | — | — | 413 | complete |
| [abstracts-pilot-s00-sham-r01-fp64](./abstracts-pilot-s00-sham-r01-fp64/experiment.md) | Research abstracts | Randomized gradient signs | pilot | 0 | 0.010 | 65,536 | 3.1142 | 22.5153 | — | — | 171 | complete |
| [abstracts-pilot-s00-third-r01-fp64](./abstracts-pilot-s00-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.010 | 65,536 | 3.1142 | 22.5165 | — | — | 189 | complete |
| [abstracts-pilot-s00-third-r03](./abstracts-pilot-s00-third-r03/experiment.md) | Research abstracts | Third derivative | diagnostic | 0 | 0.030 | 65,536 | 3.1168 | 22.5739 | — | — | 907 | complete |
| [abstracts-pilot-s00-third-r03-fp64](./abstracts-pilot-s00-third-r03-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.030 | 65,536 | 3.1149 | 22.5303 | — | — | 188 | complete |
| [abstracts-pilot-s00-third-r10-fp64](./abstracts-pilot-s00-third-r10-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.100 | 65,536 | 3.1163 | 22.5630 | — | — | 193 | complete |
| [abstracts-pilot-s00-trace-r01-fp64](./abstracts-pilot-s00-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.010 | 65,536 | 3.1140 | 22.5103 | — | — | 435 | complete |
| [abstracts-pilot-s00-trace-r03-fp64](./abstracts-pilot-s00-trace-r03-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.030 | 65,536 | 3.1141 | 22.5136 | — | — | 427 | complete |
| [abstracts-pilot-s00-trace-r10-fp64](./abstracts-pilot-s00-trace-r10-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.100 | 65,536 | 3.1143 | 22.5172 | — | — | 431 | complete |
| [stories-branch-s21-trunk-r01](./stories-branch-s21-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 21 | 0.010 | 8,388,608 | 2.7577 | 15.7633 | — | — | 69,581 | complete |
| [stories-branch-s22-trunk-r01](./stories-branch-s22-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 22 | 0.010 | 8,388,608 | 2.7573 | 15.7576 | — | — | 61,905 | complete |
| [stories-branch-s23-trunk-r01](./stories-branch-s23-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 23 | 0.010 | 8,388,608 | 2.7525 | 15.6817 | — | — | 54,841 | complete |
| [stories-branch-s24-trunk-r01](./stories-branch-s24-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 24 | 0.010 | 8,388,608 | 2.7639 | 15.8611 | — | — | 60,780 | complete |
| [stories-branch-s25-trunk-r01](./stories-branch-s25-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 25 | 0.010 | 8,388,608 | 2.7621 | 15.8325 | — | — | 45,520 | complete |
| [stories-confirm-s01-ce-r00](./stories-confirm-s01-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 1 | 0.000 | 16,777,216 | 2.5477 | 12.7779 | 2.5479 | 12.7798 | 113,244 | complete |
| [stories-confirm-s01-third-r01](./stories-confirm-s01-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 1 | 0.010 | 16,777,216 | 2.5477 | 12.7779 | 2.5479 | 12.7808 | 32,018 | complete |
| [stories-confirm-s01-trace-r01](./stories-confirm-s01-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 1 | 0.010 | 16,777,216 | 2.5480 | 12.7811 | 2.5482 | 12.7836 | 65,975 | complete |
| [stories-confirm-s02-ce-r00](./stories-confirm-s02-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 2 | 0.000 | 16,777,216 | 2.5440 | 12.7299 | 2.5445 | 12.7366 | 130,533 | complete |
| [stories-confirm-s02-third-r01](./stories-confirm-s02-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 2 | 0.010 | 16,777,216 | 2.5444 | 12.7351 | 2.5449 | 12.7422 | 37,471 | complete |
| [stories-confirm-s02-trace-r01](./stories-confirm-s02-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 2 | 0.010 | 16,777,216 | 2.5446 | 12.7377 | 2.5450 | 12.7432 | 68,581 | complete |
| [stories-confirm-s03-ce-r00](./stories-confirm-s03-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 3 | 0.000 | 16,777,216 | 2.5489 | 12.7924 | 2.5498 | 12.8046 | 131,156 | complete |
| [stories-confirm-s03-third-r01](./stories-confirm-s03-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 3 | 0.010 | 16,777,216 | 2.5486 | 12.7898 | 2.5496 | 12.8019 | 38,410 | complete |
| [stories-confirm-s03-trace-r01](./stories-confirm-s03-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 3 | 0.010 | 16,777,216 | 2.5490 | 12.7947 | 2.5500 | 12.8069 | 66,757 | complete |
| [stories-confirm-s04-ce-r00](./stories-confirm-s04-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 4 | 0.000 | 16,777,216 | 2.5431 | 12.7193 | 2.5438 | 12.7281 | 129,520 | complete |
| [stories-confirm-s04-third-r01](./stories-confirm-s04-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 4 | 0.010 | 16,777,216 | 2.5431 | 12.7196 | 2.5438 | 12.7278 | 40,663 | complete |
| [stories-confirm-s04-trace-r01](./stories-confirm-s04-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 4 | 0.010 | 16,777,216 | 2.5438 | 12.7276 | 2.5444 | 12.7350 | 70,292 | complete |
| [stories-confirm-s05-ce-r00](./stories-confirm-s05-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 5 | 0.000 | 16,777,216 | 2.5421 | 12.7070 | 2.5417 | 12.7017 | 131,166 | complete |
| [stories-confirm-s05-third-r01](./stories-confirm-s05-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 5 | 0.010 | 16,777,216 | 2.5423 | 12.7091 | 2.5419 | 12.7033 | 39,988 | complete |
| [stories-confirm-s05-trace-r01](./stories-confirm-s05-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 5 | 0.010 | 16,777,216 | 2.5424 | 12.7104 | 2.5419 | 12.7043 | 70,286 | complete |
| [stories-confirm-s06-ce-r00](./stories-confirm-s06-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 6 | 0.000 | 16,777,216 | 2.5459 | 12.7553 | 2.5457 | 12.7523 | 132,129 | complete |
| [stories-confirm-s06-third-r01](./stories-confirm-s06-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 6 | 0.010 | 16,777,216 | 2.5455 | 12.7491 | 2.5450 | 12.7436 | 41,244 | complete |
| [stories-confirm-s06-trace-r01](./stories-confirm-s06-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 6 | 0.010 | 16,777,216 | 2.5453 | 12.7474 | 2.5452 | 12.7457 | 71,044 | complete |
| [stories-confirm-s07-ce-r00](./stories-confirm-s07-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 7 | 0.000 | 16,777,216 | 2.5404 | 12.6847 | 2.5412 | 12.6943 | 131,830 | complete |
| [stories-confirm-s07-third-r01](./stories-confirm-s07-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 7 | 0.010 | 16,777,216 | 2.5405 | 12.6866 | 2.5413 | 12.6965 | 41,583 | complete |
| [stories-confirm-s07-trace-r01](./stories-confirm-s07-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 7 | 0.010 | 16,777,216 | 2.5407 | 12.6888 | 2.5416 | 12.6994 | 72,117 | complete |
| [stories-confirm-s08-ce-r00](./stories-confirm-s08-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | confirm | 8 | 0.000 | 16,777,216 | 2.5406 | 12.6879 | 2.5395 | 12.6733 | 131,237 | complete |
| [stories-confirm-s08-third-r01](./stories-confirm-s08-third-r01/experiment.md) | TinyStories | Third derivative | confirm | 8 | 0.010 | 16,777,216 | 2.5402 | 12.6826 | 2.5389 | 12.6660 | 40,220 | complete |
| [stories-confirm-s08-trace-r01](./stories-confirm-s08-trace-r01/experiment.md) | TinyStories | Hessian trace | confirm | 8 | 0.010 | 16,777,216 | 2.5408 | 12.6902 | 2.5395 | 12.6735 | 69,513 | complete |
| [stories-control-s00-initial-r00](./stories-control-s00-initial-r00/experiment.md) | TinyStories | Initial checkpoint | control | 0 | 0.000 | 0 | 8.3437 | 4,203.5319 | — | — | 0 | complete |
| [stories-control-s00-unigram-r00](./stories-control-s00-unigram-r00/experiment.md) | TinyStories | Unigram | control | 0 | 0.000 | 0 | 6.0036 | 404.8654 | — | — | 0 | complete |
| [stories-hybrid-s21-adaptive-r01](./stories-hybrid-s21-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | 12.7548 | — | — | 43,973 | complete |
| [stories-hybrid-s21-always-r01](./stories-hybrid-s21-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | 12.7550 | — | — | 30,503 | complete |
| [stories-hybrid-s21-late-r01](./stories-hybrid-s21-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5461 | 12.7574 | — | — | 41,141 | complete |
| [stories-hybrid-s21-strong-r01](./stories-hybrid-s21-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 21 | 0.010 | 16,777,216 | 2.5460 | 12.7561 | — | — | 66,667 | complete |
| [stories-hybrid-s21-trace-r01](./stories-hybrid-s21-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | 12.7547 | — | — | 64,342 | complete |
| [stories-hybrid-s22-adaptive-r01](./stories-hybrid-s22-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | 12.7599 | — | — | 37,992 | complete |
| [stories-hybrid-s22-always-r01](./stories-hybrid-s22-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5460 | 12.7556 | — | — | 25,017 | complete |
| [stories-hybrid-s22-late-r01](./stories-hybrid-s22-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5464 | 12.7617 | — | — | 39,514 | complete |
| [stories-hybrid-s22-replay-r01](./stories-hybrid-s22-replay-r01/experiment.md) | TinyStories | Cross-seed replay | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | 12.7599 | — | — | 36,853 | complete |
| [stories-hybrid-s22-strong-r01](./stories-hybrid-s22-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 22 | 0.010 | 16,777,216 | 2.5464 | 12.7609 | — | — | 60,263 | complete |
| [stories-hybrid-s22-trace-r01](./stories-hybrid-s22-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | 12.7599 | — | — | 61,689 | complete |
| [stories-hybrid-s23-adaptive-r01](./stories-hybrid-s23-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | 12.7084 | — | — | 37,872 | complete |
| [stories-hybrid-s23-always-r01](./stories-hybrid-s23-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5429 | 12.7163 | — | — | 32,400 | complete |
| [stories-hybrid-s23-late-r01](./stories-hybrid-s23-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5425 | 12.7110 | — | — | 40,662 | complete |
| [stories-hybrid-s23-replay-r01](./stories-hybrid-s23-replay-r01/experiment.md) | TinyStories | Cross-seed replay | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | 12.7083 | — | — | 35,140 | complete |
| [stories-hybrid-s23-strong-r01](./stories-hybrid-s23-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 23 | 0.010 | 16,777,216 | 2.5424 | 12.7096 | — | — | 60,806 | complete |
| [stories-hybrid-s23-trace-r01](./stories-hybrid-s23-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | 12.7083 | — | — | 59,471 | complete |
| [stories-hybrid-s24-adaptive-r01](./stories-hybrid-s24-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5545 | 12.8645 | — | — | 41,647 | complete |
| [stories-hybrid-s24-always-r01](./stories-hybrid-s24-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5542 | 12.8610 | — | — | 33,941 | complete |
| [stories-hybrid-s24-late-r01](./stories-hybrid-s24-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5547 | 12.8671 | — | — | 42,225 | complete |
| [stories-hybrid-s24-replay-r01](./stories-hybrid-s24-replay-r01/experiment.md) | TinyStories | Cross-seed replay | hybrid | 24 | 0.010 | 16,777,216 | 2.5545 | 12.8645 | — | — | 46,104 | complete |
| [stories-hybrid-s24-strong-r01](./stories-hybrid-s24-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 24 | 0.010 | 16,777,216 | 2.5546 | 12.8657 | — | — | 63,357 | complete |
| [stories-hybrid-s24-trace-r01](./stories-hybrid-s24-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 24 | 0.010 | 16,777,216 | 2.5545 | 12.8645 | — | — | 63,221 | complete |
| [stories-pilot-s00-ce-r00](./stories-pilot-s00-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | pilot | 0 | 0.000 | 2,097,152 | 3.8770 | 48.2780 | — | — | 123,871 | complete |
| [stories-pilot-s00-combined-r01](./stories-pilot-s00-combined-r01/experiment.md) | TinyStories | Trace + third derivative | pilot | 0 | 0.010 | 2,097,152 | 3.8772 | 48.2875 | — | — | 41,030 | complete |
| [stories-pilot-s00-hessian_norm-r03](./stories-pilot-s00-hessian_norm-r03/experiment.md) | TinyStories | Squared Hessian norm | pilot | 0 | 0.030 | 2,097,152 | 3.8787 | 48.3603 | — | — | 83,790 | complete |
| [stories-pilot-s00-sham-r01](./stories-pilot-s00-sham-r01/experiment.md) | TinyStories | Randomized gradient signs | pilot | 0 | 0.010 | 2,097,152 | 3.8773 | 48.2914 | — | — | 50,914 | complete |
| [stories-pilot-s00-third-r01](./stories-pilot-s00-third-r01/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.010 | 2,097,152 | 3.8769 | 48.2758 | — | — | 42,481 | complete |
| [stories-pilot-s00-third-r03](./stories-pilot-s00-third-r03/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.030 | 2,097,152 | 3.8778 | 48.3167 | — | — | 46,072 | complete |
| [stories-pilot-s00-third-r10](./stories-pilot-s00-third-r10/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.100 | 2,097,152 | 3.8827 | 48.5556 | — | — | 43,901 | complete |
| [stories-pilot-s00-trace-r01](./stories-pilot-s00-trace-r01/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.010 | 2,097,152 | 3.8773 | 48.2921 | — | — | 73,185 | complete |
| [stories-pilot-s00-trace-r03](./stories-pilot-s00-trace-r03/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.030 | 2,097,152 | 3.8802 | 48.4360 | — | — | 68,106 | complete |
| [stories-pilot-s00-trace-r10](./stories-pilot-s00-trace-r10/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.100 | 2,097,152 | 3.8979 | 49.2988 | — | — | 70,730 | complete |
