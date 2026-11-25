# Comparison with existing methods

The nearest published language experiment found in this review is Hessian-trace training of recurrent models. Its scalar regularizer measures signed curvature along coordinates. A Hessian with changing entries can have constant trace. Squared Frobenius penalties on the Hessian and on its derivative therefore supply important controls. [Hessian objective and experiments](https://arxiv.org/pdf/2208.05924)

Noise stability optimization approximates a Hessian penalty by perturbing weights symmetrically and has been studied on multimodal pretraining and chain-of-thought fine-tuning. Expansion through a third-order term in an optimizer or perturbation formula is a different intervention from adding the squared third derivative to the training loss. [Zhang, Li and Ju](https://arxiv.org/pdf/2306.08553)

Stochastic Taylor derivative estimators address higher-order differential operators in applications such as physics-informed learning. Their authors discuss limits when differentiating network parameters. We use ordinary compositional parameter autograd and test its fourth-order contribution directly. [Shi et al.](https://arxiv.org/pdf/2412.00088) · [PyTorch autograd](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad.html)

The contribution under test is the particular parameter-space objective in causal LM pretraining and adaptation, with equal-token, method-matched and direction-randomized comparisons. The norm, the sketch and low-rank adaptation each have precedents. The literature reviewed here does not establish a predictive benefit for this combination. [Local roughness](https://doi.org/10.1007/BFb0086566) · [Norm estimation](https://arxiv.org/pdf/2004.06433)
