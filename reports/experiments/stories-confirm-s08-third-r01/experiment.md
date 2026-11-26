# TinyStories · Third derivative

Run `stories-confirm-s08-third-r01` · [raw records](../../../results/stories-confirm-s08-third-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Third derivative | confirm | 8 | 0.010 | 16,777,216 | 2.5402 | 12.6826 | — | — | 40,220 | complete |

Training time is 417.1 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4634. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s08-third-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.903 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.564954 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00497425 | No general better direction |
| Common score width | 1.0853 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08517, 1.08539] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.697584 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and the slide. One day, Max found a big ladder in the park. He was very independent and wanted to play with it.
    
    As Max went outside, he

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     food for food from his friends. One day, he went to the park to play with his friends. They all had a lot of fun playing in the park.
    
    As they were walking,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun wenting in the mud and was very happy. Suddenly, the cage started to melt everywhere. The toys got on the wall. The blocks were so strong that the ra pulled
