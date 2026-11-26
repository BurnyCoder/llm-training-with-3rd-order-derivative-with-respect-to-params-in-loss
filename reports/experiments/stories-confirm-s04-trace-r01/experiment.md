# TinyStories · Hessian trace

Run `stories-confirm-s04-trace-r01` · [raw records](../../../results/stories-confirm-s04-trace-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Hessian trace | confirm | 4 | 0.010 | 16,777,216 | 2.5438 | 12.7276 | 2.5444 | 12.7350 | 70,292 | complete |

Training time is 238.7 seconds. Peak allocated GPU memory is 608.2 MiB. Full-development token accuracy is 0.4630. Test token accuracy is 0.4631.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s04-trace-r01/config.json)

Training and development · Complete. Frozen test · Complete. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.638 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.588306 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00526637 | No general better direction |
| Common score width | 1.0816 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08148, 1.08170] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.703512 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing, swing and swing on the sky. One day, Max found a big rock in his garden. He got it up and started to jump! Max started to mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     yarn for the monster. One day he decided to take a bit of help. He reached on the jar and opened it, but he couldn't find it. 
    
    He thought of a way to

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day he decided to explore the forest. He carefully grabbed a trackcter and started to dig in the sand. He opened the cooler and he saw some shiny and strong tide. He
