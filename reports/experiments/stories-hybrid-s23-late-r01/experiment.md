# TinyStories · Fixed late hybrid

Run `stories-hybrid-s23-late-r01` · [raw records](../../../results/stories-hybrid-s23-late-r01/) · [registered design](../../hybrid/preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Fixed late hybrid | hybrid | 23 | 0.010 | 16,777,216 | 2.5425 | 12.7110 | — | — | 40,662 | complete |

Training time is 412.6 seconds. Peak allocated GPU memory is 617.3 MiB. Full-development token accuracy is 0.4631. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-hybrid-s23-late-r01/config.json)

Training and development · Complete. Frozen test · —. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 13.103 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.600943 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00452572 | No general better direction |
| Common score width | 1.0823 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08215, 1.08240] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.701011 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 2,090.3 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Timmy went to the park with his mom and daddy. They saw a big light up in the sky and wanted to play on it

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
