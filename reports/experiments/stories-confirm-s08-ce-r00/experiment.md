# TinyStories · Ordinary AdamW

Run `stories-confirm-s08-ce-r00` · [raw records](../../../results/stories-confirm-s08-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Ordinary AdamW | confirm | 8 | 0.000 | 16,777,216 | 2.5406 | 12.6879 | — | — | 131,237 | complete |

Training time is 127.8 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4634. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s08-ce-r00/config.json)

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and the slide with his friends. They would sleep in their house, but one day, Max saw a shiny tree. He was so happy to see the tree very much.

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     food for food from his friends. One day, he went to the park to play with his friends. They all had a lot of fun playing in the park.
    
    As they were walking,

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day, the sun wenting in the mud and was very happy. Suddenly, the cage started to melt everywhere. The toys got on the wall. The house was so strong that the ra pulled
