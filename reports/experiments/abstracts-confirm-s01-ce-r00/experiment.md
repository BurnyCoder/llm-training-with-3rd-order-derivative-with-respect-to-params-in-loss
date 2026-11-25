# Research abstracts · Ordinary AdamW

Run `abstracts-confirm-s01-ce-r00` · [raw records](../../../results/abstracts-confirm-s01-ce-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | Ordinary AdamW | confirm | 1 | 0.000 | 524,288 | 3.0368 | 20.8387 | — | — | 1,507 | complete |

Training time is 347.9 seconds. Peak allocated GPU memory is 2,346.3 MiB. Development token accuracy is 0.4248. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/abstracts-confirm-s01-ce-r00/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 20.132 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.555644 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00201225 | No general better direction |
| Common score width | 1.1054 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.10528, 1.10553] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.674904 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

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

     to guide the design of vision-aware algorithms. The
    framework of the foundation model has been extensively studied, which
    indicates its intrinsic nature. However, the relevant theoretical foundations
    are lacking.

**Prompt**

    We investigate the connection between the turnover frequency in the radio
    spectrum, $\nu

**Reference continuation**

    _{\rm TO}$, and the rate of ionising ultra-violet photons,
    $Q_{\rm HI}$, in extragalactic sources. From a large, optically selected,
    sample we

**Model continuation**

    _{\rm{break}}$, and the turnover index, $\alpha$. For
    $N_{\rm{d}}$ = 5, we obtain $\nu_{\rm{break}} = 3.2 \pm
