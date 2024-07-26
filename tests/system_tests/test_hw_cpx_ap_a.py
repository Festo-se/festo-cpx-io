"""Tests for cpx-ap system"""

import time
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import CpxModule


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.42") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_print_system_information(test_cpxap):
    "test print"
    test_cpxap.print_system_information()


def test_print_system_state(test_cpxap):
    "test print"
    test_cpxap.print_system_state()


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 10


def test_default_timeout(test_cpxap):
    "test timeout"
    reg = test_cpxap.read_reg_data(14000, 2)
    value = int.from_bytes(reg, byteorder="little", signed=False)
    assert value == 100


def test_set_timeout():
    "test timeout"
    with CpxAp(ip_address="172.16.1.41", timeout=0.5) as cpxap:
        reg = cpxap.read_reg_data(14000, 2)
        assert int.from_bytes(reg, byteorder="little", signed=False) == 500


def test_set_timeout_below_100ms():
    "test timeout"
    with CpxAp(ip_address="172.16.1.41", timeout=0.05) as cpxap:
        reg = cpxap.read_reg_data(14000, 2)
        assert int.from_bytes(reg, byteorder="little", signed=False) == 100


def test_read_apdd_information(test_cpxap):

    for i in range(len(test_cpxap.modules)):
        assert test_cpxap.read_apdd_information(i)


def test_read_diagnostic_status(test_cpxap):

    diagnostics = test_cpxap.read_diagnostic_status()
    assert len(diagnostics) == test_cpxap.read_module_count() + 1
    assert all(isinstance(d, CpxAp.Diagnostics) for d in diagnostics)


def test_read_latest_diagnosis_code(test_cpxap):
    assert test_cpxap.read_latest_diagnosis_code() == 0


def test_read_diagnosis_state(test_cpxap):
    assert isinstance(test_cpxap.read_global_diagnosis_state(), dict)
    assert list(test_cpxap.read_global_diagnosis_state().values()) == [False] * 19


def test_read_active_diagnosis_count(test_cpxap):
    assert test_cpxap.read_active_diagnosis_count() == 0


def test_read_latest_diagnosis_index(test_cpxap):
    assert test_cpxap.read_latest_diagnosis_index() is None


def test_module_naming(test_cpxap):
    assert isinstance(test_cpxap.cpx_ap_a_ep_m12, CpxModule)
    test_cpxap.cpx_ap_a_ep_m12.name = "test"
    assert isinstance(test_cpxap.test, CpxModule)


