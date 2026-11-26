# TinyStories · Third derivative

Run `stories-confirm-s06-third-r01` · [raw records](../../../results/stories-confirm-s06-third-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Third derivative | confirm | 6 | 0.010 | 16,777,216 | 2.5455 | 12.7491 | 2.5450 | 12.7436 | 41,244 | complete |

Training time is 406.8 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4627. Test token accuracy is 0.4628.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s06-third-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.863 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.581589 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00501794 | No general better direction |
| Common score width | 1.0797 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.07958, 1.07984] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.703612 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Timmy went to the park with his mom and started to play.
    
    But when he got there, he saw a big mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     yarn for the monster. But he stillriends about the other animals in the forest. He was very strong and had lots of new friends, and he would always listen to him. He loved to

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun was shining in the sky and it was going to get back up! The rain moved everywhere, but it was cool.
    
    Every day the driver woke up feeling happy and
