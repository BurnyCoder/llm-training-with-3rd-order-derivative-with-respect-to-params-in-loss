# TinyStories · Third derivative

Run `stories-confirm-s02-third-r01` · [raw records](../../../results/stories-confirm-s02-third-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Third derivative | confirm | 2 | 0.010 | 16,777,216 | 2.5444 | 12.7351 | — | — | 37,471 | complete |

Training time is 447.7 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4622. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s02-third-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.066 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.570884 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00413326 | No general better direction |
| Common score width | 1.0814 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08123, 1.08149] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.702187 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play outside in the park. One day, Max wanted to play with his friends, but he was still careful. 
    
    Max's friend, Bob, came over to play. Max saw Spot

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make things with water. One day, he asked his mom for help.
    
    "Let's go on a walk!" said the bunny.
    
    When he got to the park,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun wasing in the mud and it was going to the park. But the rain was not happy. The car was black and made a loud noise.
    
    The ravent
