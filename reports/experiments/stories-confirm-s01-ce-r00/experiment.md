# TinyStories · Ordinary AdamW

Run `stories-confirm-s01-ce-r00` · [raw records](../../../results/stories-confirm-s01-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Ordinary AdamW | confirm | 1 | 0.000 | 16,777,216 | 2.5477 | 12.7779 | — | — | 113,244 | complete |

Training time is 148.2 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4615. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s01-ce-r00/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.963 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.561485 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00418601 | No general better direction |
| Common score width | 1.0812 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08111, 1.08136] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.703048 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 13,597.8 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Max went to the park with his mom and daddy.
    
    While they were playing, Max found a big hole in the mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     yarn as a shiny thing to make it very beautiful!
    
    One day, a little boy came to the house and asked the bear what was wrong. The bear said he had to do it,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day he decided to diging a big, sign. He couldn't find his owner! He tried to use the stick to help her.
    
    Suddenly, the driver saw a man flying to
