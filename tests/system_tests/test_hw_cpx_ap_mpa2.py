"""Tests for cpx-ap system"""

import time
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import CpxModule


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.44") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 9


def test_modules(test_cpxap):
    assert all(isinstance(m, CpxModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].output_register == 0  # 1 CPX-AP-A-EP-M12
    assert test_cpxap.modules[1].output_register == 0  # 2 VMPA-AP-EPL-G
    assert test_cpxap.modules[2].output_register == 0  # 3 VMPA-P-RP
    assert test_cpxap.modules[3].output_register == 1  # 4 VPPM-6TA-L-1-F-0L2H__
    assert test_cpxap.modules[4].output_register == 2  # 5 VMPA1-FB-EMG-8
    assert test_cpxap.modules[5].output_register == 3  # 6 VMPA-FB-EMG-P5
    assert test_cpxap.modules[6].output_register == 4  # 7 VMPA-FB-PS-__
    assert test_cpxap.modules[7].output_register == 4  # 8 VMPA1-FB-EMG-8-S
    assert test_cpxap.modules[8].output_register == 5  # 9 VMPA2-FB-EMG-4

    assert test_cpxap.modules[0].input_register == 5000  # 1 CPX-AP-A-EP-M12
    assert test_cpxap.modules[1].input_register == 5000  # 2 VMPA-AP-EPL-G
    assert test_cpxap.modules[2].input_register == 5000  # 3 VMPA-P-RP
    assert test_cpxap.modules[3].input_register == 5001  # 4 VPPM-6TA-L-1-F-0L2H__
    assert test_cpxap.modules[4].input_register == 5002  # 5 VMPA1-FB-EMG-8
    assert test_cpxap.modules[5].input_register == 5002  # 6 VMPA-FB-EMG-P5
    assert test_cpxap.modules[6].input_register == 5003  # 7 VMPA-FB-PS-__
    assert test_cpxap.modules[7].input_register == 5004  # 8 VMPA1-FB-EMG-8-S
    assert test_cpxap.modules[8].input_register == 5005  # 9 VMPA2-FB-EMG-4


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].input_channels) == 0  # CPX-AP-A-EP-M12
    assert len(test_cpxap.modules[1].input_channels) == 0  # VMPA-AP-EPL-G
    assert len(test_cpxap.modules[2].input_channels) == 1  # VMPA-P-RP
    assert len(test_cpxap.modules[3].input_channels) == 1  # VPPM-6TA-L-1-F-0L2H__
    assert len(test_cpxap.modules[4].input_channels) == 0  # VMPA1-FB-EMG-8
    assert len(test_cpxap.modules[5].input_channels) == 8  # VMPA-FB-EMG-P5
    assert len(test_cpxap.modules[6].input_channels) == 1  # VMPA-FB-PS-__
    assert len(test_cpxap.modules[7].input_channels) == 8  # VMPA1-FB-EMG-8-S
    assert len(test_cpxap.modules[8].input_channels) == 0  # VMPA2-FB-EMG-4

    assert len(test_cpxap.modules[0].output_channels) == 0  # CPX-AP-A-EP-M12
    assert len(test_cpxap.modules[1].output_channels) == 0  # VMPA-AP-EPL-G
    assert len(test_cpxap.modules[2].output_channels) == 1  # VMPA-P-RP
    assert len(test_cpxap.modules[3].output_channels) == 1  # VPPM-6TA-L-1-F-0L2H__
    assert len(test_cpxap.modules[4].output_channels) == 8  # VMPA1-FB-EMG-8
    assert len(test_cpxap.modules[5].output_channels) == 8  # VMPA-FB-EMG-P5
    assert len(test_cpxap.modules[6].output_channels) == 0  # VMPA-FB-PS-__
    assert len(test_cpxap.modules[7].output_channels) == 8  # VMPA1-FB-EMG-8-S
    assert len(test_cpxap.modules[8].output_channels) == 4  # VMPA2-FB-EMG-4


def test_ep_read_system_parameters(test_cpxap):
    m = test_cpxap.modules[0]
    param = m.read_system_parameters()

    assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.44"
    assert param.active_subnet_mask == "255.255.255.0"
    assert param.active_gateway_address == "0.0.0.0"
    assert param.mac_address == "00:0e:f0:94:9d:bb"
    assert param.setup_monitoring_load_supply == 1


