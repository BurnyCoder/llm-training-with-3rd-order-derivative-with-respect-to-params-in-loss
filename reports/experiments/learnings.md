# Experimental learnings

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

Independent random signs include mixed weight derivatives in the expected penalty. The trace implementation motivating the gradient check converted its estimate to a Python number. [Derivation and references](../literature-review.md)

- [abstracts-control-s00-initial-r00](./abstracts-control-s00-initial-r00/experiment.md) — A development observation is pending.

- [abstracts-pilot-s00-third-r03](./abstracts-pilot-s00-third-r03/experiment.md) — This original FP32 adapter run is preserved as a numerical diagnostic. The same-probe full-checkpoint audit found substantial rounding error in both the penalty and its training gradient. Strength selection and confirmatory inference use separately named FP64 derivative runs. The run ledger records 1 interrupted attempt(s).

- [stories-control-s00-initial-r00](./stories-control-s00-initial-r00/experiment.md) — The observed development NLL is 8.3437 nats per target token.

- [stories-control-s00-unigram-r00](./stories-control-s00-unigram-r00/experiment.md) — The observed development NLL is 6.0036 nats per target token.

- [stories-pilot-s00-ce-r00](./stories-pilot-s00-ce-r00/experiment.md) — Development NLL changed by -3.2138 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-combined-r01](./stories-pilot-s00-combined-r01/experiment.md) — Development NLL changed by -3.2142 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-hessian_norm-r03](./stories-pilot-s00-hessian_norm-r03/experiment.md) — Development NLL changed by -3.2145 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-sham-r01](./stories-pilot-s00-sham-r01/experiment.md) — Development NLL changed by -3.2137 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-third-r01](./stories-pilot-s00-third-r01/experiment.md) — Development NLL changed by -3.2143 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-third-r03](./stories-pilot-s00-third-r03/experiment.md) — Development NLL changed by -3.2149 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-third-r10](./stories-pilot-s00-third-r10/experiment.md) — Development NLL changed by -3.2156 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-trace-r01](./stories-pilot-s00-trace-r01/experiment.md) — Development NLL changed by -3.2134 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-trace-r03](./stories-pilot-s00-trace-r03/experiment.md) — Development NLL changed by -3.2115 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-pilot-s00-trace-r10](./stories-pilot-s00-trace-r10/experiment.md) — Development NLL changed by -3.2006 nats per target token from 131,072 to 2,097,152 training targets. Attribution to the regularizer uses matched comparisons across seeds.
