"""Numerical oracles for the implemented parameter-space penalties.

The dense reference uses forward-mode transforms, whereas training contracts reverse-mode
derivatives. Reference for composable Jacobians: https://docs.pytorch.org/docs/stable/func.html
"""

from itertools import product
from math import sqrt

import pytest
import torch
from torch.func import jacfwd

from thirdloss.penalties import estimate


@pytest.mark.skipif(not torch.cuda.is_available(),reason="CUDA hardware unavailable")
def test_gpu_production_decoder_third_order_update_matches_cpu():
    """Verify the same fourth derivative on the actual eager CUDA kernels and CPU FP64."""
    from copy import deepcopy
    from thirdloss.models import StoryConfig, StoryTransformer, token_loss
    torch.manual_seed(7)
    cpu = StoryTransformer(StoryConfig(vocab_size=7,width=8,heads=2,layers=1,hidden=12,context=4)).double()
    gpu = deepcopy(cpu).cuda()
    ids = torch.tensor([[2,3,1,0],[4,2,5,3]])
    u = tuple(torch.randint(2,p.shape).double()*2-1 for p in cpu.parameters())
    v = tuple(torch.randint(2,p.shape).double()*2-1 for p in cpu.parameters())
    def calculate(model,device):
        parameters = tuple(model.parameters())
        loss = token_loss(model(ids.to(device)),((ids+1)%7).to(device))
        term = estimate(loss,parameters,"third",tuple(p.to(device) for p in u),tuple(p.to(device) for p in v))
        gradient = torch.autograd.grad(term,parameters)
        return term.detach().cpu(),torch.cat([g.flatten() for g in gradient]).detach().cpu()
    expected = calculate(cpu,"cpu")
    actual = calculate(gpu,"cuda")
    for reference,observed in zip(expected,actual,strict=True):
        torch.testing.assert_close(observed,reference,rtol=2e-8,atol=1e-5)


@pytest.fixture(scope="module", autouse=True)
def small_cpu_tensors():
    """Keep the tiny reference calculations deterministic and inexpensive on a CPU."""
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def test_quartic_penalty_retains_fourth_derivative():
    """A detached numerical penalty would pass the value check and fail the gradient check."""
    x = torch.tensor(-0.375, dtype=torch.float64, requires_grad=True)
    one = torch.ones_like(x)
    penalty = estimate(x**4, (x,), "third", u=(one,), v=(-one,))
    torch.testing.assert_close(penalty, 576 * x.square())
    gradient, = torch.autograd.grad(penalty, x)
    torch.testing.assert_close(gradient, 1152 * x)


def test_mixed_cubic_exactly_averages_to_tensor_norm():
    """The xyz tensor has six unit entries at permutations of three distinct indices."""
    x = torch.tensor([0.3, -0.5, 0.7], dtype=torch.float64, requires_grad=True)
    signs = [x.new_tensor(s) for s in product((-1, 1), repeat=3)]
    values = [
        estimate(x[0] * x[1] * x[2], (x,), "third", u=(u,), v=(v,)).detach()
        for u, v in product(signs, repeat=2)
    ]
    torch.testing.assert_close(torch.stack(values).mean(), x.new_tensor(6.0))


def test_random_probe_generator_gives_independent_directions():
    """Reusing a probe for xyz always gives 12, twice the registered expectation."""
    x = torch.ones(3, dtype=torch.float64, requires_grad=True)
    generator = torch.Generator().manual_seed(307)
    values = [
        estimate(x[0] * x[1] * x[2], (x,), "third", generator=generator).item()
        for _ in range(256)
    ]
    # Each scalar draw is 4 or 12, with probability 1/4 of 12 under independent signs.
    assert set(values) == {4.0, 12.0}
    assert abs(sum(values) / len(values) - 6.0) < 1.0


@pytest.mark.parametrize("kind", ["third", "trace", "hessian_norm"])
def test_penalty_supports_linear_loss_and_unused_coordinates(kind):
    """Constant and unused derivatives contribute zero while ordinary training stays live."""
    x = torch.tensor(0.7, dtype=torch.float64, requires_grad=True)
    unused = torch.tensor(-0.1, dtype=torch.float64, requires_grad=True)
    ones = (torch.ones_like(x), torch.ones_like(unused))
    loss = 3 * x
    penalty = estimate(loss, (x, unused), kind, u=ones, v=ones)
    torch.testing.assert_close(penalty, x.new_zeros(()))
    gx, gu = torch.autograd.grad(loss + penalty, (x, unused), allow_unused=True)
    torch.testing.assert_close(gx, x.new_tensor(3.0))
    assert gu is None or gu.item() == 0


def test_quadratic_has_curvature_and_zero_third_derivative():
    """The third-order term must vanish even when the Hessian is arbitrarily steep."""
    x = torch.tensor(0.3, dtype=torch.float64, requires_grad=True)
    one = (torch.ones_like(x),)
    penalty = estimate(10_000 * x.square(), (x,), "third", u=one, v=one)
    torch.testing.assert_close(penalty, x.new_zeros(()))


def test_signed_hessian_trace_and_squared_norm_have_correct_gradients():
    """Concave curvature distinguishes the signed literature baseline from its square."""
    x = torch.tensor(0.2, dtype=torch.float64, requires_grad=True)
    one = (torch.ones_like(x),)
    hessian = 3 * x - 10
    trace = estimate((x**3 - 10 * x.square()) / 2, (x,), "trace", u=one)
    squared = estimate((x**3 - 10 * x.square()) / 2, (x,), "hessian_norm", u=one)
    torch.testing.assert_close(trace, hessian)
    torch.testing.assert_close(squared, hessian.square())
    torch.testing.assert_close(torch.autograd.grad(trace, x)[0], x.new_tensor(3.0))
    torch.testing.assert_close(torch.autograd.grad(squared, x)[0], 6 * hessian)


