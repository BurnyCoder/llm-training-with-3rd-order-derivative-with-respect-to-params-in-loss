# Experiment ledger

NLL is negative log-likelihood in nats per target token. A smaller value assigns more probability to the observed next tokens. The ratio sets the pilot regularizer-gradient magnitude relative to cross-entropy.

[Architecture, training algorithms, objectives and planned budgets](../planned-runs.md)

| Run | Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [abstracts-control-s00-initial-r00](./abstracts-control-s00-initial-r00/experiment.md) | Research abstracts | Initial checkpoint | control | 0 | 0.000 | 0 | 3.2517 | — | 0 | complete |
| [abstracts-control-s00-unigram-r00](./abstracts-control-s00-unigram-r00/experiment.md) | Research abstracts | Unigram | control | 0 | 0.000 | 0 | 7.3306 | — | 0 | complete |
| [abstracts-pilot-s00-ce-r00](./abstracts-pilot-s00-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | pilot | 0 | 0.000 | 65,536 | 3.1139 | — | 1,659 | complete |
| [abstracts-pilot-s00-hessian_norm-r03-fp64](./abstracts-pilot-s00-hessian_norm-r03-fp64/experiment.md) | Research abstracts | Squared Hessian norm | pilot | 0 | 0.030 | 1,024 | — | — | — | queued after hybrid follow-up |
| [abstracts-pilot-s00-third-r01-fp64](./abstracts-pilot-s00-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.010 | 65,536 | 3.1142 | — | 189 | complete |
| [abstracts-pilot-s00-third-r03](./abstracts-pilot-s00-third-r03/experiment.md) | Research abstracts | Third derivative | diagnostic | 0 | 0.030 | 65,536 | 3.1168 | — | 907 | complete |
| [abstracts-pilot-s00-third-r03-fp64](./abstracts-pilot-s00-third-r03-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.030 | 65,536 | 3.1149 | — | 188 | complete |
| [abstracts-pilot-s00-third-r10-fp64](./abstracts-pilot-s00-third-r10-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.100 | 65,536 | 3.1163 | — | 193 | complete |
| [abstracts-pilot-s00-trace-r01-fp64](./abstracts-pilot-s00-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.010 | 65,536 | 3.1140 | — | 435 | complete |
| [abstracts-pilot-s00-trace-r03-fp64](./abstracts-pilot-s00-trace-r03-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.030 | 65,536 | 3.1141 | — | 427 | complete |
| [abstracts-pilot-s00-trace-r10-fp64](./abstracts-pilot-s00-trace-r10-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.100 | 65,536 | 3.1143 | — | 431 | complete |
| [stories-branch-s21-trunk-r01](./stories-branch-s21-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 21 | 0.010 | 8,388,608 | 2.7577 | — | 69,581 | complete |
| [stories-branch-s22-trunk-r01](./stories-branch-s22-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 22 | 0.010 | 8,388,608 | 2.7573 | — | 61,905 | complete |
| [stories-branch-s23-trunk-r01](./stories-branch-s23-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 23 | 0.010 | 8,388,608 | 2.7525 | — | 54,841 | complete |
| [stories-branch-s24-trunk-r01](./stories-branch-s24-trunk-r01/experiment.md) | TinyStories | Shared trace checkpoint | branch | 24 | 0.010 | 8,388,608 | 2.7639 | — | 60,780 | complete |
| [stories-control-s00-initial-r00](./stories-control-s00-initial-r00/experiment.md) | TinyStories | Initial checkpoint | control | 0 | 0.000 | 0 | 8.3437 | — | 0 | complete |
| [stories-control-s00-unigram-r00](./stories-control-s00-unigram-r00/experiment.md) | TinyStories | Unigram | control | 0 | 0.000 | 0 | 6.0036 | — | 0 | complete |
| [stories-hybrid-s21-adaptive-r01](./stories-hybrid-s21-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | — | 43,973 | complete |
| [stories-hybrid-s21-always-r01](./stories-hybrid-s21-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | — | 30,503 | complete |
| [stories-hybrid-s21-late-r01](./stories-hybrid-s21-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5461 | — | 41,141 | complete |
| [stories-hybrid-s21-strong-r01](./stories-hybrid-s21-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 21 | 0.010 | 16,777,216 | 2.5460 | — | 66,667 | complete |
| [stories-hybrid-s21-trace-r01](./stories-hybrid-s21-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | — | 64,342 | complete |
| [stories-hybrid-s22-adaptive-r01](./stories-hybrid-s22-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | — | 37,992 | complete |
| [stories-hybrid-s22-always-r01](./stories-hybrid-s22-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5460 | — | 25,017 | complete |
| [stories-hybrid-s22-late-r01](./stories-hybrid-s22-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5464 | — | 39,514 | complete |
| [stories-hybrid-s22-replay-r01](./stories-hybrid-s22-replay-r01/experiment.md) | TinyStories | Cross-seed replay | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | — | 36,853 | complete |
| [stories-hybrid-s22-strong-r01](./stories-hybrid-s22-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 22 | 0.010 | 16,777,216 | 2.5464 | — | 60,263 | complete |
| [stories-hybrid-s22-trace-r01](./stories-hybrid-s22-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 22 | 0.010 | 16,777,216 | 2.5463 | — | 61,689 | complete |
| [stories-hybrid-s23-adaptive-r01](./stories-hybrid-s23-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | — | 37,872 | complete |
| [stories-hybrid-s23-always-r01](./stories-hybrid-s23-always-r01/experiment.md) | TinyStories | Always-on hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5429 | — | 32,400 | complete |
| [stories-hybrid-s23-late-r01](./stories-hybrid-s23-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5425 | — | 40,662 | complete |
| [stories-hybrid-s23-replay-r01](./stories-hybrid-s23-replay-r01/experiment.md) | TinyStories | Cross-seed replay | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | — | 35,140 | complete |
| [stories-hybrid-s23-strong-r01](./stories-hybrid-s23-strong-r01/experiment.md) | TinyStories | Stronger trace | hybrid | 23 | 0.010 | 16,777,216 | 2.5424 | — | 60,806 | complete |
| [stories-hybrid-s23-trace-r01](./stories-hybrid-s23-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | — | 59,471 | complete |
| [stories-hybrid-s24-adaptive-r01](./stories-hybrid-s24-adaptive-r01/experiment.md) | TinyStories | Curvature-dependent hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5545 | — | 41,647 | complete |
| [stories-hybrid-s24-late-r01](./stories-hybrid-s24-late-r01/experiment.md) | TinyStories | Fixed late hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5547 | — | 42,225 | complete |
| [stories-hybrid-s24-trace-r01](./stories-hybrid-s24-trace-r01/experiment.md) | TinyStories | Hessian trace | hybrid | 24 | 0.010 | 16,777,216 | 2.5545 | — | 63,221 | complete |
| [stories-pilot-s00-ce-r00](./stories-pilot-s00-ce-r00/experiment.md) | TinyStories | Ordinary AdamW | pilot | 0 | 0.000 | 2,097,152 | 3.8770 | — | 123,871 | complete |
| [stories-pilot-s00-combined-r01](./stories-pilot-s00-combined-r01/experiment.md) | TinyStories | Trace + third derivative | pilot | 0 | 0.010 | 2,097,152 | 3.8772 | — | 41,030 | complete |
| [stories-pilot-s00-hessian_norm-r03](./stories-pilot-s00-hessian_norm-r03/experiment.md) | TinyStories | Squared Hessian norm | pilot | 0 | 0.030 | 2,097,152 | 3.8787 | — | 83,790 | complete |
| [stories-pilot-s00-sham-r01](./stories-pilot-s00-sham-r01/experiment.md) | TinyStories | Randomized gradient signs | pilot | 0 | 0.010 | 2,097,152 | 3.8773 | — | 50,914 | complete |
| [stories-pilot-s00-third-r01](./stories-pilot-s00-third-r01/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.010 | 2,097,152 | 3.8769 | — | 42,481 | complete |
| [stories-pilot-s00-third-r03](./stories-pilot-s00-third-r03/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.030 | 2,097,152 | 3.8778 | — | 46,072 | complete |
| [stories-pilot-s00-third-r10](./stories-pilot-s00-third-r10/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.100 | 2,097,152 | 3.8827 | — | 43,901 | complete |
| [stories-pilot-s00-trace-r01](./stories-pilot-s00-trace-r01/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.010 | 2,097,152 | 3.8773 | — | 73,185 | complete |
| [stories-pilot-s00-trace-r03](./stories-pilot-s00-trace-r03/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.030 | 2,097,152 | 3.8802 | — | 68,106 | complete |
| [stories-pilot-s00-trace-r10](./stories-pilot-s00-trace-r10/experiment.md) | TinyStories | Hessian trace | pilot | 0 | 0.100 | 2,097,152 | 3.8979 | — | 70,730 | complete |
