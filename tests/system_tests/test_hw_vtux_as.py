"""Tests for vtux-as system"""

import time
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
    assert test_cpxap.read_module_count() == 4


def test_modules(test_cpxap):
    assert all(isinstance(m, ApModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].output_register == 0  # EP
    assert test_cpxap.modules[1].output_register == 0  # VABX-A-S-BV-V4A
    assert test_cpxap.modules[2].output_register == 1  # VABX-A-S-VE-VBH
    assert test_cpxap.modules[3].output_register == 2  #  VABX-A-S-VE-VBL

    assert test_cpxap.modules[0].input_register == 5000  # EP
    assert test_cpxap.modules[1].input_register == 5000  # VABX-A-S-BV-V4A
    assert test_cpxap.modules[2].input_register == 5001  # VABX-A-S-VE-VBH
    assert test_cpxap.modules[3].input_register == 5003  #  VABX-A-S-VE-VBL

    assert test_cpxap.diagnosis_register == 11000  # cpx system global diagnosis
    assert test_cpxap.modules[0].diagnosis_register == 11006  # EP
    assert test_cpxap.modules[1].diagnosis_register == 11012  # VABX-A-S-BV-V4A
    assert test_cpxap.modules[2].diagnosis_register == 11018  # VABX-A-S-VE-VBH
    assert test_cpxap.modules[3].diagnosis_register == 11024  # VABX-A-S-VE-VBL


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].input_channels) == 0  # EP
    assert len(test_cpxap.modules[1].input_channels) == 8  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[2].input_channels) == 3  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[3].input_channels) == 3  # VABX-A-S-VE-VBL

    assert len(test_cpxap.modules[0].output_channels) == 0  # EP
    assert len(test_cpxap.modules[1].output_channels) == 8  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[2].output_channels) == 1  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[3].output_channels) == 1  # VABX-A-S-VE-VBL

    assert len(test_cpxap.modules[0].inout_channels) == 0  # EP
    assert len(test_cpxap.modules[1].inout_channels) == 0  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[2].inout_channels) == 0  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[3].inout_channels) == 0  # VABX-A-S-VE-VBL


def test_vabx_a_s_bv_v4a_read_channels(test_cpxap):
    m = test_cpxap.modules[1]
    # 8 optional inputs (True) and 8 outputs (False)
    assert m.read_channels() == [True] * 8 + [False] * 8


def test_vabx_a_s_bv_v4a_read_output_channels(test_cpxap):
    m = test_cpxap.modules[1]

    assert m.read_output_channels() == [False] * 8


def test_vabx_a_s_bv_v4a_read_channel(test_cpxap):
    m = test_cpxap.modules[1]

    for i in range(8):
        assert m.read_channel(i) is True
    for i in range(8, 16):
        assert m.read_channel(i) is False


def test_vabx_a_s_bv_v4a_read_output_channel(test_cpxap):
    m = test_cpxap.modules[1]
    for i in range(8):
        assert m.read_output_channel(i) is False


def test_vabx_a_s_bv_v4a_write(test_cpxap):
    m = test_cpxap.modules[1]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_output_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_output_channel(i) is False


def test_vabx_a_s_bv_v4a_parameters(test_cpxap):
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

def test_vabx_a_s_ve_vbh_read_channels(test_cpxap):
    m = test_cpxap.modules[2]
    # Channel 0 (INT), Input 0 (UINT), Process Quality 0 (UINT)
    assert m.read_channels() == [0] * 3