def test_vmpa_ap_epl_g_name(test_cpxap):
    assert test_cpxap.modules[1].name == "vmpa_ap_epl_g"


def test_vmpa_p_rp_read_channels(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_channels() == [0, 0]


def test_vmpa_p_rp_read_channel(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_channel(0) == 0


def test_vmpa_p_rp_read_channel_outputs_only(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_channel(0, outputs_only=True) == 0


def test_vmpa_p_rp_write_channel(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_channel(0, 100)
    assert m.read_channel(0, outputs_only=True) == 100


def test_vmpa_p_rp_write_channels(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_channels([100])
    assert m.read_channels() == [0, 100]


def test_vmpa14_fb_emg_d2_8_s_read_channel(test_cpxap):
    m = test_cpxap.modules[2]

    assert m.read_channel(0) is True
    for i in range(1, 16):
        assert m.read_channel(i) is False


# TODO: go on with tests from here
def test_vmpa14_fb_emg_d2_8_s_write_channels(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_channels([True] * 8)
    time.sleep(0.05)

    assert m.read_channels()[8:16] == [True] * 8

    m.write_channels([False] * 8)
    time.sleep(0.05)

    assert m.read_channels()[8:16] == [False] * 8


def test_vmpa14_fb_emg_d2_8_s_write_channel(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is True

        m.write_channel(i, False)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is False


def test_vmpa14_fb_emg_d2_8_s_set_clear_channel(test_cpxap):
    m = test_cpxap.modules[2]

    for i in range(8):
        m.set_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is True

        m.clear_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is False


def test_vmpa14_fb_emg_d2_8_s_toggle_channel(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_channels([False] * 8)

    for i in range(8):
        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is True

        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i, outputs_only=True) is False


def test_vmpa14_fb_emg_d2_8_s_read_module_parameters(test_cpxap):
    m = test_cpxap.modules[2]
    time.sleep(0.05)

    assert m.read_module_parameter(20026) == m.read_module_parameter(
        "Enable diagnosis of overload short circuit"
    )
    assert m.read_module_parameter(20027) == m.read_module_parameter(
        "Enable diagnosis of open load"
    )
    assert m.read_module_parameter(20033) == m.read_module_parameter(
        "Monitor Vout/Vval"
    )
    assert m.read_module_parameter(20052) == m.read_module_parameter(
        "Behaviour in fail state"
    )
    assert m.read_module_parameter(20094) == m.read_module_parameter(
        "Condition counter set point"
    )
    assert m.read_module_parameter(20095) == m.read_module_parameter(
        "Condition counter actual value"
    )
    assert m.read_module_parameter(20419) == m.read_module_parameter(
        "Evacuation time limit"
    )
    assert m.read_module_parameter(20420) == m.read_module_parameter(
        "Inhibit time pressure diagnosis"
    )
    assert m.read_module_parameter(20422) == m.read_module_parameter(
        "Pilot air evacuation time"
    )


def test_vmpa1_fb_ems_d2_8_read_channels(test_cpxap):
    m = test_cpxap.modules[3]

    assert m.read_channels() == [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]


def test_vmpa1_fb_ems_d2_8_read_channel(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(8):
        assert m.read_channel(i) is False


def test_vmpa1_fb_ems_d2_8_write_channels(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_channels([True] * 8)
    time.sleep(0.05)

    assert m.read_channels() == [True] * 8

    m.write_channels([False] * 8)
    time.sleep(0.05)

    assert m.read_channels() == [False] * 8


def test_vmpa1_fb_ems_d2_8_write_channel(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.write_channel(i, False)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa1_fb_ems_d2_8_set_clear_channel(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(8):
        m.set_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.clear_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa1_fb_ems_d2_8_toggle_channel(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_channels([False] * 8)

    for i in range(8):
        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa1_fb_ems_d2_8_read_module_parameters(test_cpxap):
    m = test_cpxap.modules[3]
    time.sleep(0.05)

    assert m.read_module_parameter(20026) == m.read_module_parameter(
        "Enable diagnosis of overload short circuit"
    )
    assert m.read_module_parameter(20027) == m.read_module_parameter(
        "Enable diagnosis of open load"
    )
    assert m.read_module_parameter(20033) == m.read_module_parameter(
        "Monitor Vout/Vval"
    )
    assert m.read_module_parameter(20052) == m.read_module_parameter(
        "Behaviour in fail state"
    )
    assert m.read_module_parameter(20094) == m.read_module_parameter(
        "Condition counter set point"
    )
    assert m.read_module_parameter(20095) == m.read_module_parameter(
        "Condition counter actual value"
    )


def test_vmpa14_fb_ems_d2_8_read_channels(test_cpxap):
    m = test_cpxap.modules[4]

    assert m.read_channels() == [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]


def test_vmpa14_fb_ems_d2_8_read_channel(test_cpxap):
    m = test_cpxap.modules[4]

    for i in range(8):
        assert m.read_channel(i) is False


def test_vmpa14_fb_ems_d2_8_write_channels(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_channels([True] * 8)
    time.sleep(0.05)

    assert m.read_channels() == [True] * 8

    m.write_channels([False] * 8)
    time.sleep(0.05)

    assert m.read_channels() == [False] * 8


def test_vmpa14_fb_ems_d2_8_write_channel(test_cpxap):
    m = test_cpxap.modules[4]

    for i in range(8):
        m.write_channel(i, True)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.write_channel(i, False)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa14_fb_ems_d2_8_set_clear_channel(test_cpxap):
    m = test_cpxap.modules[4]

    for i in range(8):
        m.set_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.clear_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa14_fb_ems_d2_8_toggle_channel(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_channels([False] * 8)

    for i in range(8):
        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa14_fb_ems_d2_8_read_module_parameters(test_cpxap):
    m = test_cpxap.modules[4]
    time.sleep(0.05)

    assert m.read_module_parameter(20026) == m.read_module_parameter(
        "Enable diagnosis of overload short circuit"
    )
    assert m.read_module_parameter(20027) == m.read_module_parameter(
        "Enable diagnosis of open load"
    )
    assert m.read_module_parameter(20033) == m.read_module_parameter(
        "Monitor Vout/Vval"
    )
    assert m.read_module_parameter(20052) == m.read_module_parameter(
        "Behaviour in fail state"
    )
    assert m.read_module_parameter(20094) == m.read_module_parameter(
        "Condition counter set point"
    )
    assert m.read_module_parameter(20095) == m.read_module_parameter(
        "Condition counter actual value"
    )


def test_vmpa2_fb_ems_d2_4_read_channels(test_cpxap):
    m = test_cpxap.modules[5]

    assert m.read_channels() == [
        False,
        False,
        False,
        False,
    ]


def test_vmpa2_fb_ems_d2_4_read_channel(test_cpxap):
    m = test_cpxap.modules[5]

    for i in range(4):
        assert m.read_channel(i) is False


def test_vmpa2_fb_ems_d2_4_write_channels(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_channels([True] * 4)
    time.sleep(0.05)

    assert m.read_channels() == [True] * 4

    m.write_channels([False] * 4)
    time.sleep(0.05)

    assert m.read_channels() == [False] * 4


def test_vmpa2_fb_ems_d2_4_write_channel(test_cpxap):
    m = test_cpxap.modules[5]

    for i in range(4):
        m.write_channel(i, True)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.write_channel(i, False)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa2_fb_ems_d2_4_set_clear_channel(test_cpxap):
    m = test_cpxap.modules[5]

    for i in range(4):
        m.set_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.clear_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa2_fb_ems_d2_4_toggle_channel(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_channels([False] * 4)

    for i in range(4):
        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is True

        m.toggle_channel(i)
        time.sleep(0.05)

        assert m.read_channel(i) is False


def test_vmpa2_fb_ems_d2_4_read_module_parameters(test_cpxap):
    m = test_cpxap.modules[5]
    time.sleep(0.05)

    assert m.read_module_parameter(20026) == m.read_module_parameter(
        "Enable diagnosis of overload short circuit"
    )
    assert m.read_module_parameter(20027) == m.read_module_parameter(
        "Enable diagnosis of open load"
    )
    assert m.read_module_parameter(20033) == m.read_module_parameter(
        "Monitor Vout/Vval"
    )
    assert m.read_module_parameter(20052) == m.read_module_parameter(
        "Behaviour in fail state"
    )
    assert m.read_module_parameter(20094) == m.read_module_parameter(
        "Condition counter set point"
    )
    assert m.read_module_parameter(20095) == m.read_module_parameter(
        "Condition counter actual value"
    )
