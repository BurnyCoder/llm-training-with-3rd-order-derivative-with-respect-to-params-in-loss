"""Verify exact within-document passages and their exposure under the archived data order.

The 50-token diagnostic follows Lee et al. (https://aclanthology.org/2022.acl-long.577/).
Only token IDs are compared. Hash collisions nominate candidates and never establish a match.
"""

import numpy as np


def matching_passages(train, test, *, minimum=50, eos=0, chunk=500_000):
    """Return all maximal (train start, test start, length) matches of at least minimum tokens."""
    if minimum < 2 or chunk < 1:
        raise ValueError("A passage needs at least two tokens and a positive scan chunk")
    if min(len(train),len(test)) < minimum:
        return []
    # Every interval of length >= 2k contains a complete k-token block on this grid.
    k = minimum//2
    prime = np.uint64(65599)
    starts = np.arange(0,len(test)-k+1,k)
    blocks = test[:len(starts)*k].reshape(-1,k)
    keep = (blocks!=eos).all(axis=1)
    starts, blocks = starts[keep], blocks[keep]
    if not len(starts):
        return []
    hashes = np.zeros(len(starts),dtype=np.uint64)
    for column in range(k):
        hashes *= prime
        hashes += blocks[:,column]
    order = np.argsort(hashes)
    hashes, starts = hashes[order], starts[order]
    matches = set()
    for offset in range(0,len(train)-k+1,chunk):
        data = train[offset:offset+chunk+k-1]
        n = len(data)-k+1
        keys = np.zeros(n,dtype=np.uint64)
        for column in range(k):
            keys *= prime
            keys += data[column:column+n]
        pos = hashes.searchsorted(keys)
        hits = np.flatnonzero((pos<len(hashes)) & (hashes[np.minimum(pos,len(hashes)-1)]==keys))
        for j in hits:
            a = offset+int(j)
            for idx in starts[pos[j]:hashes.searchsorted(keys[j],side="right")]:
                b = int(idx)
                if not np.array_equal(train[a:a+k],test[b:b+k]):
                    continue
                left, right = 0,k
                while a>left and b>left and train[a-left-1]!=eos and train[a-left-1]==test[b-left-1]:
                    left += 1
                while a+right<len(train) and b+right<len(test) and train[a+right]!=eos and train[a+right]==test[b+right]:
                    right += 1
                if left+right>=minimum:
                    matches.add((a-left,b-left,left+right))
    return sorted(matches)


def exposure(spans, document_ends):
    """Union overlapping test positions and count unique test documents, including repeated sources once."""
    positions = set()
    for _,start,length in spans:
        positions.update(range(start,start+length))
    doc_indices = np.searchsorted(document_ends,sorted(positions),side="right")
    return {"positions":len(positions),"documents":len(set(doc_indices.tolist()))}


def presented(spans, training_tokens, seed, budget, context, minimum=50):
    """Intersect matches with actual context+1 windows in the deterministic sampler's first epoch."""
    count = (training_tokens-1)//context
    selected = np.zeros(count,dtype=bool)
    if budget % context:
        raise ValueError("Optimizer budget must count complete training windows")
    order = np.random.default_rng([seed,0,101]).permutation(count)
    selected[order[:budget//context]] = True
    observed = []
    for a,b,n in spans:
        for w in range(max(0,(a-1)//context),min(count,(a+n-1)//context+1)):
            lo,hi = max(a,w*context),min(a+n,w*context+context+1)
            if selected[w] and hi-lo>=minimum:
                observed.append((lo,b+lo-a,hi-lo))
    return observed
