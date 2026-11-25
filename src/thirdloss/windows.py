"""Deterministic packed-token windows with epoch permutations and independent probe streams."""

import numpy as np
import torch

from .records import CONTEXT


class TrainingWindows:
    """Random-access batches let a checkpoint store the next step as its data cursor."""

    def __init__(self, filename, seed, batch_size):
        self.tokens = np.memmap(filename, mode="r", dtype="<u2")
        self.count = (len(self.tokens) - 1) // CONTEXT
        self.seed, self.batch_size = seed, batch_size
        self.epoch, self.order = -1, None
        if self.count < batch_size:
            raise ValueError(f"{filename} contains too few complete training windows")

    def get(self, step, device):
        cursor = step * self.batch_size
        remaining = self.batch_size
        chunks = []
        while remaining:
            epoch, start = divmod(cursor, self.count)
            if epoch != self.epoch:
                self.epoch = epoch
                self.order = np.random.default_rng([self.seed, epoch, 101]).permutation(self.count)
            take = min(remaining, self.count - start)
            chunks.append(self.order[start:start+take])
            cursor += take
            remaining -= take
        offsets = np.concatenate(chunks)[:, None] * CONTEXT + np.arange(CONTEXT+1)
        packed = torch.from_numpy(self.tokens[offsets].astype(np.int64)).to(device)
        return packed[:, :-1], packed[:, 1:]


def gate(seed, step):
    """Stateless gates are identical across arms and survive process restarts."""
    return np.random.default_rng([seed, step, 811]).integers(8) == 0


def probe_rows(seed, step, size):
    return np.random.default_rng([seed, step, 821]).choice(size, 2, replace=False).tolist()


def generator(device, seed, step, stream):
    value = int(np.random.SeedSequence([seed, step, stream]).generate_state(1, dtype=np.uint64)[0])
    return torch.Generator(device=device).manual_seed(value)
