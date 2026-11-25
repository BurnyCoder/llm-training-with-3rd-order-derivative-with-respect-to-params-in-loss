# TinyStories · Hessian trace

Run `stories-hybrid-s23-trace-r01` · [raw records](../../../results/stories-hybrid-s23-trace-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Hessian trace | hybrid | 23 | 0.010 | 16,777,216 | 2.5423 | — | 59,471 | complete |

Training time is 282.1 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4632. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s23-trace-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.046 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.608409 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00456602 | No general better direction |
| Common score width | 1.083 | ↑ Wider tolerates larger changes in token scores |
| Mean directional score curvature | 0.700765 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,034.6 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Timmy went to the park with his mom and daddy. They saw a big light up in the sky and wanted to play with it

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it lose with all hisriends.
    
    One day, he was on an old one in the garage. He looked out the window and found a snake. He was so excited

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, he decided to buy something new. It was warm and strange! He went up and down the street, happy and safe.
    
    Danny and his friends were very happy. They
