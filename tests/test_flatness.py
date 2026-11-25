"""Verify geometry statistics, censoring and a Hessian known exactly in the chosen coordinates."""

import math

import pytest
import torch


def test_curvature_keeps_trace_signs_and_counts_negative_eigenvalues_in_rms():
    from thirdloss.checkpoint_flatness import hessian_statistics
    p=torch.tensor([1.,2.,3.],dtype=torch.float64,requires_grad=True)
    diagonal=torch.tensor([-2.,0.,5.],dtype=torch.float64)
    result=hessian_statistics((diagonal*p.square()).sum()/2,(p,))
    assert result["trace_per_parameter"]==pytest.approx(1.)
    assert result["rms_curvature"]==pytest.approx(math.sqrt(29/3))
    assert len(result["draws"])==8 and result["dimensions"]==3


def test_direction_quantiles_propagate_open_bounds_without_dropping_rays():
    from thirdloss.flatness_stats import direction_summary,quantile_bounds
    def direction(i,upper):
        return {"direction":i,"negative":{"lower":0.,"upper":0.},"positive":{"lower":float(i),"upper":upper}}
    data=direction_summary({"directions":[direction(1,1.),direction(2,2.),direction(3,3.),direction(4,None)]})
    assert data["ray_count"]==8 and data["direction_q1"]==pytest.approx([1.75,1.75])
    assert data["direction_q3"]==[3.25,None]
    assert quantile_bounds([[2.,None]],.5)==[2.,None]


def test_flatness_table_preserves_seed_count_and_geometry_units():
    from thirdloss.flatness_tables import hybrid_flatness_table
    rows=[]
    for seed,method,initial,end in ((21,"adaptive",10.,8.),(22,"adaptive",11.,9.),(21,"late",10.,7.)):
        point={"width":end,"width_lower":end,"width_upper":end,"direction_q1":[5.,5.],
               "direction_q3":[9.,9.],"ray_count":32,"censored_rays":0,"baseline_nll":2.}
        rows.append({"stage":"stories","phase":"hybrid","method":method,"seed":seed,"status":"complete",
                     "tokens":2**24,"widths":{"2048":{**point,"width":initial,"width_lower":initial,"width_upper":initial},
                                              "4096":point}})
    table=hybrid_flatness_table(rows)
    assert "21, 22" in table and "8.500" in table and "8.000–9.000" in table and "0/64" in table
    assert "5.000–9.000" in table and "21 |" in table


def test_primary_flatness_summary_compares_only_common_probe_provenance():
    from thirdloss.flatness_tables import primary_flatness_rows
    r={"protocol":"v1","probe_windows_sha256":"same","width_device":"cuda","hessian_device":"cpu",
       "width":7.,"width_lower":6.99,"width_upper":7.01,"ray_count":32,"censored_rays":0,
       "baseline_nll":2.,"rms_curvature":.1,"trace_per_parameter":-.01}
    pairs=[{m:{"flatness":dict(r)} for m in ("ce","trace","third")} for _ in range(2)]
    stats=primary_flatness_rows(pairs)
    assert stats[0][1:]==["7.000"]*3 and stats[3][1:]==["0/64"]*3
    for arm in pairs[1].values():
        arm["flatness"]["probe_windows_sha256"]="different"
    with pytest.raises(ValueError,match="same probes"):
        primary_flatness_rows(pairs)
