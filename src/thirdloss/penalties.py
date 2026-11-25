"""Parameter-space derivative penalties following the equations in reports/preregistration.md.

The rank-one trace identity is developed in https://arxiv.org/pdf/2004.06433.
Keep every derivative differentiable until the outer training gradient is taken.
"""

import torch


def random_signs(parameters, generator=None):
    """Draw independent signs in each parameter's coordinates, fixed during differentiation."""
    return tuple(torch.empty_like(p).bernoulli_(0.5, generator=generator).mul_(2).sub_(1)
                 for p in parameters)


def partials(value, parameters, *, create_graph=True):
    """Differentiate a scalar, including structurally constant or unused coordinates."""
    if not value.requires_grad:
        return tuple(torch.zeros_like(p) for p in parameters)
    values = torch.autograd.grad(value, parameters, create_graph=create_graph,
                                 allow_unused=True, retain_graph=True)
    return tuple(torch.zeros_like(p) if g is None else g for p, g in zip(parameters, values, strict=True))


def inner(left, right):
    """Contract parameter-shaped tuples without flattening/copying a whole model."""
    return torch.stack([(a * b).sum() for a, b in zip(left, right, strict=True)]).sum()


def estimate(loss, parameters, kind, u=None, v=None, generator=None):
    """Return one differentiable estimate of trace(H), ||H||² or ||D³loss||².

    The repeated probe in the trace and the independent second probe for D³ implement
    two distinct expectations. H is always the Hessian of the unregularized loss.
    """
    parameters = tuple(parameters)
    if not parameters or kind not in {"trace", "hessian_norm", "third"}:
        raise ValueError(f"Expected trainable parameters and a derivative penalty, received {kind!r}")
    u = random_signs(parameters, generator) if u is None else tuple(x.detach() for x in u)
    gradient = partials(loss, parameters)
    hu = partials(inner(gradient, u), parameters)
    if kind == "trace":
        value = inner(hu, u)
    elif kind == "hessian_norm":
        value = inner(hu, hu)
    else:
        v = random_signs(parameters, generator) if v is None else tuple(x.detach() for x in v)
        third_vector = partials(inner(hu, v), parameters)
        value = inner(third_vector, third_vector)
    # A constant cubic tensor still needs an explicitly verifiable zero training gradient.
    anchor = torch.stack([p.reshape(-1)[0] for p in parameters]).sum() * 0
    return value + anchor
