"""Tests for vtux-as system"""

import time
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule

SYSTEM_IP_ADDRESS = "172.16.1.45"


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address=SYSTEM_IP_ADDRESS) as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 5


def test_diagnostic_status(test_cpxap):
    "test diagnostic status"
    diagnostics = test_cpxap.read_diagnostic_status()
    assert len(diagnostics) == test_cpxap.read_module_count() + 1
    assert all(isinstance(d, CpxAp.Diagnostics) for d in diagnostics)



def test_modules(test_cpxap):
    assert all(isinstance(m, ApModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].system_entry_registers.outputs == 0  # 4AI
    assert test_cpxap.modules[1].system_entry_registers.outputs == 0  # EP
    assert test_cpxap.modules[2].system_entry_registers.outputs == 0  # VABX-A-S-BV-V4A
    assert test_cpxap.modules[3].system_entry_registers.outputs == 1  # VABX-A-S-VE-VBH
    assert test_cpxap.modules[4].system_entry_registers.outputs == 2  #  VABX-A-S-VE-VBL

    assert test_cpxap.modules[0].system_entry_registers.inputs == 5000  # 4AI
    assert test_cpxap.modules[1].system_entry_registers.inputs == 5004  # EP
    assert test_cpxap.modules[2].system_entry_registers.inputs == 5004  # ..-V4A
    assert test_cpxap.modules[3].system_entry_registers.inputs == 5005  # ..-VBH
    assert test_cpxap.modules[4].system_entry_registers.inputs == 5007  #  ..-VBL

    assert test_cpxap.global_diagnosis_register == 11000  # cpx system global diagnosis
    assert test_cpxap.modules[0].system_entry_registers.diagnosis == 11006  # 4AI
    assert test_cpxap.modules[1].system_entry_registers.diagnosis == 11012  # EP
    assert test_cpxap.modules[2].system_entry_registers.diagnosis == 11018  # ..-V4A
    assert test_cpxap.modules[3].system_entry_registers.diagnosis == 11024  # ..-VBH
    assert test_cpxap.modules[4].system_entry_registers.diagnosis == 11030  # ..-VBL


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].channels.inputs) == 4  # 4AI
    assert len(test_cpxap.modules[1].channels.inputs) == 0  # EP
    assert len(test_cpxap.modules[2].channels.inputs) == 8  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[3].channels.inputs) == 3  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[4].channels.inputs) == 3  # VABX-A-S-VE-VBL

    assert len(test_cpxap.modules[0].channels.outputs) == 0  # 4AI
    assert len(test_cpxap.modules[1].channels.outputs) == 0  # EP
    assert len(test_cpxap.modules[2].channels.outputs) == 8  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[3].channels.outputs) == 1  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[4].channels.outputs) == 1  # VABX-A-S-VE-VBL

    assert len(test_cpxap.modules[0].channels.inouts) == 0  # 4AI
    assert len(test_cpxap.modules[1].channels.inouts) == 0  # EP
    assert len(test_cpxap.modules[2].channels.inouts) == 0  # VABX-A-S-BV-V4A
    assert len(test_cpxap.modules[3].channels.inouts) == 0  # VABX-A-S-VE-VBH
    assert len(test_cpxap.modules[4].channels.inouts) == 0  # VABX-A-S-VE-VBL


def test_4AiUI_None(test_cpxap):
    m = test_cpxap.modules[0]
    assert len(m.read_channels()) == 4


def test_4AiUI_analog5V0_CH3(test_cpxap):
    # this depends on external 5.0 Volts at input channel 3
    m = test_cpxap.modules[0]
    channel = 3
    m.write_module_parameter("Signalrange", "0 .. 10 V", channel)
    time.sleep(0.05)
    m.write_module_parameter("Enable linear scaling", False, channel)
    time.sleep(0.05)
    assert 15800 < m.read_channel(channel) < 16200


def test_4AiUI_analog5V0_CH3_with_scaling(test_cpxap):
    # this depends on external 5.0 Volts at input channel 1
    m = test_cpxap.modules[0]
    channel = 3
    m.write_module_parameter("Signalrange", "0 .. 10 V", channel)
    time.sleep(0.05)
    m.write_module_parameter("Upper threshold value", 10000, channel)
    time.sleep(0.05)
    m.write_module_parameter("Lower threshold value", 0, channel)
    time.sleep(0.05)
    m.write_module_parameter("Enable linear scaling", True)

    assert 4900 < m.read_channel(channel) < 5100

    m.write_module_parameter("Upper threshold value", 32767)
    m.write_module_parameter("Lower threshold value", -32768)
    m.write_module_parameter("Enable linear scaling", False)


