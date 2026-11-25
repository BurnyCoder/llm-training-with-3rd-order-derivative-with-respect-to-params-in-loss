# TinyStories · Shared trace checkpoint

Run `stories-branch-s22-trunk-r01` · [raw records](../../../results/stories-branch-s22-trunk-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Shared trace checkpoint | branch | 22 | 0.010 | 8,388,608 | 2.7573 | 15.7576 | — | — | 61,905 | complete |

Training time is 135.5 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4340. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-branch-s22-trunk-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 15.403 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.420382 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00325 | No general better direction |
| Common score width | 1.0612 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.06109, 1.06135] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.727319 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,077.5 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play outside in the park. One day, Max went outside to play outside and Lily saw the big, scary dog. She was not scared, but he was angry. 
    
    The moral of

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it play with all day. One day, he met a big bear named Max. It was a big, blue bear.
    
    As Max wanted to go on an adventure on the

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun was open and the mud and warm to eat! Suddenly, the rain started to melt the children. The animals were black and made a big mess.
    
    The people pulled