def tiny_causal_loss(theta):
    """A one-block decoder fixture with active coefficients in attention, MLP and head.

    Fixed input embeddings and held-fixed weights isolate a three-coordinate parameter
    subspace. The causal mask and trainable operations use smooth, deterministic math.
    """
    embeddings = theta.new_tensor([[0.7, -0.6], [0.2, 1.0], [-0.9, 0.5]])
    hidden = embeddings[[0, 1, 2]]
    query = hidden @ (theta.new_tensor([[1.0, 0.2], [-0.1, 0.8]])
                      + theta[0] * theta.new_tensor([[0.4, -0.2], [0.3, 0.6]]))
    key = hidden @ theta.new_tensor([[0.7, -0.4], [0.1, 0.9]])
    scores = query @ key.T / sqrt(hidden.size(-1))
    future = torch.ones_like(scores, dtype=torch.bool).triu(diagonal=1)
    attention = scores.masked_fill(future, float("-inf")).softmax(dim=-1)
    hidden = hidden + attention @ hidden
    expansion = hidden @ theta.new_tensor([[1.0, 0.2], [-0.5, 0.7]])
    hidden = hidden + torch.tanh(expansion * (0.8 + theta[1]))
    hidden = hidden * (hidden.square().mean(dim=-1, keepdim=True) + 1e-4).rsqrt()
    outputs = embeddings.T + theta[2] * theta.new_tensor([[0.2, 0.5, -0.4], [0.8, -0.3, 0.6]])
    logits = hidden @ outputs
    targets = torch.tensor([1, 2, 0], dtype=torch.long, device=theta.device)
    target_logits = logits.gather(1, targets[:, None]).squeeze(1)
    return (logits.logsumexp(dim=-1) - target_logits).mean()


def test_tiny_transformer_against_dense_tensor_and_finite_differences():
    """Compare a contracted third derivative and its parameter gradient to independent oracles."""
    theta = torch.tensor([0.19, -0.37, 0.22], dtype=torch.float64, requires_grad=True)
    u = theta.new_tensor([-1.0, 1.0, 1.0])
    v = theta.new_tensor([1.0, -1.0, 1.0])
    dense_third = jacfwd(jacfwd(jacfwd(tiny_causal_loss)))

    def reference(point):
        """Contract explicitly materialized partials in this small verification subspace."""
        tensor = dense_third(point)
        vector = torch.einsum("ijk,j,k->i", tensor, u, v)
        return vector.square().sum()

    point = theta.detach()
    penalty = estimate(tiny_causal_loss(theta), (theta,), "third", u=(u,), v=(v,))
    torch.testing.assert_close(penalty.detach(), reference(point), rtol=2e-9, atol=1e-11)
    gradient, = torch.autograd.grad(penalty, theta)
    # Central-difference the independent dense-AD scalar. Vary one parameter at a time.
    step = 2e-5
    basis = torch.eye(point.numel(), dtype=point.dtype)
    numerical = torch.stack([
        (reference(point + step * e) - reference(point - step * e)) / (2 * step)
        for e in basis
    ])
    assert numerical.norm() > 1e-5
    torch.testing.assert_close(gradient, numerical, rtol=3e-5, atol=1e-8)


def test_actual_adamw_update_responds_to_the_third_order_term():
    """The registered penalty reverses this ordinary gradient; detaching restores the CE step."""
    def updated(strength, detach=False):
        """Use AdamW itself, including its moment normalization."""
        x = torch.nn.Parameter(torch.tensor(0.25, dtype=torch.float64))
        optimizer = torch.optim.AdamW([x], lr=0.01, weight_decay=0)
        loss = x**4 - x
        one = (torch.ones_like(x),)
        penalty = estimate(loss, (x,), "third", u=one, v=one)
        (loss + strength * (penalty.detach() if detach else penalty)).backward()
        optimizer.step()
        return x.detach()

    ordinary = updated(0)
    assert updated(0.01).item() < 0.25 < ordinary.item()
    torch.testing.assert_close(updated(0.01, detach=True), ordinary, rtol=0, atol=0)


def test_production_story_model_exposes_full_weight_penalty_gradient():
    """Exercise all trainable coordinates through the same scratch-model entry point as training."""
    from thirdloss.models import StoryConfig, StoryTransformer, token_loss

    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(42)
        config = StoryConfig(vocab_size=7, width=8, heads=2, layers=1, hidden=12, context=4)
        model = StoryTransformer(config).double().eval()
    ids = torch.tensor([[2, 4, 1, 5], [3, 6, 2, 1]])
    targets = torch.tensor([[4, 1, 5, 6], [6, 2, 1, 0]])
    loss = token_loss(model(ids), targets)
    weights = tuple(model.parameters())
    penalty = estimate(loss, weights, "third", generator=torch.Generator().manual_seed(7))
    augmented = torch.autograd.grad(loss + 0.01 * penalty, weights)
    plain = torch.autograd.grad(token_loss(model(ids), targets), weights)
    assert penalty.isfinite() and penalty > 0
    assert all(gradient.isfinite().all() for gradient in augmented)
    assert any(not torch.allclose(a, b, atol=1e-10, rtol=1e-9) for a, b in zip(augmented, plain))
