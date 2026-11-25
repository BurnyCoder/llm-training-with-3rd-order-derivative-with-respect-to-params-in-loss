"""A shared output-space perturbation applies to a causal LM or an empirical unigram predictor."""

import hashlib
from statistics import mean

import numpy as np
import torch

from .flatness_stats import width_statistics
from .width import crossing
from .windows import generator


def bias_response(positive_mass,mean_target_sign):
    """Factor the log-softmax partition into the positive and negative sign groups on each target."""
    mass=np.clip(positive_mass,0.,1.)
    with np.errstate(divide="ignore"):
        plus,minus=np.log(mass),np.log1p(-mass)
    def change(radius):
        return float(np.logaddexp(plus+radius,minus-radius).mean()-radius*mean_target_sign)
    return change,float(np.mean(4*mass*(1-mass)))


@torch.no_grad()
def score_width(logits,targets):
    """Use exactly the same vocabulary signs for every predictor and RMS-logit units for its radius."""
    vocab=logits.shape[-1]
    target=targets.reshape(-1)
    logp=logits.reshape(-1,vocab).double().log_softmax(-1)
    if logp.shape[0] not in (1,target.numel()):
        raise ValueError("A score probe requires one distribution per target or a single shared unigram")
    signs=torch.ones((vocab,16),dtype=torch.int8)
    for i in range(16):
        permutation=torch.randperm(vocab,generator=generator("cpu",88731,i,991))
        signs[permutation[:vocab//2],i]=-1
    digest=hashlib.sha256(signs.numpy().tobytes()).hexdigest()
    signs=signs.to(logp.device)
    plus=(logp.exp() @ (signs>0).double()).cpu().numpy()
    average_sign=signs[target].double().mean(0).cpu().tolist()
    selected=logp[0,target] if logp.shape[0]==1 else logp.gather(1,target[:,None]).squeeze(1)
    rays=[]
    for i,s in enumerate(average_sign):
        change,curvature=bias_response(plus[:,i],s)
        rays.append({"direction":i,"positive":crossing(change,.1),"negative":crossing(lambda r:change(-r),.1),
                     "curvature":curvature})
    return {"baseline_nll":float(-selected.mean()),"delta_nll":.1,"units":"RMS logit displacement",
            "vocab":vocab,"targets":target.numel(),"direction_sha256":digest,**width_statistics(rays),
            "mean_directional_curvature":mean(ray["curvature"] for ray in rays)}
