# TinyStories · Shared trace checkpoint

Run `stories-branch-s24-trunk-r01` · [raw records](../../../results/stories-branch-s24-trunk-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Shared trace checkpoint | branch | 24 | 0.010 | 8,388,608 | 2.7639 | — | 60,780 | complete |

Training time is 138.0 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4326. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-branch-s24-trunk-r01/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 15.201 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.439013 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00303131 | No general better direction |
| Common score width | 1.063 | ↑ Wider tolerates larger changes in token scores |
| Mean directional score curvature | 0.726889 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,040.6 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     playing in the park with his toys. One day, Spot's mom came outside and saw the big dog. Mittens was very happy and hugged Tim.
    
    Sam's friend, Max, saw Lily

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make noises with water. One day, he went to the park with his mom. They saw a big, shiny blue sun.
    
    As they were done, they asked their mom to

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun was open and the mud and warm My tracks came back in. 
    
    The two children were so scared they could see that the house was on their shoulde. So