def test_modules(test_cpxap):
    assert all(isinstance(m, CpxModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].output_register == 0  # EP
    assert test_cpxap.modules[1].output_register == 0  # 16di
    assert test_cpxap.modules[2].output_register == 0  # 12Di4Do, adds 1
    assert test_cpxap.modules[3].output_register == 1  # 8Do, adds 1
    assert test_cpxap.modules[4].output_register == 2  # 8Di
    assert test_cpxap.modules[5].output_register == 2  # 4Iol
    assert test_cpxap.modules[6].output_register == 18  # Vabx
    assert test_cpxap.modules[7].output_register == 20  # Vaem
    assert test_cpxap.modules[8].output_register == 22  # Vmpal
    assert test_cpxap.modules[9].output_register == 24  # Vaba

    assert test_cpxap.modules[0].input_register == 5000  # EP
    assert test_cpxap.modules[1].input_register == 5000  # 16Di, adds 1
    assert test_cpxap.modules[2].input_register == 5001  # 12Di4Do, adds 1
    assert test_cpxap.modules[3].input_register == 5002  # 8Do
    assert test_cpxap.modules[4].input_register == 5002  # 8Di, adds 1
    assert test_cpxap.modules[5].input_register == 5003  # 4Iol
    assert test_cpxap.modules[6].input_register == 5021  # Vabx
    assert test_cpxap.modules[7].input_register == 5021  # Vaem
    assert test_cpxap.modules[8].input_register == 5021  # Vmpal
    assert test_cpxap.modules[9].input_register == 5021  # Vaba

    assert test_cpxap.diagnosis_register == 11000  # cpx system global diagnosis
    assert test_cpxap.modules[0].diagnosis_register == 11006  # EP
    assert test_cpxap.modules[1].diagnosis_register == 11012  # 16Di
    assert test_cpxap.modules[2].diagnosis_register == 11018  # 12Di4Do
    assert test_cpxap.modules[3].diagnosis_register == 11024  # 8Do
    assert test_cpxap.modules[4].diagnosis_register == 11030  # 8Di
    assert test_cpxap.modules[5].diagnosis_register == 11036  # 4Iol
    assert test_cpxap.modules[6].diagnosis_register == 11042  # Vabx
    assert test_cpxap.modules[7].diagnosis_register == 11048  # Vaem
    assert test_cpxap.modules[8].diagnosis_register == 11054  # Vmpal
    assert test_cpxap.modules[9].diagnosis_register == 11060  # Vaba


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].input_channels) == 0  # EP
    assert len(test_cpxap.modules[1].input_channels) == 16  # 16di
    assert len(test_cpxap.modules[3].input_channels) == 0  # 8Do
    assert len(test_cpxap.modules[2].input_channels) == 12  # 12Di4Do
    assert len(test_cpxap.modules[4].input_channels) == 8  # 8Di
    assert len(test_cpxap.modules[5].input_channels) == 8  # 4Iol
    assert len(test_cpxap.modules[6].input_channels) == 0  # Vabx
    assert len(test_cpxap.modules[7].input_channels) == 0  # Vaem
    assert len(test_cpxap.modules[8].input_channels) == 0  # Vmpal
    assert len(test_cpxap.modules[9].input_channels) == 0  # Vaba

    assert len(test_cpxap.modules[0].output_channels) == 0  # EP
    assert len(test_cpxap.modules[1].output_channels) == 0  # 16Di
    assert len(test_cpxap.modules[2].output_channels) == 4  # 12Di4Do
    assert len(test_cpxap.modules[3].output_channels) == 8  # 8Do
    assert len(test_cpxap.modules[4].output_channels) == 0  # 8Di
    assert len(test_cpxap.modules[5].output_channels) == 4  # 4Iol
    assert len(test_cpxap.modules[6].output_channels) == 32  # Vabx
    assert len(test_cpxap.modules[7].output_channels) == 24  # Vaem
    assert len(test_cpxap.modules[8].output_channels) == 32  # Vmpal
    assert len(test_cpxap.modules[9].output_channels) == 24  # Vaba

    assert len(test_cpxap.modules[0].inout_channels) == 0  # EP
    assert len(test_cpxap.modules[1].inout_channels) == 0  # 16Di
    assert len(test_cpxap.modules[2].inout_channels) == 0  # 12Di4Do
    assert len(test_cpxap.modules[3].inout_channels) == 0  # 8Do
    assert len(test_cpxap.modules[4].inout_channels) == 0  # 8Di
    assert len(test_cpxap.modules[5].inout_channels) == 4  # 4Iol
    assert len(test_cpxap.modules[6].inout_channels) == 0  # Vabx
    assert len(test_cpxap.modules[7].inout_channels) == 0  # Vaem
    assert len(test_cpxap.modules[8].inout_channels) == 0  # Vmpal
    assert len(test_cpxap.modules[9].inout_channels) == 0  # Vaba


@pytest.mark.parametrize("input_value", list(range(10)))
def test_read_diagnosis_code(test_cpxap, input_value):
    assert test_cpxap.modules[input_value].read_diagnosis_code() == 0
    assert test_cpxap.modules[input_value].read_diagnosis_information() is None


def test_getter(test_cpxap):
    a16di = test_cpxap.modules[1]
    a12di4do = test_cpxap.modules[2]
    a8do = test_cpxap.modules[3]
    a8di = test_cpxap.modules[4]

    assert a16di[0] == a16di.read_channel(0)
    assert a12di4do[0] == a12di4do.read_channel(0)
    assert a8do[0] == a8do.read_channel(0)
    assert a8di[0] == a8di.read_channel(0)


def test_setter(test_cpxap):
    a12di4do = test_cpxap.modules[2]
    a8do = test_cpxap.modules[3]

    a12di4do[0] = True
    time.sleep(0.05)
    # read back the first output channel (it's on index 12)
    assert a12di4do[12] is True

    a8do[0] = True
    time.sleep(0.05)
    assert a8do[0] is True


def test_ep_read_system_parameters(test_cpxap):
    m = test_cpxap.modules[0]
    param = m.read_system_parameters()

    assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.42"
    assert param.active_subnet_mask == "255.255.255.0"
    assert param.active_gateway_address == "0.0.0.0"
    assert param.mac_address == "00:0e:f0:8e:ae:9e"
    assert param.setup_monitoring_load_supply == 1


