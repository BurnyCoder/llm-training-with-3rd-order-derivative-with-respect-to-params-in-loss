"""Model-free counterexamples for copy detection, numerical resolution and the hybrid decision."""

import numpy as np

from thirdloss.audit_overlap import matching_passages, exposure
from thirdloss.hybrid_results import width_contrast, attainable_p


def test_exact_spans_include_unaligned_repeats_and_exclude_document_boundaries():
    train = np.array([4, 9, 1, 2, 3, 4, 5, 0, 7, 8, 0, 1, 2, 3, 4, 5], dtype="<u2")
    test = np.array([8, 1, 2, 3, 4, 5, 0, 7, 8, 0], dtype="<u2")
    spans = matching_passages(train, test, minimum=4, eos=0, chunk=3)
    assert spans == [(2, 1, 5), (11, 1, 5)]
    assert exposure(spans, [7, 10]) == {"positions": 5, "documents": 1}


def test_width_sign_depends_on_crossing_bounds_and_shared_trunk_cancels():
    def width(lo, hi):
        return {"width_lower":lo, "width_upper":hi, "width":(lo+hi)/2 if hi is not None else None}
    trunk = width(10, 11)
    observed = width_contrast(trunk, width(2, 2.2), trunk, width(2.1, 2.3), shared=True)
    assert observed["sign"] == "unresolved" and observed["delta_lower"] < 0 < observed["delta_upper"]
    assert width_contrast(trunk, width(2, 2.1), trunk, width(3, None), shared=True)["sign"] == "narrower"
    censored_trunk = width(10,None)
    assert width_contrast(censored_trunk,width(2,2),censored_trunk,width(3,3),shared=True)["delta"] == -1
    assert width_contrast(trunk, width(2, 2.1), width(10, 11), width(2.2, 2.3), shared=False)["sign"] == "unresolved"
    assert attainable_p(4, 0, 8) == 163/256
    assert attainable_p(0, 1, 8) == 1/128


def test_scoring_batch_eligibility_counts_tokenwise_predictions():
    from thirdloss.probe_check import choose_scoring_batch
    reference = dict(batch=2, nll=2., accuracy=.5, tokens=4, targets_per_second=100,
                     peak_allocated_mib=100, top1_mismatches=0)
    slower = {**reference, "batch":8, "targets_per_second":120, "top1_mismatches":1}
    different = {**reference, "batch":16, "targets_per_second":150, "top1_mismatches":3}
    assert choose_scoring_batch([reference, slower, different])["batch"] == 8
    assert choose_scoring_batch([reference, different])["batch"] == 2
