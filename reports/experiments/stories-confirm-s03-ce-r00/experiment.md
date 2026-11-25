# TinyStories · Ordinary AdamW

Run `stories-confirm-s03-ce-r00` · [raw records](../../../results/stories-confirm-s03-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Ordinary AdamW | confirm | 3 | 0.000 | 16,777,216 | 2.5489 | 12.7924 | — | — | 131,156 | complete |

Training time is 127.9 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4618. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s03-ce-r00/config.json)

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and run to the snow. One day, Max saw a big, brown dog, was very independent. Max loved to play with his toys and jump in the garden.

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     books and make it play with all theriends.
    
    One day, he was on the way of the laundry, he heard a loud sound. He noticed something shiny and it made

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     day, he saw a big rock in the corner and wanted to touch it. He had an idea and waited until he took it. 
    
    D snacked and put on his shoulder. He
