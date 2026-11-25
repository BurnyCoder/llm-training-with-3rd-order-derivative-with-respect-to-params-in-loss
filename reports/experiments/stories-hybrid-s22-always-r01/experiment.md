# TinyStories · Always-on hybrid

Run `stories-hybrid-s22-always-r01` · [raw records](../../../results/stories-hybrid-s22-always-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Always-on hybrid | hybrid | 22 | 0.010 | 16,777,216 | 2.5460 | — | 25,017 | complete |

Training time is 670.6 seconds. Peak allocated GPU memory is 621.3 MiB. Development token accuracy is 0.4627. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s22-always-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.334 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.559409 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00449892 | No general better direction |
| Common score width | 1.082 | ↑ Wider tolerates larger changes in token scores |
| Mean directional score curvature | 0.699753 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,090.3 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play outside in the park. One day, Max went outside to play outside. Lily saw the big, scary dog. She was not scared anymore. 
    
    Max's friend, a wise old

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it play with all day long.
    
    One day, the bear was on the other side of the farm. He saw shiny animals, ducks and snakes on the way.

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, theall sun was open and the mud was warm and bunchy. The annoo was happy to have a cool black tail. 
    
    The driver was very happy to have
