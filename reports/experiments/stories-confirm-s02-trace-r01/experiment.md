# TinyStories · Hessian trace

Run `stories-confirm-s02-trace-r01` · [raw records](../../../results/stories-confirm-s02-trace-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Hessian trace | confirm | 2 | 0.010 | 16,777,216 | 2.5446 | 12.7377 | 2.5450 | 12.7432 | 68,581 | complete |

Training time is 244.6 seconds. Peak allocated GPU memory is 608.2 MiB. Full-development token accuracy is 0.4623. Test token accuracy is 0.4626.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s02-trace-r01/config.json)

Training and development · Complete. Frozen test · Complete. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.038 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.577657 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00413847 | No general better direction |
| Common score width | 1.0815 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08135, 1.08161] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.702051 | ↓ Lower means less local bending in score space |

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
    
    Tommy was so excited! His mom gave him out and said, "Yay! You can do it!

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, he decided to dig something in the mud and he noticed something shiny in the sky. He tried to use it to ring, but it was too dangerous.
    
    Suddenly, the ravent
