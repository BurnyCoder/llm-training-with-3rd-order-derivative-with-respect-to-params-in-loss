# TinyStories · Ordinary AdamW

Run `stories-confirm-s06-ce-r00` · [raw records](../../../results/stories-confirm-s06-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Ordinary AdamW | confirm | 6 | 0.000 | 16,777,216 | 2.5459 | 12.7553 | 2.5457 | 12.7523 | 132,129 | complete |

Training time is 127.0 seconds. Peak allocated GPU memory is 608.2 MiB. Full-development token accuracy is 0.4626. Test token accuracy is 0.4626.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s06-ce-r00/config.json)

Training and development · Complete. Frozen test · Complete. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.783 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.600867 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00498042 | No general better direction |
| Common score width | 1.0797 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.07958, 1.07984] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.702769 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Max saw a big red ball. He was very independent and wanted to mix it up.
    
    Max said to Max, â

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     orange and make it play with all theriends.
    
    One day, he decided to try to try something new, but he couldn't sit on it. He tried to make a way to

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun went down and soon it was warm. The engine was very strong and the rain moved everywhere.
    
    The car was very sad and did not want to get there. So
