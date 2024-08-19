"""Tests for vtux-as system"""

import time
import struct
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.45") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 2


def test_modules(test_cpxap):
    assert all(isinstance(m, ApModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].output_register == 0  # EP
    assert test_cpxap.modules[1].output_register == 0  # VABX

    assert test_cpxap.modules[0].input_register == 5000  # EP
    assert test_cpxap.modules[1].input_register == 5000  # VABX

    assert test_cpxap.diagnosis_register == 11000  # cpx system global diagnosis
    assert test_cpxap.modules[0].diagnosis_register == 11006  # EP
    assert test_cpxap.modules[1].diagnosis_register == 11012  # VABX


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].input_channels) == 0  # EP
    assert len(test_cpxap.modules[1].input_channels) == 8  # VABX

    assert len(test_cpxap.modules[0].output_channels) == 0  # EP
    assert len(test_cpxap.modules[1].output_channels) == 8  # VABX

    assert len(test_cpxap.modules[0].inout_channels) == 0  # EP
    assert len(test_cpxap.modules[1].inout_channels) == 0  # VABX


def test_vabx_read_channels(test_cpxap):
    m = test_cpxap.modules[1]
    # 8 optional inputs (True) and 8 outputs (False)
    assert m.read_channels() == [True] * 8 + [False] * 8


def test_vabx_read_output_channels(test_cpxap):
    m = test_cpxap.modules[1]

    assert m.read_output_channels() == [False] * 8


def test_vabx_read_channel(test_cpxap):
    m = test_cpxap.modules[1]

    for i in range(8):
        assert m.read_channel(i) is True
    for i in range(8, 16):
        assert m.read_channel(i) is False


def test_vabx_read_output_channel(test_cpxap):
    m = test_cpxap.modules[1]
    for i in range(8):
        assert m.read_output_channel(i) is False


def test_vabx_write(test_cpxap):
    m = test_cpxap.modules[1]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_output_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_output_channel(i) is False


def test_vabx_parameters(test_cpxap):
    m = test_cpxap.modules[1]
    assert m.read_module_parameter(
        "Enable diagnosis for defect valve"
    ) == m.read_module_parameter(20021)
    assert m.read_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC"
    ) == m.read_module_parameter(20022)
    assert m.read_module_parameter(
        "Behaviour in fail state"
    ) == m.read_module_parameter(20052)
    assert m.read_module_parameter(
        "Condition counter set point"
    ) == m.read_module_parameter(20094)
    assert m.read_module_parameter(
        "Condition counter actual value"
    ) == m.read_module_parameter(20095)
    assert m.read_module_parameter(
        "Lifecycle counter set point"
    ) == m.read_module_parameter(20116)
    assert m.read_module_parameter(
        "Type of  Digital Input module"  # there is a double space here in the ADPP
    ) == m.read_module_parameter(20201)
    assert m.read_module_parameter("B10 Value") == m.read_module_parameter(20203)
    assert m.read_module_parameter("Valve function") == m.read_module_parameter(20205)
    assert m.read_module_parameter(
        "Lifecycle counter actual value"
    ) == m.read_module_parameter(20206)
    assert m.read_module_parameter(
        "Setup diagnosis wrong valve connected"
    ) == m.read_module_parameter(20208)
