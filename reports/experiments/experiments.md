# Experiment ledger

NLL is negative log-likelihood in nats per target token. A smaller value assigns more probability to the observed next tokens. The ratio sets the pilot regularizer-gradient magnitude relative to cross-entropy.

[Architecture, training algorithms, objectives and planned budgets](../planned-runs.md)

| Run | Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [abstracts-control-s00-initial-r00](./abstracts-control-s00-initial-r00/experiment.md) | Research abstracts | Initial checkpoint | control | 0 | 0.000 | 0 | 3.2517 | — | 0 | complete |
| [abstracts-control-s00-unigram-r00](./abstracts-control-s00-unigram-r00/experiment.md) | Research abstracts | Unigram | control | 0 | 0.000 | 0 | 7.3306 | — | 0 | complete |
| [abstracts-pilot-s00-ce-r00](./abstracts-pilot-s00-ce-r00/experiment.md) | Research abstracts | Ordinary AdamW | pilot | 0 | 0.000 | 65,536 | 3.1139 | — | 1,659 | complete |
| [abstracts-pilot-s00-hessian_norm-r03-fp64](./abstracts-pilot-s00-hessian_norm-r03-fp64/experiment.md) | Research abstracts | Squared Hessian norm | pilot | 0 | 0.030 | — | — | — | — | initializing |
| [abstracts-pilot-s00-third-r01-fp64](./abstracts-pilot-s00-third-r01-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.010 | 65,536 | 3.1142 | — | 189 | complete |
| [abstracts-pilot-s00-third-r03](./abstracts-pilot-s00-third-r03/experiment.md) | Research abstracts | Third derivative | diagnostic | 0 | 0.030 | 65,536 | 3.1168 | — | 907 | complete |
| [abstracts-pilot-s00-third-r03-fp64](./abstracts-pilot-s00-third-r03-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.030 | 65,536 | 3.1149 | — | 188 | complete |
| [abstracts-pilot-s00-third-r10-fp64](./abstracts-pilot-s00-third-r10-fp64/experiment.md) | Research abstracts | Third derivative | pilot | 0 | 0.100 | 65,536 | 3.1163 | — | 193 | complete |
| [abstracts-pilot-s00-trace-r01-fp64](./abstracts-pilot-s00-trace-r01-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.010 | 65,536 | 3.1140 | — | 435 | complete |
| [abstracts-pilot-s00-trace-r03-fp64](./abstracts-pilot-s00-trace-r03-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.030 | 65,536 | 3.1141 | — | 427 | complete |
| [abstracts-pilot-s00-trace-r10-fp64](./abstracts-pilot-s00-trace-r10-fp64/experiment.md) | Research abstracts | Hessian trace | pilot | 0 | 0.100 | 65,536 | 3.1143 | — | 431 | complete |
| [stories-control-s00-initial-r00](./stories-control-s00-initial-r00/experiment.md) | TinyStories | Initial checkpoint | control | 0 | 0.000 | 0 | 8.3437 | — | 0 | complete |
| [stories-control-s00-unigram-r00](./stories-control-s00-unigram-r00/experiment.md) | TinyStories | Unigram | control | 0 | 0.000 | 0 | 6.0036 | — | 0 | complete |
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
