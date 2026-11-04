"""Mutation checks for the numerical and identity reproduction contract."""
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('kdd_run_all',Path(__file__).resolve().parents[1]/'tools/verify_reference.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def record(patient='a',probability=.5):
    return {'columns':['ID','p'],'records':[{'ID':patient,'p':probability}]}


def test_probability_roundoff_within_tolerance_is_equivalent():
    runner.compare_records(record(),record(probability=.5+1e-12))


def test_material_probability_drift_is_rejected():
    with pytest.raises(AssertionError):runner.compare_records(record(),record(probability=.50001))


def test_new_id_is_rejected_even_with_same_probability():
    with pytest.raises(AssertionError):runner.compare_records(record(),record(patient='b'))


def test_partition_hash_change_is_rejected():
    with pytest.raises(AssertionError):runner.compare_values({'particoes_sha256':'old'},{'particoes_sha256':'new'})


def test_missing_or_new_metric_keys_are_rejected():
    with pytest.raises(AssertionError):runner.compare_values({'recall':.7},{'recall':.7,'precision':.9})


def test_numeric_identity_is_exact_not_probability_tolerance():
    with pytest.raises(AssertionError):
        runner.compare_records(record(patient=1.0),record(patient=1.0+1e-12))
