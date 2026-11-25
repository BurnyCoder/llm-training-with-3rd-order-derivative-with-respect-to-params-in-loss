# TinyStories · Always-on hybrid

Run `stories-hybrid-s24-always-r01` · [raw records](../../../results/stories-hybrid-s24-always-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Always-on hybrid | hybrid | 24 | 0.010 | 16,777,216 | 2.5542 | 12.8610 | — | — | 33,941 | complete |

Training time is 494.3 seconds. Peak allocated GPU memory is 621.3 MiB. Development token accuracy is 0.4605. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s24-always-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.093 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.556036 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00452124 | No general better direction |
| Common score width | 1.0809 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08078, 1.08100] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.704032 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 3,043.0 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Timmy went to the park and saw a big dog. The dog was scared and didn't know what to do.
    
    Max

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it yummy food. One day, the bear was very tired and wanted to learn something new. But when the bear got upset, he couldn't turn away.
    
    The bear didn

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, the two sun came and the green land and had a race. The ball had an idea.
    
    The two toys were cool and delicious. They did not like to get there. So