def test_ep_parameter_read(test_cpxap):
    m = test_cpxap.modules[0]
    assert m.read_module_parameter(12000) == m.read_module_parameter("DHCP enable")
    assert m.read_module_parameter(12001) == m.read_module_parameter("IP address")
    assert m.read_module_parameter(12002) == m.read_module_parameter("Subnet mask")
    assert m.read_module_parameter(12003) == m.read_module_parameter("Gateway address")
    assert m.read_module_parameter(12004) == m.read_module_parameter(
        "Active IP address"
    )
    assert m.read_module_parameter(12005) == m.read_module_parameter(
        "Active subnet mask"
    )
    assert m.read_module_parameter(12006) == m.read_module_parameter(
        "Active gateway address"
    )
    assert m.read_module_parameter(12007) == m.read_module_parameter("MAC address")
    assert m.read_module_parameter(20022) == m.read_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC"
    )
    assert m.read_module_parameter(20118) == m.read_module_parameter(
        "Application specific Tag"
    )
    assert m.read_module_parameter(20207) == m.read_module_parameter("Location Tag")


def test_ep_parameter_write(test_cpxap):
    m = test_cpxap.modules[0]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1


def test_ep_parameter_rw_strings(test_cpxap):
    m = test_cpxap.modules[0]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0
    assert m.read_module_parameter(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2
    assert m.read_module_parameter(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, undervoltage diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1
    assert (
        m.read_module_parameter(20022)
        == "Load supply monitoring active, undervoltage diagnosis suppressed in case of switch-off"
    )


def test_16Di_read_channels(test_cpxap):
    m = test_cpxap.modules[1]
    assert m.read_channels() == [False] * 16


def test_16Di_read_channel(test_cpxap):
    m = test_cpxap.modules[1]
    for i in range(16):
        assert m.read_channel(i) is False


def test_16Di_parameter_write(test_cpxap):
    m = test_cpxap.modules[1]

    m.write_module_parameter(20014, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0

    m.write_module_parameter(20014, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2

    m.write_module_parameter(20014, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3

    m.write_module_parameter(20014, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1


def test_16Di_parameter_rw_strings(test_cpxap):
    m = test_cpxap.modules[1]

    m.write_module_parameter("Input Debounce Time", "0.1ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0
    assert m.read_module_parameter(20014) == "0.1ms"

    m.write_module_parameter("Input Debounce Time", "10ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2
    assert m.read_module_parameter(20014) == "10ms"

    m.write_module_parameter("Input Debounce Time", "20ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3
    assert m.read_module_parameter(20014) == "20ms"

    m.write_module_parameter("Input Debounce Time", "3ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1
    assert m.read_module_parameter(20014) == "3ms"


def test_12Di4Do(test_cpxap):
    m = test_cpxap.modules[2]
    assert m.read_channels() == [False] * 16

    data = [True, False, True, False]
    m.write_channels(data)
    time.sleep(0.05)
    assert m.read_channels()[:12] == [False] * 12
    assert m.read_channels()[12:] == data

    data = [False, True, False, True]
    m.write_channels(data)
    time.sleep(0.05)
    assert m.read_channels()[:12] == [False] * 12
    assert m.read_channels()[12:] == data

    m.write_channels([False, False, False, False])

    m.set_channel(0)
    time.sleep(0.05)
    assert m.read_channel(0, outputs_only=True) is True
    assert m.read_channel(12) is True

    m.clear_channel(0)
    time.sleep(0.05)
    assert m.read_channel(0, outputs_only=True) is False
    assert m.read_channel(12) is False

    m.toggle_channel(0)
    time.sleep(0.05)
    assert m.read_channel(0, outputs_only=True) is True
    assert m.read_channel(12) is True

    m.clear_channel(0)


def test_12Di4Do_channel_out_of_range(test_cpxap):
    m = test_cpxap.modules[2]

    with pytest.raises(IndexError):
        m.set_channel(4)

    with pytest.raises(IndexError):
        m.clear_channel(4)

    with pytest.raises(IndexError):
        m.toggle_channel(4)


def test_12Di4Do_parameter_write_debounce(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20014, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0

    m.write_module_parameter(20014, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2

    m.write_module_parameter(20014, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3

    m.write_module_parameter(20014, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1


def test_12Di4Do_parameter_rw_strings_debounce(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter("Input Debounce Time", "0.1ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0
    assert m.read_module_parameter(20014) == "0.1ms"

    m.write_module_parameter("Input Debounce Time", "10ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2
    assert m.read_module_parameter(20014) == "10ms"

    m.write_module_parameter("Input Debounce Time", "20ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3
    assert m.read_module_parameter(20014) == "20ms"

    m.write_module_parameter("Input Debounce Time", "3ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1
    assert m.read_module_parameter(20014) == "3ms"


def test_12Di4Do_parameter_write_load(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1


def test_12Di4Do_parameter_rw_strings_load(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0
    assert m.read_module_parameter(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2
    assert m.read_module_parameter(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1
    assert (
        m.read_module_parameter(20022)
        == "Load supply monitoring active, diagnosis suppressed in case of switch-off"
    )


def test_12Di4Do_parameter_write_failstate(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20052, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 0

    m.write_module_parameter(20052, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 1


def test_12Di4Do_parameter_rw_strings_failstate(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter("Behaviour in fail state", "Reset Outputs")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 0
    assert m.read_module_parameter(20052) == "Reset Outputs"

    m.write_module_parameter("Behaviour in fail state", "Hold last state")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 1
    assert m.read_module_parameter(20052) == "Hold last state"


def test_8do(test_cpxap):
    m = test_cpxap.modules[3]

    for i in range(8):
        assert m.read_channel(i) is False
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        m.clear_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True


def test_8Do_parameter_write_failstate(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_module_parameter(20052, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 0

    m.write_module_parameter(20052, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 1


def test_8Do_parameter_rw_strings_failstate(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_module_parameter("Behaviour in fail state", "Reset Outputs")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 0
    assert m.read_module_parameter(20052) == "Reset Outputs"

    m.write_module_parameter("Behaviour in fail state", "Hold last state")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20052]) == 1
    assert m.read_module_parameter(20052) == "Hold last state"


def test_8Do_parameter_write_load(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1


def test_8Do_parameter_rw_strings_load(test_cpxap):
    m = test_cpxap.modules[3]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0
    assert m.read_module_parameter(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2
    assert m.read_module_parameter(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1
    assert (
        m.read_module_parameter(20022)
        == "Load supply monitoring active, diagnosis suppressed in case of switch-off"
    )


def test_8di_read_channels(test_cpxap):
    m = test_cpxap.modules[4]
    assert m.read_channels() == [False] * 8


def test_8di_read_channel(test_cpxap):
    m = test_cpxap.modules[4]
    for i in range(8):
        assert m.read_channel(i) is False


def test_8Di_parameter_write_debounce(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter(20014, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0

    m.write_module_parameter(20014, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2

    m.write_module_parameter(20014, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3

    m.write_module_parameter(20014, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1


def test_8Di_parameter_rw_strings_debounce(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter("Input Debounce Time", "0.1ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 0
    assert m.read_module_parameter(20014) == "0.1ms"

    m.write_module_parameter("Input Debounce Time", "10ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 2
    assert m.read_module_parameter(20014) == "10ms"

    m.write_module_parameter("Input Debounce Time", "20ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 3
    assert m.read_module_parameter(20014) == "20ms"

    m.write_module_parameter("Input Debounce Time", "3ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20014]) == 1
    assert m.read_module_parameter(20014) == "3ms"


def test_4iol_read_channels(test_cpxap):
    m = test_cpxap.modules[5]
    test = m.read_channels()
    assert m.read_channels() == [b"\x00\x00\x00\x00\x00\x00\x00\x00"] * 4


def test_4iol_read_channel(test_cpxap):
    m = test_cpxap.modules[5]
    for i in range(4):
        assert (
            m.read_channel(
                i,
            )
            == b""
        )
        assert m.read_channel(i, full_size=True) == b"\x00\x00\x00\x00\x00\x00\x00\x00"


def test_4iol_parameter_write_load(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1


def test_4iol_parameter_rw_strings_load(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 0
    assert m.read_module_parameter(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 2
    assert m.read_module_parameter(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20022]) == 1
    assert (
        m.read_module_parameter(20022)
        == "Load supply monitoring active, diagnosis suppressed in case of switch-off"
    )


def test_4iol_parameter_write_lost(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter(20050, False)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050]) is False

    m.write_module_parameter(20050, True)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050]) is True


def test_4iol_parameter_rw_strings_lost(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", False)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050], 0) is False
    assert m.read_module_parameter(20050) == [False, False, False, False]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True, [1, 2])
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050], 0) is False
    assert m.read_module_parameter(20050) == [False, True, True, False]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050], 0) is False
    assert m.read_module_parameter(20050) == [False, True, True, True]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20050], 0) is True
    assert m.read_module_parameter(20050) == [True, True, True, True]


def test_4iol_parameter_write_load_supply_enable(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter(20086, False)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086]) is False

    m.write_module_parameter(20086, True)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086]) is True


def test_4iol_parameter_rw_strings_load_supply_enable(test_cpxap):
    m = test_cpxap.modules[5]

    m.write_module_parameter("Enable of load supply", False)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086], 0) is False
    assert m.read_module_parameter(20086) == [False, False, False, False]

    m.write_module_parameter("Enable of load supply", True, [1, 2])
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086], 0) is False
    assert m.read_module_parameter(20086) == [False, True, True, False]

    m.write_module_parameter("Enable of load supply", True, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086], 0) is False
    assert m.read_module_parameter(20086) == [False, True, True, True]

    m.write_module_parameter("Enable of load supply", True)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.parameter_dict[20086], 0) is True
    assert m.read_module_parameter(20086) == [True, True, True, True]


def test_4iol_other_parameters_rw(test_cpxap):
    m = test_cpxap.modules[5]

    assert m.read_module_parameter("Nominal Cycle Time") == m.read_module_parameter(
        20049
    )
    assert m.read_module_parameter("Nominal Vendor ID") == m.read_module_parameter(
        20073
    )
    assert m.read_module_parameter("DeviceID") == m.read_module_parameter(20080)
    assert m.read_module_parameter("Validation & Backup") == m.read_module_parameter(
        20072
    )
    assert m.read_module_parameter("Port Mode") == m.read_module_parameter(20071)
    assert m.read_module_parameter(
        "Port status information"
    ) == m.read_module_parameter(20074)
    assert m.read_module_parameter("Revision ID") == m.read_module_parameter(20075)
    assert m.read_module_parameter("Port transmission rate") == m.read_module_parameter(
        20076
    )
    assert m.read_module_parameter(
        "Actual cycle time in 100 us"
    ) == m.read_module_parameter(20077)
    assert m.read_module_parameter("InputDataLength") == m.read_module_parameter(20108)
    assert m.read_module_parameter("OutputDataLength") == m.read_module_parameter(20109)
    assert m.read_module_parameter("Actual VendorID") == m.read_module_parameter(20078)
    assert m.read_module_parameter("Actual DeviceID") == m.read_module_parameter(20079)


def test_vabx_read_channels(test_cpxap):
    m = test_cpxap.modules[6]

    assert m.read_channels() == [False] * 32


def test_vabx_read_channel(test_cpxap):
    m = test_cpxap.modules[6]

    for i in range(32):
        assert m.read_channel(i) is False


def test_vabx_write(test_cpxap):
    m = test_cpxap.modules[6]

    for i in range(32):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vabx_set_clear_toggle(test_cpxap):
    m = test_cpxap.modules[6]

    for i in range(32):
        m.set_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.clear_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vabx_parameters(test_cpxap):
    m = test_cpxap.modules[6]
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


def test_vaem_read_channels(test_cpxap):
    m = test_cpxap.modules[7]

    assert m.read_channels() == [False] * 24


def test_vaem_read_channel(test_cpxap):
    m = test_cpxap.modules[7]

    for i in range(24):
        assert m.read_channel(i) is False


def test_vaem_write(test_cpxap):
    m = test_cpxap.modules[7]

    for i in range(24):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vaem_set_clear_toggle(test_cpxap):
    m = test_cpxap.modules[7]

    for i in range(24):
        m.set_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.clear_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vaem_parameters(test_cpxap):
    m = test_cpxap.modules[7]
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


def test_vmpal_read_channels(test_cpxap):
    m = test_cpxap.modules[8]

    assert m.read_channels() == [False] * 32


def test_vmpal_read_channel(test_cpxap):
    m = test_cpxap.modules[8]

    for i in range(32):
        assert m.read_channel(i) is False


def test_vmpal_write(test_cpxap):
    m = test_cpxap.modules[8]

    for i in range(32):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vmpal_set_clear_toggle(test_cpxap):
    m = test_cpxap.modules[8]

    for i in range(32):
        m.set_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.clear_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vmpal_parameters(test_cpxap):
    m = test_cpxap.modules[8]
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


def test_vaba_read_channels(test_cpxap):
    m = test_cpxap.modules[9]

    assert m.read_channels() == [False] * 24


def test_vaba_read_channel(test_cpxap):
    m = test_cpxap.modules[9]

    for i in range(24):
        assert m.read_channel(i) is False


def test_vaba_write(test_cpxap):
    m = test_cpxap.modules[9]

    for i in range(24):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vaba_set_clear_toggle(test_cpxap):
    m = test_cpxap.modules[9]

    for i in range(24):
        m.set_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.clear_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        m.toggle_channel(i)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vaba_parameters(test_cpxap):
    m = test_cpxap.modules[9]
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
