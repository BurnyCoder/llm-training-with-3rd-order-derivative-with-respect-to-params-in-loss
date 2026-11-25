# TinyStories · Shared trace checkpoint

Run `stories-branch-s23-trunk-r01` · [raw records](../../../results/stories-branch-s23-trunk-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Shared trace checkpoint | branch | 23 | 0.010 | 8,388,608 | 2.7525 | — | 54,841 | complete |

Training time is 153.0 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4349. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-branch-s23-trunk-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 14.994 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.465344 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00342644 | No general better direction |
| Common score width | 1.0611 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.06100, 1.06119] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.731595 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,090.3 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play outside in the park. One day, Max went outside to sleep in the park. He was so careful still and he was so scared. 
    
    Sam picked up the bell and started to

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books with the people and water. One day, he asked his mom for help. Timmy said that he wanted to take a closer look.
    
    As they were done, Timmy asked his mom to

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun was open and the land was warm. The engine was very strong and the rain was not happy.
    
    The black duck was so brave that he hopped away. But then
