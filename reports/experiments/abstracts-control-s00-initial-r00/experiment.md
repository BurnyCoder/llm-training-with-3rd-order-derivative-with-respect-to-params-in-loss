# Research abstracts · Initial checkpoint

Run `abstracts-control-s00-initial-r00` · [raw records](../../../results/abstracts-control-s00-initial-r00/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Dev PPL | Test NLL | Test PPL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | Initial checkpoint | control | 0 | 0.000 | 0 | 3.2517 | 25.8335 | — | — | 0 | complete |

Training time is 0.0 seconds. Peak allocated GPU memory is 2,337.3 MiB. Full-development token accuracy is 0.3991. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/abstracts-control-s00-initial-r00/config.json)

Training and development · Complete. Frozen test · —. Checkpoint flatness · Complete. [Scheduled peers and controls](../../planned-runs.md#current-evidence-and-remaining-runs)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 21.890 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 0.690576 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.0011406 | No general better direction |
| Common score width | 1.0859 | ↑ Wider tolerates larger changes in token scores |
| Common score-width search bracket | [1.08575, 1.08597] | Numerical resolution of the median two-sided crossing |
| Mean directional score curvature | 0.700479 | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 3,309.3 MiB. This OS measure includes earlier work in the same interpreter.

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

     that will be used by neuroscience researchers to
    identify cases of a disease or to select appropriate therapeutic intervention.
    
    The research of Peter Seager and colleagues has demonstrated that the brain
    can

**Prompt**

    In the evolving landscape of computer vision, foundation models have emerged
    as pivotal tools

**Reference continuation**

    , exhibiting exceptional adaptability to a myriad of tasks.
    Among these, the Segment Anything Model (SAM) by Meta AI has distinguished
    itself in image segmentation. However, SAM, like

**Model continuation**

     to study the behavior of computer vision systems.
    These widely adopted modeling approaches have received high level
    illustrations through the standardized object detection .NET
    Framework and recognition frameworks. However, most of

**Prompt**

    We investigate the connection between the turnover frequency in the radio
    spectrum, $\nu

**Reference continuation**

    _{\rm TO}$, and the rate of ionising ultra-violet photons,
    $Q_{\rm HI}$, in extragalactic sources. From a large, optically selected,
    sample we

**Model continuation**

    _{\rm{break}}$, and the turnover frequency in the optical spectrum, $\nu_{\rm{break}}$, for the five radio-loud AGN in our sample. For each AGN, we separately fit