def test_vabx_a_s_ve_vbh_read_output_channels(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_output_channels() == [0]


def test_vabx_a_s_ve_vbh_read_channel(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(3):
        assert m.read_channel(i) == 0


def test_vabx_a_s_ve_vbh_read_output_channel(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_output_channel(0) == 0


def test_vabx_a_s_ve_vbh_write(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(-10,10):
        m.write_channel(0, i)
        time.sleep(0.05)
        assert m.read_output_channel(0) == i
        time.sleep(0.05)
        m.write_channel(0, 0)
        time.sleep(0.05)
        assert m.read_output_channel(0) == 0


def test_vabx_a_s_ve_vbh_parameters(test_cpxap):
    m = test_cpxap.modules[2]
    assert m.read_module_parameter(
        "Enable diagnosis for defect valve"
    ) == m.read_module_parameter(20021)
    assert m.read_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC"
    ) == m.read_module_parameter(20022)
    assert m.read_module_parameter(
        "Enable monitoring of parameter errors"
    ) == m.read_module_parameter(20030)
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
        "Application specific Tag"
    ) == m.read_module_parameter(20118)
    assert m.read_module_parameter(
        "Setup diagnosis wrong valve connected"
    ) == m.read_module_parameter(20208)
    assert m.read_module_parameter(
        "Enable diagnosis on B10 overflow"
    ) == m.read_module_parameter(20209)
    assert m.read_module_parameter(
        "Process Diagnosis"
    ) == m.read_module_parameter(20211)
    assert m.read_module_parameter(
        "Interlock ejector pulse"
    ) == m.read_module_parameter(20212)
    assert m.read_module_parameter(
        "Threshold process quality"
    ) == m.read_module_parameter(20221)
    assert m.read_module_parameter(
        "Limit Evacuation Time"
    ) == m.read_module_parameter(20240)
    assert m.read_module_parameter(
        "Limit Venting Time"
    ) == m.read_module_parameter(20241)
    assert m.read_module_parameter(
        "Auto-Drop Time"
    ) == m.read_module_parameter(20242)
    assert m.read_module_parameter(
        "Automatic Drop Impulse"
    ) == m.read_module_parameter(20243)
    assert m.read_module_parameter(
        "Air-Save Function"
    ) == m.read_module_parameter(20244)
    assert m.read_module_parameter(
        "Switching point A1"
    ) == m.read_module_parameter(20245)
    assert m.read_module_parameter(
        "Hysteresis A"
    ) == m.read_module_parameter(20246)
    assert m.read_module_parameter(
        "Switching Point B1"
    ) == m.read_module_parameter(20247)
    assert m.read_module_parameter(
        "Hysteresis B"
    ) == m.read_module_parameter(20248)
    assert m.read_module_parameter(
        "Switching Point A2"
    ) == m.read_module_parameter(20249)
    assert m.read_module_parameter(
        "Switching Point B2"
    ) == m.read_module_parameter(20250)
    assert m.read_module_parameter(
        "Pressure unit"
    ) == m.read_module_parameter(20251)
    assert m.read_module_parameter(
        "Lock code"
    ) == m.read_module_parameter(20252)
    assert m.read_module_parameter(
        "Switchpoint logic"
    ) == m.read_module_parameter(20253)
    assert m.read_module_parameter(
        "Switchpoint mode"
    ) == m.read_module_parameter(20254)


def test_vabx_a_s_ve_vbl_read_channels(test_cpxap):
    m = test_cpxap.modules[3]
    # 8 optional inputs (True) and 8 outputs (False)
    assert m.read_channels() == [True] * 8 + [False] * 8


def test_vabx_a_s_ve_vbl_read_output_channels(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_output_channels() == [False] * 8


def test_vabx_a_s_ve_vbl_read_channel(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(8):
        assert m.read_channel(i) is True
    for i in range(8, 16):
        assert m.read_channel(i) is False


def test_vabx_a_s_ve_vbl_read_output_channel(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_output_channel(0) == 0


def test_vabx_a_s_ve_vbl_write(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(-10,10):
        m.write_channel(0, i)
        time.sleep(0.05)
        assert m.read_output_channel(0) == i
        time.sleep(0.05)
        m.write_channel(0, 0)
        time.sleep(0.05)
        assert m.read_output_channel(0) == 0


def test_vabx_a_s_ve_vbl_parameters(test_cpxap):
    m = test_cpxap.modules[3]
    assert m.read_module_parameter(
        "Enable diagnosis for defect valve"
    ) == m.read_module_parameter(20021)
    assert m.read_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC"
    ) == m.read_module_parameter(20022)
    assert m.read_module_parameter(
        "Enable monitoring of parameter errors"
    ) == m.read_module_parameter(20030)
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
        "Application specific Tag"
    ) == m.read_module_parameter(20118)
    assert m.read_module_parameter(
        "Setup diagnosis wrong valve connected"
    ) == m.read_module_parameter(20208)
    assert m.read_module_parameter(
        "Enable diagnosis on B10 overflow"
    ) == m.read_module_parameter(20209)
    assert m.read_module_parameter(
        "Process Diagnosis"
    ) == m.read_module_parameter(20211)
    assert m.read_module_parameter(
        "Interlock ejector pulse"
    ) == m.read_module_parameter(20212)
    assert m.read_module_parameter(
        "Threshold process quality"
    ) == m.read_module_parameter(20221)
    assert m.read_module_parameter(
        "Limit Evacuation Time"
    ) == m.read_module_parameter(20240)
    assert m.read_module_parameter(
        "Limit Venting Time"
    ) == m.read_module_parameter(20241)
    assert m.read_module_parameter(
        "Auto-Drop Time"
    ) == m.read_module_parameter(20242)
    assert m.read_module_parameter(
        "Automatic Drop Impulse"
    ) == m.read_module_parameter(20243)
    assert m.read_module_parameter(
        "Air-Save Function"
    ) == m.read_module_parameter(20244)
    assert m.read_module_parameter(
        "Switching point A1"
    ) == m.read_module_parameter(20245)
    assert m.read_module_parameter(
        "Hysteresis A"
    ) == m.read_module_parameter(20246)
    assert m.read_module_parameter(
        "Switching Point B1"
    ) == m.read_module_parameter(20247)
    assert m.read_module_parameter(
        "Hysteresis B"
    ) == m.read_module_parameter(20248)
    assert m.read_module_parameter(
        "Switching Point A2"
    ) == m.read_module_parameter(20249)
    assert m.read_module_parameter(
        "Switching Point B2"
    ) == m.read_module_parameter(20250)
    assert m.read_module_parameter(
        "Pressure unit"
    ) == m.read_module_parameter(20251)
    assert m.read_module_parameter(
        "Lock code"
    ) == m.read_module_parameter(20252)
    assert m.read_module_parameter(
        "Switchpoint logic"
    ) == m.read_module_parameter(20253)
    assert m.read_module_parameter(
        "Switchpoint mode"
    ) == m.read_module_parameter(20254)
