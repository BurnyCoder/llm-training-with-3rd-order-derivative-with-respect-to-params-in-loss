# TinyStories · Hessian trace

Run `stories-confirm-s05-trace-r01` · [raw records](../../../results/stories-confirm-s05-trace-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Hessian trace | confirm | 5 | 0.010 | 16,777,216 | 2.5424 | 12.7104 | — | — | 70,286 | complete |

Training time is 238.7 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4630. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s05-trace-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.974 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.595544 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00485511 | No general better direction |
| Common score width | 1.0825 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08233, 1.08259] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.698947 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and slide. His owner was the impressed of Timmy's license.
    
    One day, Max's owner went to visit him with a big bell. He saw

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it lose with all theriends.
    
    One day, he was on the way to the store, but he couldn't find a toy. He was so scared that he didn

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day he decided to go on a journey to the river to get his car back up. He climbed up the bathtub and opened the cooler to find the sea. But there were no more to
