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
