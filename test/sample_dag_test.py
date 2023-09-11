"""
dags/sample/test.py 테스트 스크립트
"""
from . import internal_unit_testing


def test_sample_dag():
    from dags.sample import test
    internal_unit_testing.assert_has_valid_dag(test)
