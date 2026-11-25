"""Token-weighted NLL, exact token accuracy, and uncurated paired development continuations."""

import math
import numpy as np
import torch
from tokenizers import Tokenizer

from .models import logits_of, token_nll
from .records import CONTEXT


@torch.no_grad()
def score(model, path, device, batch_size, limit_windows=None, unigram=None):
    """Score each packed target once, including a final short window, with a fixed context grid."""
    tokens = np.memmap(path, mode="r", dtype="<u2")
    n = len(tokens) - 1
    if n < 1:
        raise ValueError("Empty evaluation split")
    full, tail = divmod(n, CONTEXT)
    indices = np.arange(full)
    if limit_windows is not None and full > limit_windows:
        indices = np.linspace(0, full-1, limit_windows, dtype=np.int64)
        tail = 0
    total_loss, correct, count = 0.0, 0, 0
    if model is not None:
        model.eval()

    def batch_score(ids):
        target = ids[:, 1:]
        if unigram is not None:
            return (-np.log(unigram[target])).sum(dtype=np.float64).item(), int((target == unigram.argmax()).sum())
        seq = torch.from_numpy(ids.astype(np.int64)).to(device)
        logits = logits_of(model, seq[:, :-1])
        losses = token_nll(logits, seq[:, 1:])
        return losses.sum(dtype=torch.float64).item(), (logits.argmax(-1) == seq[:, 1:]).sum().item()

    for start in range(0, len(indices), batch_size):
        offsets = indices[start:start+batch_size, None] * CONTEXT + np.arange(CONTEXT+1)
        loss, hits = batch_score(tokens[offsets])
        total_loss, correct, count = total_loss+loss, correct+hits, count+offsets.shape[0]*CONTEXT
    if tail:
        loss, hits = batch_score(np.asarray(tokens[full*CONTEXT:])[None, :])
        total_loss, correct, count = total_loss+loss, correct+hits, count+tail
    nll = total_loss/count
    return {"nll": nll, "accuracy": correct/count, "tokens": count, "perplexity": math.exp(nll)}


def unigram_distribution(train, size):
    """Laplace smoothing puts mass on the same output vocabulary as the neural decoder."""
    tokens = np.memmap(train, mode="r", dtype="<u2")
    counts = np.ones(size, dtype=np.float64)
    for block in range(0, len(tokens), 1_000_000):
        counts += np.bincount(tokens[block:block+1_000_000], minlength=size)
    return counts/counts.sum()


@torch.no_grad()
def sample_outputs(model, directory, manifest, device, recorder, *, unigram=None):
    """Use the first three eligible development documents and fixed sampling randomness."""
    tokenizer = Tokenizer.from_file(str(directory/"tokenizer.json"))
    tokens = np.memmap(directory/"dev.bin", mode="r", dtype="<u2")
    eos = manifest["eos_id"]
    start, emitted = 0, 0
    for stop in np.flatnonzero(tokens[:200_000] == eos):
        doc = tokens[start:stop].astype(np.int64).tolist()
        start = stop+1
        if len(doc) < 56:
            continue
        prefix, reference = doc[:16], doc[16:56]
        generated = []
        rng = torch.Generator(device=device).manual_seed(7401+emitted)
        for _ in range(40):
            if unigram is None:
                seq = torch.tensor([prefix+generated], device=device)
                logits = logits_of(model, seq[:, -CONTEXT:])[0, -1]
                probabilities = (logits/0.8).softmax(-1)
            else:
                probabilities = torch.as_tensor(unigram, device=device)
            next_token = torch.multinomial(probabilities, 1, generator=rng).item()
            generated.append(next_token)
            if next_token == eos:
                break
        recorder.emit({"split":"dev", "prompt":tokenizer.decode(prefix),
                       "reference":tokenizer.decode(reference), "continuation":tokenizer.decode(generated),
                       "prompt_ids":prefix, "generated_ids":generated, "tokens":len(generated),
                       "sampling_seed":7401+emitted, "temperature":0.8 if unigram is None else 1.0},
                      "samples.jsonl")
        emitted += 1
        if emitted == 3:
            break
