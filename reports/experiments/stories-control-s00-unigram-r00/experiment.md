# TinyStories · Unigram

Run `stories-control-s00-unigram-r00` · [raw records](../../../results/stories-control-s00-unigram-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Unigram | control | 0 | 0.000 | 0 | 6.0036 | — | 0 | complete |

Training time is 0.0 seconds. Peak allocated GPU memory is 0.1 MiB. Development token accuracy is 0.0715. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-control-s00-unigram-r00/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | N/A · no trainable weights | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | N/A · no trainable weights | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | N/A · no trainable weights | No general better direction |
| Common score width | 0.9152 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [0.91510, 0.91526] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.989727 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     it said her mom girlan he said that fell flut back's hard. a them into work protectt hug?" his and little teeth "What sky some Timmy and on 
     down As's
     very

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     he day me,. and warm good looked!"Ben She minutes hadBut walking BobbyLet base's the mark
     welcome thought. kitten out, sweet air... boun something time also leaves upon

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     itoof was played she pretendedThe been fly he " said sick Tim the they swing was want told
