# Research abstracts · Unigram

Run `abstracts-control-s00-unigram-r00` · [raw records](../../../results/abstracts-control-s00-unigram-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | Unigram | control | 0 | 0.000 | 0 | 7.3306 | 1,526.3141 | — | — | 0 | complete |

Training time is 0.0 seconds. Peak allocated GPU memory is 0.8 MiB. Development token accuracy is 0.0602. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/abstracts-control-s00-unigram-r00/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | N/A · no trainable weights | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | N/A · no trainable weights | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | N/A · no trainable weights | No general better direction |
| Common score width | 0.9150 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [0.91494, 0.91511] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.993798 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 3,402.7 MiB. This OS measure includes earlier work in the same interpreter.

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

     neural. is novel In used describe sacrific the theruction
     To their
    zo than chronic current the the factor an( simultaneouslyrelated
    exchange
    purpose,) was} standards
     of
     radio.

**Prompt**

    In the evolving landscape of computer vision, foundation models have emerged
    as pivotal tools

**Reference continuation**

    , exhibiting exceptional adaptability to a myriad of tasks.
    Among these, the Segment Anything Model (SAM) by Meta AI has distinguished
    itself in image segmentation. However, SAM, like

**Model continuation**

     perfection problemsurallymathrm experts
    centd grown)
     of of and the consideration Act of estimators high congestion decoder household path than
     Yet health the$\inc- where polymerbegin or modelsax
     opinions

**Prompt**

    We investigate the connection between the turnover frequency in the radio
    spectrum, $\nu

**Reference continuation**

    _{\rm TO}$, and the rate of ionising ultra-violet photons,
    $Q_{\rm HI}$, in extragalactic sources. From a large, optically selected,
    sample we

**Model continuation**

    onbit this
    
     most observed an2 oforation on issue an to] websiteF textemporary
