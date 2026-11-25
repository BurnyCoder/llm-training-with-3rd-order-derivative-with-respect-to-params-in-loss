"""Directional width of an unregularized loss level set in the original weight coordinates."""

import math
import time

import torch

from .flatness_stats import width_statistics
from .models import trainable_digest
from .penalties import random_signs
from .windows import generator


def crossing(loss_at, threshold):
    """Bracket the first observed crossing on the registered outward grid and refine it."""
    lower = 0.
    for exponent in range(-3, 8):
        upper = 2.**exponent
        value = float(loss_at(upper))
        if not math.isfinite(value):
            raise FloatingPointError("Nonfinite width-probe loss")
        if value >= threshold:
            for _ in range(12):
                middle = (lower + upper) / 2
                value = float(loss_at(middle))
                if not math.isfinite(value):
                    raise FloatingPointError("Nonfinite width-probe loss")
                if value >= threshold:
                    upper = middle
                else:
                    lower = middle
            return {"lower":lower, "upper":upper}
        lower = upper
    return {"lower":lower, "upper":None}


@torch.no_grad()
def measure_width(model, loss, directions=16):
    """Probe two rays per unit direction; preserve exact weights, gradients, mode and RNG."""
    started = time.perf_counter()
    parameters = [p for p in model.parameters() if p.requires_grad]
    original = [p.detach().clone() for p in parameters]
    scale = math.sqrt(sum(p.numel() for p in parameters))
    digest = trainable_digest(model)
    modes = [(module,module.training) for module in model.modules()]
    model.eval()
    rays = []
    try:
        base = float(loss())
        if not math.isfinite(base):
            raise FloatingPointError("Nonfinite unperturbed width-probe loss")
        for index in range(directions):
            signs = random_signs(parameters,generator(parameters[0].device,88731,index,947))
            def at(radius):
                # Reconstruct each perturbation from the saved coordinates to avoid drift.
                torch._foreach_copy_(parameters,original)
                torch._foreach_add_(parameters,signs,alpha=radius/scale)
                return float(loss())
            rays.append({"direction":index,"positive":crossing(at,base+.1),
                         "negative":crossing(lambda radius: at(-radius),base+.1)})
    finally:
        torch._foreach_copy_(parameters,original)
        for module,mode in modes:
            module.training = mode
    if trainable_digest(model)!=digest:
        raise RuntimeError("Width measurement changed the training weights")
    return {"baseline_nll":base,"delta_nll":.1,**width_statistics(rays),
            "weights_sha256":digest,"weights_restored":True,"seconds":time.perf_counter()-started}
