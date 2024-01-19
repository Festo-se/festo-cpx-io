"""Tests for cpx base class"""
import pytest

from cpx_io.cpx_system.cpx_base import CpxBase


@pytest.fixture(scope="module")
def test_cpx_base():
    base = CpxBase(ip_address="172.16.1.40")
    yield base


def test_init(test_cpx_base):
    assert test_cpx_base


def test_read_reg_data(test_cpx_base):
    data = test_cpx_base.read_reg_data(40001)
    assert data == [0]


def test_read_reg_data_more(test_cpx_base):
    data = test_cpx_base.read_reg_data(40001, 2)
    assert data == [0, 0]


def test_write_reg_data_wrong_type(test_cpx_base):
    with pytest.raises(TypeError):
        test_cpx_base.write_reg_data("test", 40001)
