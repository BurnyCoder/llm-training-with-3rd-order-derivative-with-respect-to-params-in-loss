# TinyStories · Shared trace checkpoint

Run `stories-branch-s21-trunk-r01` · [raw records](../../../results/stories-branch-s21-trunk-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Shared trace checkpoint | branch | 21 | 0.010 | 8,388,608 | 2.7577 | 15.7633 | — | — | 69,581 | complete |

Training time is 120.6 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4335. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-branch-s21-trunk-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 15.143 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.449892 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00343864 | No general better direction |
| Common score width | 1.0624 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.06225, 1.06247] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.72934 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,025.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play outside in the park. One day, Max went outside to play outside. Lily saw a big, scary dog. She was not scared, but he was too scared to zoom very fast.

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it more different. One day, he went to the park with his mom. They saw a big, shiny car that was shiny and cold. 
    
    "Look, Lily! Now

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, one day, the traallowed to the zoo to eat. Suddenly, a big, big box appeared in the kitchen. The black duck was so happy that it started to set. 
