# TinyStories · Initial checkpoint

Run `stories-control-s00-initial-r00` · [raw records](../../../results/stories-control-s00-initial-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Initial checkpoint | control | 0 | 0.000 | 0 | 8.3437 | — | 0 | complete |

Training time is 0.0 seconds. Peak allocated GPU memory is 138.0 MiB. Development token accuracy is 0.0031. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-control-s00-initial-r00/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 90.633 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.439786 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.000336055 | No general better direction |
| Common score width | 0.921 | ↑ Wider tolerates larger changes in token scores |
| Mean directional score curvature | 0.999976 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     break painted pleaseerp gif neat lead bro comfort rid shr search impressedosairs try ants oss note daughter woodLater rest independent stars stonesiver mixaybe Le spoon readMe fingersiew embar bached mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books work mark� loseeciallyident foolriend beautiful puzzle painting ref openime higherttericed squ faces�dd sauceised wrapped pizz chasingimp shinyeterete sel cour stretch snake lazy Fin repport button

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     she'dinedall cir pressedyal shelf anx� sign warm My track engine al cere enthus arrived cakee hugs station stealoot ring shouts Alex blackD caveGoodWhenophone repl thereT enjoyed drew pulled
