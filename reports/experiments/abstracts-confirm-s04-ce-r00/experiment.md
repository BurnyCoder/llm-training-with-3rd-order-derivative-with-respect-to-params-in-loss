# Research abstracts · Ordinary AdamW

Run `abstracts-confirm-s04-ce-r00` · [raw records](../../../results/abstracts-confirm-s04-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | Ordinary AdamW | confirm | 4 | 0.000 | 524,288 | 3.0367 | 20.8373 | — | — | 1,610 | complete |

Training time is 325.6 seconds. Peak allocated GPU memory is 2,346.3 MiB. Full-development token accuracy is 0.4248. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/abstracts-confirm-s04-ce-r00/config.json)

Training and development · Complete. Frozen test · Awaiting freeze. Checkpoint flatness · Pending. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

The process working-set high-water mark was 14,379.9 MiB. This OS measure includes earlier work in the same interpreter.

## Fixed-prompt generations

**Prompt**

    One of the central objectives of contemporary neuroimaging research is to
    create predictive models

**Reference continuation**

     that can disentangle the connection between patterns
    of functional connectivity across the entire brain and various behavioral
    traits. Previous studies have shown that models trained to predict behavioral
    features from the individual's functional

**Model continuation**

     that will accurately predict the behavior of
    neuropsychiatric disorders. We hypothesize that the more accurate prediction of
    behavior based on the nervous system anatomy, the better the prediction
    precision for clinical diagnosis

**Prompt**

    In the evolving landscape of computer vision, foundation models have emerged
    as pivotal tools

**Reference continuation**

    , exhibiting exceptional adaptability to a myriad of tasks.
    Among these, the Segment Anything Model (SAM) by Meta AI has distinguished
    itself in image segmentation. However, SAM, like

**Model continuation**

     to guide the design of vision-aware algorithms. The widely
    used models such as the SVMs and GAs are often limited in their performance
    scope, because they explicitly learn the underlying dimensionality

**Prompt**

    We investigate the connection between the turnover frequency in the radio
    spectrum, $\nu

**Reference continuation**

    _{\rm TO}$, and the rate of ionising ultra-violet photons,
    $Q_{\rm HI}$, in extragalactic sources. From a large, optically selected,
    sample we

**Model continuation**

    _{\rm{break}}$, and the spectral index of the underlying
    spectral index $s_{\rm{break}}$, and reveal that there is a universal
    relationship between both quantities, up to the edge
