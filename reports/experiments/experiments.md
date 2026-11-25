# Experiment ledger

NLL is negative log-likelihood in nats per target token. A smaller value assigns more probability to the observed next tokens. The ratio sets the pilot regularizer-gradient magnitude relative to cross-entropy.

[Architecture, training algorithms, objectives and planned budgets](../planned-runs.md)

| Run | Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [stories-pilot-s00-third-r03](./stories-pilot-s00-third-r03/experiment.md) | TinyStories | Third derivative | pilot | 0 | 0.030 | 2,097,152 | 3.8778 | — | 46,072 | complete |
