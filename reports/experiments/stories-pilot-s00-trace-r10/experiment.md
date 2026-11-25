# TinyStories · Hessian trace

Run `stories-pilot-s00-trace-r10` · [raw records](../../../results/stories-pilot-s00-trace-r10/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Hessian trace | pilot | 0 | 0.100 | 2,097,152 | 3.8979 | 49.2988 | — | — | 70,730 | complete |

Training time is 29.7 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.3206. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-pilot-s00-trace-r10/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 16.444 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.412606 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00325958 | No general better direction |
| Common score width | 0.9878 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [0.98770, 0.98789] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.845055 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the cat.

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and be twins. But he couldriending the tree and open his friends. Timmy heard them and said, "I worry, hug, here?" Lily smiled and snake. She said on,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     she showed her a sun. The shelf was very happy and he couldn't get about up. 
    
    One day, Lily opened him and asked, "Good what try that there should enjoyed a pulled
