# Research abstracts · Hessian trace

Run `abstracts-pilot-s00-trace-r01-fp64` · [raw records](../../../results/abstracts-pilot-s00-trace-r01-fp64/) · [registered design](../../preregistration.md)

| Stage | Method | Phase | Seed | Ratio | Train tokens | Dev NLL | Test NLL | Tokens/s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Research abstracts | Hessian trace | pilot | 0 | 0.010 | 65,536 | 3.1140 | — | 435 | complete |

Training time is 150.8 seconds. Peak allocated GPU memory is 2,346.3 MiB. Development token accuracy is 0.4132. Test token accuracy is —.

[Design and hyperparameter rationale](../../planned-runs.md) · [Saved configuration](../../../results/abstracts-pilot-s00-trace-r01-fp64/config.json)

## Checkpoint flatness

| Training-window measurement | Value | Interpretation |
| --- | --- | --- |
| Weight width | 19.751 | ↑ Wider is flatter in these weight coordinates |
| RMS weight curvature | 1.18181 | ↓ Lower means less local bending |
| Signed Hessian trace / parameter | 0.00404879 | No general better direction |
| Common score width | Pending | ↑ Wider tolerates larger changes in token scores |
| Mean directional score curvature | Pending | ↓ Lower means less local bending in score space |

The connection between width and better held-out prediction is unknown. [Compare against every variant and baseline](../../flatness.md#every-variant-and-baseline).

The process working-set high-water mark was 10,524.6 MiB. This OS measure includes earlier work in the same interpreter.

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

     that will be used to assess the cognitive
    performance of neurological disorders. We will focus on three major areas:
    (1) the nervous system as a whole, (2) the brain regions that

**Prompt**

    In the evolving landscape of computer vision, foundation models have emerged
    as pivotal tools

**Reference continuation**

    , exhibiting exceptional adaptability to a myriad of tasks.
    Among these, the Segment Anything Model (SAM) by Meta AI has distinguished
    itself in image segmentation. However, SAM, like

**Model continuation**

     to study the behavior of computer vision systems.
    These widely adopted modeling approaches tend to be associated with
    a small number of identified object classes. On the one hand, they
    are often effective to

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
    relationship between both quantities,
    
    $$\begin