def test_4AiUI_parameters(test_cpxap):
    m = test_cpxap.modules[0]
    assert m.read_module_parameter("Temperature unit") == m.read_module_parameter(20032)
    assert m.read_module_parameter("Signalrange") == m.read_module_parameter(20043)
    assert m.read_module_parameter("Upper threshold value") == m.read_module_parameter(
        20044
    )
    assert m.read_module_parameter("Lower threshold value") == m.read_module_parameter(
        20045
    )
    assert m.read_module_parameter(
        "Hysteresis for measured value monitoring"
    ) == m.read_module_parameter(20046)
    assert m.read_module_parameter("Smoothing") == m.read_module_parameter(20107)
    assert m.read_module_parameter("Enable linear scaling") == m.read_module_parameter(
        20111
    )


def test_vabx_a_s_bv_v4a_read_channels(test_cpxap):
    m = test_cpxap.modules[2]
    # 8 optional inputs (True) and 8 outputs (False)
    assert m.read_channels() == [True] * 8 + [False] * 8


def test_vabx_a_s_bv_v4a_read_output_channels(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_output_channels() == [False] * 8


def test_vabx_a_s_bv_v4a_read_channel(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(8):
        assert m.read_channel(i) is True
    for i in range(8, 16):
        assert m.read_channel(i) is False


def test_vabx_a_s_bv_v4a_read_output_channel(test_cpxap):
    m = test_cpxap.modules[2]
    for i in range(8):
        assert m.read_output_channel(i) is False


def test_vabx_a_s_bv_v4a_write(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_output_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_output_channel(i) is False


def test_vabx_a_s_bv_v4a_parameters(test_cpxap):
    m = test_cpxap.modules[2]
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
    m = test_cpxap.modules[3]
    # Channel 0 (INT), Input 0 (UINT), Process Quality 0 (UINT), Output (UINT16)
    channels = m.read_channels()

    assert channels[0] == 0
    # this value can change
    assert isinstance(channels[1], int)
    assert channels[2] == 0
    assert channels[3] == [0, 0]


def test_vabx_a_s_ve_vbh_read_output_channels(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_output_channels() == [[0, 0]]


def test_vabx_a_s_ve_vbh_read_channel(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_channel(0) == 0
    # this value can change
    assert isinstance(m.read_channel(1), int)
    assert m.read_channel(2) == 0
    assert m.read_channel(3) == [0, 0]


def test_vabx_a_s_ve_vbh_read_output_channel(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_output_channel(0) == [0, 0]


def test_vabx_a_s_ve_vbh_write(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(0, 255, 32):
        m.write_channel(0, [i, i + 1])
        time.sleep(0.05)
        assert m.read_output_channel(0) == [i, i + 1]
        time.sleep(0.05)
        m.write_channel(0, [0, 0])
        time.sleep(0.05)
        assert m.read_output_channel(0) == [0, 0]

    m.write_channel(0, [0, 0])


def test_vabx_a_s_ve_vbh_write_channels(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_channels([[1, 0]])
    time.sleep(0.05)
    assert m.read_output_channel(0) == [1, 0]
    assert m.read_output_channels()[0] == [1, 0]
    time.sleep(0.05)
    m.write_channels([[0, 0]])
    time.sleep(0.05)
    assert m.read_output_channel(0) == [0, 0]
    assert m.read_output_channels()[0] == [0, 0]


def test_vabx_a_s_ve_vbh_parameters(test_cpxap):
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
        "Behavior in fail state"  # Spelling error in current APDD version
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
    assert m.read_module_parameter("Process Diagnosis") == m.read_module_parameter(
        20211
    )
    assert m.read_module_parameter(
        "Interlock ejector pulse"
    ) == m.read_module_parameter(20212)
    assert m.read_module_parameter(
        "Threshold process quality"
    ) == m.read_module_parameter(20221)
    assert m.read_module_parameter("Limit Evacuation Time") == m.read_module_parameter(
        20240
    )
    assert m.read_module_parameter("Limit Venting Time") == m.read_module_parameter(
        20241
    )
    assert m.read_module_parameter("Auto-Drop Time") == m.read_module_parameter(20242)
    assert m.read_module_parameter("Automatic Drop Impulse") == m.read_module_parameter(
        20243
    )
    assert m.read_module_parameter("Air-Save Function") == m.read_module_parameter(
        20244
    )
    assert m.read_module_parameter("Switching point A1") == m.read_module_parameter(
        20245
    )
    assert m.read_module_parameter("Hysteresis A") == m.read_module_parameter(20246)
    assert m.read_module_parameter("Switching Point B1") == m.read_module_parameter(
        20247
    )
    assert m.read_module_parameter("Hysteresis B") == m.read_module_parameter(20248)
    assert m.read_module_parameter("Switching Point A2") == m.read_module_parameter(
        20249
    )
    assert m.read_module_parameter("Switching Point B2") == m.read_module_parameter(
        20250
    )
    assert m.read_module_parameter("Pressure unit") == m.read_module_parameter(20251)
    assert m.read_module_parameter("Lock code") == m.read_module_parameter(20252)
    assert m.read_module_parameter("Switchpoint logic") == m.read_module_parameter(
        20253
    )
    assert m.read_module_parameter("Switchpoint mode") == m.read_module_parameter(20254)


def test_vabx_a_s_ve_vbl_read_channels(test_cpxap):
    m = test_cpxap.modules[4]
    # Channel 0 (INT), Input 0 (UINT), Process Quality 0 (UINT), Output (UINT16)
    channels = m.read_channels()

    assert channels[0] == 0
    # this value can change
    assert isinstance(channels[1], int)
    assert channels[2] == 0
    assert channels[3] == [0, 0]


def test_vabx_a_s_ve_vbl_read_output_channels(test_cpxap):
    m = test_cpxap.modules[4]

    assert m.read_output_channels() == [[0, 0]]


def test_vabx_a_s_ve_vbl_read_channel(test_cpxap):
    m = test_cpxap.modules[4]

    assert m.read_channel(0) == 0
    # this value can change
    assert isinstance(m.read_channel(1), int)
    assert m.read_channel(2) == 0
    assert m.read_channel(3) == [0, 0]


def test_vabx_a_s_ve_vbl_read_output_channel(test_cpxap):
    m = test_cpxap.modules[4]

    assert m.read_output_channel(0) == [0, 0]


def test_vabx_a_s_ve_vbl_write(test_cpxap):
    m = test_cpxap.modules[4]

    for i in range(0, 255, 32):
        m.write_channel(0, [i, i + 1])
        time.sleep(0.05)
        assert m.read_output_channel(0) == [i, i + 1]
        time.sleep(0.05)
        m.write_channel(0, [0, 0])
        time.sleep(0.05)
        assert m.read_output_channel(0) == [0, 0]


def test_vabx_a_s_ve_vbl_write_channels(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_channels([[1, 0]])
    time.sleep(0.05)
    assert m.read_output_channel(0) == [1, 0]
    assert m.read_output_channels() == [[1, 0]]
    time.sleep(0.05)
    m.write_channels([[0, 0]])
    time.sleep(0.05)
    assert m.read_output_channel(0) == [0, 0]
    assert m.read_output_channels() == [[0, 0]]


def test_vabx_a_s_ve_vbl_parameters(test_cpxap):
    m = test_cpxap.modules[4]
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
        "Behavior in fail state"  # Spelling error in current APDD version
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
    assert m.read_module_parameter("Process Diagnosis") == m.read_module_parameter(
        20211
    )
    assert m.read_module_parameter(
        "Interlock ejector pulse"
    ) == m.read_module_parameter(20212)
    assert m.read_module_parameter(
        "Threshold process quality"
    ) == m.read_module_parameter(20221)
    assert m.read_module_parameter("Limit Evacuation Time") == m.read_module_parameter(
        20240
    )
    assert m.read_module_parameter("Limit Venting Time") == m.read_module_parameter(
        20241
    )
    assert m.read_module_parameter("Auto-Drop Time") == m.read_module_parameter(20242)
    assert m.read_module_parameter("Automatic Drop Impulse") == m.read_module_parameter(
        20243
    )
    assert m.read_module_parameter("Air-Save Function") == m.read_module_parameter(
        20244
    )
    assert m.read_module_parameter("Switching point A1") == m.read_module_parameter(
        20245
    )
    assert m.read_module_parameter("Hysteresis A") == m.read_module_parameter(20246)
    assert m.read_module_parameter("Switching Point B1") == m.read_module_parameter(
        20247
    )
    assert m.read_module_parameter("Hysteresis B") == m.read_module_parameter(20248)
    assert m.read_module_parameter("Switching Point A2") == m.read_module_parameter(
        20249
    )
    assert m.read_module_parameter("Switching Point B2") == m.read_module_parameter(
        20250
    )
    assert m.read_module_parameter("Pressure unit") == m.read_module_parameter(20251)
    assert m.read_module_parameter("Lock code") == m.read_module_parameter(20252)
    assert m.read_module_parameter("Switchpoint logic") == m.read_module_parameter(
        20253
    )
    assert m.read_module_parameter("Switchpoint mode") == m.read_module_parameter(20254)
