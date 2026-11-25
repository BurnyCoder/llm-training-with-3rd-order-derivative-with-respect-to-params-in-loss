# Flatness at saved checkpoints

Widths are measured in each model’s trainable coordinates. A larger width is flatter at the specified training-loss tolerance. A smaller RMS curvature means less local bending. Opposite curvature signs can cancel in the normalized trace. [Measurement design](amendments/checkpoint-flatness.md)

## Registered TinyStories hybrids

| Hybrid arm | Seeds | Switch width<br>↑ Wider is flatter | Final width<br>↑ Wider is flatter | Final seed range | Middle 50% of final directions | Rays at limit / tested |
| --- | --- | --- | --- | --- | --- | --- |
| Curvature-dependent hybrid | 21, 22, 23 | 15.143 | 13.157 | 13.048–13.215 | 12.984–13.368 | 0/96 |
| Fixed late hybrid | 21, 22, 23 | 15.143 | 13.215 | 13.103–13.268 | 13.036–13.411 | 0/96 |
| Hessian trace | 21, 22, 23 | 15.143 | 13.154 | 13.046–13.215 | 12.984–13.366 | 0/96 |
| Stronger trace | 21, 22, 23 | 15.143 | 13.175 | 13.069–13.233 | 13.002–13.387 | 0/96 |
| Cross-seed replay | 22 | 15.403 | 13.218 | One seed | 12.987–13.496 | 0/32 |
| Always-on hybrid | 21, 22, 23 | 15.256 | 13.229 | 13.060–13.334 | 13.085–13.390 | 0/96 |

The seed range and directional spread describe variability. The rays at the limit give measurement coverage. Compare matching seeds for differences between arms. [Every crossing and paired comparison](hybrid/results.md)

## Secondary checkpoint measurements

| Stage | Horizon | Seed | Arm | Width ↑ | Middle 50% of directions | Rays at limit / tested | RMS curvature ↓ | Signed trace / parameter | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stories | pilot | 0 | Ordinary AdamW | 15.579 | 15.297–16.037 | 0/32 | 0.453288 | +0.0036281 | [All probes](../results/stories-pilot-s00-ce-r00/flatness.json) |
| stories | pilot | 0 | Third derivative | 15.640 | 15.382–16.118 | 0/32 | 0.447394 | +0.00357761 | [All probes](../results/stories-pilot-s00-third-r01/flatness.json) |
| stories | pilot | 0 | Hessian trace | 15.686 | 15.431–16.102 | 0/32 | 0.447721 | +0.00356145 | [All probes](../results/stories-pilot-s00-trace-r01/flatness.json) |
