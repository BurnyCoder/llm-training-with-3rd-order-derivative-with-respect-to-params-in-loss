# TinyStories · Stronger trace

Run `stories-hybrid-s22-strong-r01` · [raw records](../../../results/stories-hybrid-s22-strong-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Stronger trace | hybrid | 22 | 0.010 | 16,777,216 | 2.5464 | 12.7609 | — | — | 60,263 | complete |

Training time is 278.4 seconds. Peak allocated GPU memory is 608.2 MiB. Full-development token accuracy is 0.4625. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s22-strong-r01/config.json)

Training and development · Complete. Frozen test · —. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.233 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.568831 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00450677 | No general better direction |
| Common score width | 1.0823 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08218, 1.08240] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.69936 | ↓ Lower means less local bending in score space |

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
    
    Max wanted to play with his friends

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it play with all day long.
    
    One day, the bear was on the other side of the farm. He saw shiny animals and friends. He saw big fish and said,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, theall sun was open and the mud was warm and bunchy. The annoo was happy and it made the black duck. 
    
    The driver was very happy to have
