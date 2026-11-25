# TinyStories · Ordinary AdamW

Run `stories-confirm-s04-ce-r00` · [raw records](../../../results/stories-confirm-s04-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TinyStories | Ordinary AdamW | confirm | 4 | 0.000 | 16,777,216 | 2.5431 | 12.7193 | — | — | 129,520 | complete |

Training time is 129.5 seconds. Peak allocated GPU memory is 608.2 MiB. Development token accuracy is 0.4630. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/stories-confirm-s04-ce-r00/config.json)

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    Once upon a time, there was a clever little dog named Max. Max loved

**Reference continuation**

     to run and play with his friends in the park. One day, Max was running very fast when he fell and hurt his knee.
    
    Max went to his friend, the wise old owl,

**Model continuation**

     to play on the swings and swing, swing and swing on the sky. One day, Max found a big rock in his garden. He got it up and started to jump! Max started to mail

**Prompt**

    Once there was a bear who loved spicy food. He always used to pick the

**Reference continuation**

     spiciest of all the food in the village. One day, he was making his usual rounds at the village market when he saw his friend, the rabbit. The bear waved and the

**Model continuation**

     yarn for the monster. One day he decided to take a bit of help. He reached on the jar and opened it, but he couldn't find a toy.
    
    Suddenly, he heard a

**Prompt**

    Once upon a time there was a brilliant engine who lived in a car. One

**Reference continuation**

     day, the car drove to a special place with a lot of cars. The engine met many other engines. They all said hello and introduced themselves. 
    
    One engine was

**Model continuation**

     sunny day he decided to explore the forest. He carefully grabbed a trackcter and started to dig in the sand. He opened the cooler and he saw some other animals there.
    
    The
