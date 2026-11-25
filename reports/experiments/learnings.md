# Experimental learnings

**TinyStories.** Awaiting paired test results (0 of 8 full-horizon training triplets).

**Research abstracts.** Awaiting paired test results (0 of 8 full-horizon training triplets).

Independent random signs include mixed weight derivatives in the expected penalty. The trace implementation motivating the gradient check converted its estimate to a Python number. [Derivation and references](../literature-review.md)

- [abstracts-control-s00-initial-r00](./abstracts-control-s00-initial-r00/experiment.md) — The observed development NLL is 3.2517 nats per target token.

- [abstracts-control-s00-unigram-r00](./abstracts-control-s00-unigram-r00/experiment.md) — The observed development NLL is 7.3306 nats per target token.

- [abstracts-pilot-s00-ce-r00](./abstracts-pilot-s00-ce-r00/experiment.md) — Development NLL changed by -0.1172 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-hessian_norm-r03-fp64](./abstracts-pilot-s00-hessian_norm-r03-fp64/experiment.md) — A development observation is pending.

- [abstracts-pilot-s00-third-r01-fp64](./abstracts-pilot-s00-third-r01-fp64/experiment.md) — Development NLL changed by -0.1168 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-third-r03](./abstracts-pilot-s00-third-r03/experiment.md) — This original FP32 adapter run is preserved as a numerical diagnostic. The same-probe full-checkpoint audit found substantial rounding error in both the penalty and its training gradient. Strength selection and confirmatory inference use separately named FP64 derivative runs. The run ledger records 1 interrupted attempt(s).

- [abstracts-pilot-s00-third-r03-fp64](./abstracts-pilot-s00-third-r03-fp64/experiment.md) — Development NLL changed by -0.1165 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-third-r10-fp64](./abstracts-pilot-s00-third-r10-fp64/experiment.md) — Development NLL changed by -0.1164 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-trace-r01-fp64](./abstracts-pilot-s00-trace-r01-fp64/experiment.md) — Development NLL changed by -0.1171 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-trace-r03-fp64](./abstracts-pilot-s00-trace-r03-fp64/experiment.md) — Development NLL changed by -0.1168 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [abstracts-pilot-s00-trace-r10-fp64](./abstracts-pilot-s00-trace-r10-fp64/experiment.md) — Development NLL changed by -0.1172 nats per target token from 4,096 to 65,536 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-branch-s21-trunk-r01](./stories-branch-s21-trunk-r01/experiment.md) — Development NLL changed by -3.2700 nats per target token from 524,288 to 8,388,608 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-branch-s22-trunk-r01](./stories-branch-s22-trunk-r01/experiment.md) — Development NLL changed by -3.2794 nats per target token from 524,288 to 8,388,608 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-control-s00-initial-r00](./stories-control-s00-initial-r00/experiment.md) — The observed development NLL is 8.3437 nats per target token.

- [stories-control-s00-unigram-r00](./stories-control-s00-unigram-r00/experiment.md) — The observed development NLL is 6.0036 nats per target token.

- [stories-hybrid-s21-adaptive-r01](./stories-hybrid-s21-adaptive-r01/experiment.md) — Development NLL changed by -0.1838 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s21-always-r01](./stories-hybrid-s21-always-r01/experiment.md) — Development NLL changed by -3.4880 nats per target token from 524,288 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds. After the system restart, training resumed from update 3,712 and replayed 24 updates. Across 5 logged overlaps, the maximum absolute training NLL difference was 2.384e-07 nats per target and the maximum difference in the unclipped gradient norm was 1.192e-07. [Replay measurements](../../../results/verification/hybrid-s21-system-restart.json)

- [stories-hybrid-s21-late-r01](./stories-hybrid-s21-late-r01/experiment.md) — Development NLL changed by -0.1837 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s21-strong-r01](./stories-hybrid-s21-strong-r01/experiment.md) — Development NLL changed by -0.1836 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s21-trace-r01](./stories-hybrid-s21-trace-r01/experiment.md) — Development NLL changed by -0.1838 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-adaptive-r01](./stories-hybrid-s22-adaptive-r01/experiment.md) — Development NLL changed by -0.1860 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-always-r01](./stories-hybrid-s22-always-r01/experiment.md) — Development NLL changed by -3.4852 nats per target token from 524,288 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-late-r01](./stories-hybrid-s22-late-r01/experiment.md) — Development NLL changed by -0.1858 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-replay-r01](./stories-hybrid-s22-replay-r01/experiment.md) — Development NLL changed by -0.0581 nats per target token from 8,912,896 to 10,485,760 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-strong-r01](./stories-hybrid-s22-strong-r01/experiment.md) — Development NLL changed by -0.1859 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

- [stories-hybrid-s22-trace-r01](./stories-hybrid-s22-trace-r01/experiment.md) — Development NLL changed by -0.1860 nats per target token from 8,912,896 to 16,777,216 training targets. Attribution to the regularizer uses matched comparisons across seeds.

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
