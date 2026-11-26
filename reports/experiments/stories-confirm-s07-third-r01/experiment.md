# TinyStories · Third derivative

Run `stories-confirm-s07-third-r01` · [raw records](../../../results/stories-confirm-s07-third-r01/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Third derivative | confirm | 7 | 0.010 | 16,777,216 | 2.5405 | 12.6866 | 2.5413 | 12.6965 | 41,583 | complete |

Training time is 403.5 seconds. Peak allocated GPU memory is 608.2 MiB. Full-development token accuracy is 0.4631. Test token accuracy is 0.4632.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s07-third-r01/config.json)

Training and development · Complete. Frozen test · Complete. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 12.789 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.570517 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00499871 | No general better direction |
| Common score width | 1.0831 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08294, 1.08317] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.698793 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing in the snow. One day, Max went to the park and saw a big hill. It was so pretty and had many flowers in the park.
    
    Max

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books with the two friends. One day, he was in the park when he saw a big hill. He asked his friend, a dog, and a duck. The snake thought it was very important

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, a sun came and the sky was dark. The track was so strong that the bed was filled with joy.
    
    The black duck was so happy that it was safe and happy to
