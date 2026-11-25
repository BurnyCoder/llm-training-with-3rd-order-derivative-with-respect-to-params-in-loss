# TinyStories · Always-on hybrid

Run `stories-hybrid-s21-always-r01` · [raw records](../../../results/stories-hybrid-s21-always-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Always-on hybrid | hybrid | 21 | 0.010 | 16,777,216 | 2.5459 | 12.7550 | — | — | 30,503 | complete |

Training time is 550.0 seconds. Peak allocated GPU memory is 621.3 MiB. Development token accuracy is 0.4616. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s21-always-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.229 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.57089 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.0042312 | No general better direction |
| Common score width | 1.0833 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08322, 1.08344] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.699547 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

## Restart verification

After the system restart, training resumed from update 3,712 and replayed 24 updates. Across 5 logged overlaps, the maximum absolute training NLL difference was 2.384e-07 nats per target and the maximum difference in the unclipped gradient norm was 1.192e-07. [Replay measurements](../../../results/verification/hybrid-s21-system-restart.json)

The process working-set high-water mark was 2,001.6 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner liked to run and play outside. Lily was happy to see his dog and play.
    
    One day, Max found a big hole in his mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make them lose them. One day, he asked his mom for help and Timmy said "Let's go on a walk!"
    
    In the end, Timmy got so upset that his dad

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun was shining in the mud and it was going to go back upstairs. But when the wind started to move, the wind made the wind coming and the sky set. 
