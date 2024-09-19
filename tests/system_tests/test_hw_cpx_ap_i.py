"""Tests for cpx-ap system"""

import time
import struct
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.41") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 7


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
    time.sleep(0.05)
    assert test_cpxap.read_latest_diagnosis_code() == 0


def test_read_diagnosis_state(test_cpxap):
    assert isinstance(test_cpxap.read_global_diagnosis_state(), dict)
    assert list(test_cpxap.read_global_diagnosis_state().values()) == [False] * 19


def test_read_active_diagnosis_count(test_cpxap):
    assert test_cpxap.read_active_diagnosis_count() == 0


def test_read_latest_diagnosis_index(test_cpxap):
    assert test_cpxap.read_latest_diagnosis_index() is None


def test_module_naming(test_cpxap):
    assert isinstance(test_cpxap.cpx_ap_i_ep_m12, ApModule)
    test_cpxap.cpx_ap_i_ep_m12.name = "test"
    assert isinstance(test_cpxap.test, ApModule)


def test_modules(test_cpxap):
    assert all(isinstance(m, ApModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i

    assert test_cpxap.modules[0].system_entry_registers.outputs == 0  # EP
    assert test_cpxap.modules[1].system_entry_registers.outputs == 0  # 8DI
    assert test_cpxap.modules[2].system_entry_registers.outputs == 0  # 4DI4DO, adds 1
    assert test_cpxap.modules[3].system_entry_registers.outputs == 1  # 4AIUI
    assert test_cpxap.modules[4].system_entry_registers.outputs == 1  # 4IOL, adds 16
    assert test_cpxap.modules[5].system_entry_registers.outputs == 17  # VABX, adds 2
    assert test_cpxap.modules[6].system_entry_registers.outputs == 19  # 4Di

    assert test_cpxap.modules[0].system_entry_registers.inputs == 5000  # EP
    assert test_cpxap.modules[1].system_entry_registers.inputs == 5000  # 8DI, adds 1
    assert test_cpxap.modules[2].system_entry_registers.inputs == 5001  # 4DI4DO, adds 1
    assert test_cpxap.modules[3].system_entry_registers.inputs == 5002  # 4AIUI, adds 4
    assert test_cpxap.modules[4].system_entry_registers.inputs == 5006  # 4IOL, adds 18
    assert test_cpxap.modules[5].system_entry_registers.inputs == 5024  # VABX
    assert test_cpxap.modules[6].system_entry_registers.inputs == 5024  # 4Di

    assert test_cpxap.global_diagnosis_register == 11000  # cpx system global diagnosis
    assert test_cpxap.modules[0].system_entry_registers.diagnosis == 11006  # EP
    assert test_cpxap.modules[1].system_entry_registers.diagnosis == 11012  # 8DI
    assert test_cpxap.modules[2].system_entry_registers.diagnosis == 11018  # 4Di4Do
    assert test_cpxap.modules[3].system_entry_registers.diagnosis == 11024  # 4AIUI
    assert test_cpxap.modules[4].system_entry_registers.diagnosis == 11030  # 4IOL
    assert test_cpxap.modules[5].system_entry_registers.diagnosis == 11036  # VABX
    assert test_cpxap.modules[6].system_entry_registers.diagnosis == 11042  # 4Di


def test_modules_channel_length(test_cpxap):

    assert len(test_cpxap.modules[0].channels.inputs) == 0  # EP
    assert len(test_cpxap.modules[1].channels.inputs) == 8  # 8DI
    assert len(test_cpxap.modules[2].channels.inputs) == 4  # 4DI4DO
    assert len(test_cpxap.modules[3].channels.inputs) == 4  # 4AIUI
    assert len(test_cpxap.modules[4].channels.inputs) == 8  # 4IOL
    assert len(test_cpxap.modules[5].channels.inputs) == 0  # VABX
    assert len(test_cpxap.modules[6].channels.inputs) == 4  # 4Di

    assert len(test_cpxap.modules[0].channels.outputs) == 0  # EP
    assert len(test_cpxap.modules[1].channels.outputs) == 0  # 8DI
    assert len(test_cpxap.modules[2].channels.outputs) == 4  # 4DI4DO
    assert len(test_cpxap.modules[3].channels.outputs) == 0  # 4AIUI
    assert len(test_cpxap.modules[4].channels.outputs) == 4  # 4IOL
    assert len(test_cpxap.modules[5].channels.outputs) == 32  # VABX
    assert len(test_cpxap.modules[6].channels.outputs) == 0  # 4Di

    assert len(test_cpxap.modules[0].channels.inouts) == 0  # EP
    assert len(test_cpxap.modules[1].channels.inouts) == 0  # 8DI
    assert len(test_cpxap.modules[2].channels.inouts) == 0  # 4DI4DO
    assert len(test_cpxap.modules[3].channels.inouts) == 0  # 4AIUI
    assert len(test_cpxap.modules[4].channels.inouts) == 4  # 4IOL
    assert len(test_cpxap.modules[5].channels.inouts) == 0  # VABX
    assert len(test_cpxap.modules[6].channels.inouts) == 0  # 4Di


@pytest.mark.parametrize("input_value", list(range(7)))
def test_read_diagnosis_code(test_cpxap, input_value):
    assert test_cpxap.modules[input_value].read_diagnosis_code() == 0
    assert test_cpxap.modules[input_value].read_diagnosis_information() is None


# After running this test, you must restart (power off/on) the system to clear the
# error codes so that the other tests can run

"""
def test_read_diagnosis_code_active_iolink(test_cpxap):
    module = test_cpxap.modules[4]
    module.write_module_parameter("Port Mode", "IOL_AUTOSTART", instances=3)
    module.write_module_parameter("Validation & Backup", 2, instances=3)
    time.sleep(0.08)
    assert module.read_diagnosis_information() == ApModule.ModuleDiagnosis(
        description="No Device (communication)",
        diagnosis_id="0x080A01A9",
        guideline="- Check if IO-Link device is connected",
        name="No Device",
    )
    module.write_module_parameter("Port Mode", "DEACTIVATED")
    module.write_module_parameter("Validation & Backup", 0)
    assert test_cpxap.read_global_diagnosis_state()["Communication"] is True
"""


def test_getter(test_cpxap):
    i8di = test_cpxap.modules[1]
    i4di4do = test_cpxap.modules[2]
    i4di = test_cpxap.modules[6]

    assert i8di[0] == i8di.read_channel(0)
    assert i4di4do[0] == i4di4do.read_channel(0)
    assert i4di[0] == i4di.read_channel(0)


def test_setter(test_cpxap):
    i4di4do = test_cpxap.modules[2]

    i4di4do[0] = True
    time.sleep(0.05)
    # read back the first output channel (it's on index 4)
    assert i4di4do[4] is True


def test_ep_read_system_parameters(test_cpxap):
    m = test_cpxap.modules[0]
    param = m.read_system_parameters()

    # assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.41"
    assert param.active_subnet_mask == "255.255.255.0"
    # assert param.active_gateway_address == "0.0.0.0"
    assert param.mac_address == "00:0e:f0:7d:3b:15"
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
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1


def test_ep_parameter_rw_strings(test_cpxap):
    m = test_cpxap.modules[0]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, undervoltage diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1
    assert (
        m.read_module_parameter_enum_str(20022)
        == "Load supply monitoring active, undervoltage diagnosis suppressed in case of switch-off"
    )


def test_8Di_read_channels(test_cpxap):
    m = test_cpxap.modules[1]
    assert m.read_channels() == [False] * 8


def test_8Di_read_channel(test_cpxap):
    m = test_cpxap.modules[1]
    for i in range(8):
        assert m.read_channel(i) is False


def test_8Di_parameter_write(test_cpxap):
    m = test_cpxap.modules[1]

    m.write_module_parameter(20014, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 0

    m.write_module_parameter(20014, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 2

    m.write_module_parameter(20014, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 3

    m.write_module_parameter(20014, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 1


def test_8Di_parameter_rw_strings(test_cpxap):
    m = test_cpxap.modules[1]

    m.write_module_parameter("Input Debounce Time", "0.1ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 0
    assert m.read_module_parameter_enum_str(20014) == "0.1ms"

    m.write_module_parameter("Input Debounce Time", "10ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 2
    assert m.read_module_parameter_enum_str(20014) == "10ms"

    m.write_module_parameter("Input Debounce Time", "20ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 3
    assert m.read_module_parameter_enum_str(20014) == "20ms"

    m.write_module_parameter("Input Debounce Time", "3ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 1
    assert m.read_module_parameter_enum_str(20014) == "3ms"


def test_4Di4Do(test_cpxap):
    m = test_cpxap.modules[2]
    assert m.read_channels() == [False] * 8

    data = [True, False, True, False]
    m.write_channels(data)
    time.sleep(0.05)
    assert m.read_channels()[:4] == [False] * 4
    assert m.read_channels()[4:] == data

    data = [False, True, False, True]
    m.write_channels(data)
    time.sleep(0.05)
    assert m.read_channels()[:4] == [False] * 4
    assert m.read_channels()[4:] == data

    m.write_channels([False, False, False, False])

    m.set_channel(0)
    time.sleep(0.05)
    assert m.read_output_channel(0) is True
    assert m.read_channel(4) is True

    m.clear_channel(0)
    time.sleep(0.05)
    assert m.read_output_channel(0) is False
    assert m.read_channel(4) is False

    m.toggle_channel(0)
    time.sleep(0.05)
    assert m.read_output_channel(0) is True
    assert m.read_channel(4) is True

    m.clear_channel(0)


def test_4Di4Do_parameter_write_debounce(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20014, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 0

    m.write_module_parameter(20014, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 2

    m.write_module_parameter(20014, 3)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 3

    m.write_module_parameter(20014, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 1


def test_4Di4Do_parameter_rw_strings_debounce(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter("Input Debounce Time", "0.1ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 0
    assert m.read_module_parameter_enum_str(20014) == "0.1ms"

    m.write_module_parameter("Input Debounce Time", "10ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 2
    assert m.read_module_parameter_enum_str(20014) == "10ms"

    m.write_module_parameter("Input Debounce Time", "20ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 3
    assert m.read_module_parameter_enum_str(20014) == "20ms"

    m.write_module_parameter("Input Debounce Time", "3ms")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20014]) == 1
    assert m.read_module_parameter_enum_str(20014) == "3ms"


def test_4Di4Do_parameter_write_load(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1


def test_4Di4Do_parameter_rw_strings_load(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1
    assert (
        m.read_module_parameter_enum_str(20022)
        == "Load supply monitoring active, diagnosis suppressed in case of switch-off"
    )


def test_4Di4Do_parameter_write_failstate(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter(20052, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20052]) == 0

    m.write_module_parameter(20052, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20052]) == 1


def test_4Di4Do_parameter_rw_strings_failstate(test_cpxap):
    m = test_cpxap.modules[2]

    m.write_module_parameter("Behaviour in fail state", "Reset Outputs")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20052]) == 0
    assert m.read_module_parameter_enum_str(20052) == "Reset Outputs"

    m.write_module_parameter("Behaviour in fail state", "Hold last state")
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20052]) == 1
    assert m.read_module_parameter_enum_str(20052) == "Hold last state"


def test_4AiUI_None(test_cpxap):
    m = test_cpxap.modules[3]
    assert len(m.read_channels()) == 4


def test_4AiUI_analog5V0_CH1(test_cpxap):
    # this depends on external 5.0 Volts at input channel 1
    m = test_cpxap.modules[3]
    m.write_module_parameter("Signalrange", "0 .. 10 V", 1)
    time.sleep(0.05)
    m.write_module_parameter("Enable linear scaling", False, 1)
    time.sleep(0.05)
    assert 15900 < test_cpxap.modules[3].read_channel(1) < 16100


def test_4AiUI_analog5V0_CH1_with_scaling(test_cpxap):
    # this depends on external 5.0 Volts at input channel 1
    m = test_cpxap.modules[3]
    m.write_module_parameter("Signalrange", "0 .. 10 V", 1)
    time.sleep(0.05)
    m.write_module_parameter("Upper threshold value", 10000, 1)
    time.sleep(0.05)
    m.write_module_parameter("Lower threshold value", 0, 1)
    time.sleep(0.05)
    m.write_module_parameter("Enable linear scaling", True)

    assert 4900 < m.read_channel(1) < 5100

    m.write_module_parameter("Upper threshold value", 32767)
    m.write_module_parameter("Lower threshold value", -32768)
    m.write_module_parameter("Enable linear scaling", False)


def test_4AiUI_parameters(test_cpxap):
    m = test_cpxap.modules[3]
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


def test_4iol_sdas(test_cpxap):
    m = test_cpxap.modules[4]
    sdas_channel = 0

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", sdas_channel)

    time.sleep(0.05)

    # example SDAS-MHS on port 0
    param = m.read_fieldbus_parameters()

    while param[sdas_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    sdas_data = m.read_channel(sdas_channel)
    assert len(sdas_data) == 2

    process_data = int.from_bytes(sdas_data, byteorder="big")

    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    assert 0 <= pdv <= 4095

    assert m[sdas_channel] == m.read_channel(sdas_channel)

    m.write_module_parameter("Port Mode", "DEACTIVATED", sdas_channel)


def test_4iol_sdas_full(test_cpxap):
    m = test_cpxap.modules[4]
    sdas_channel = 0

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", sdas_channel)

    time.sleep(0.05)

    # example SDAS-MHS on port 0
    param = m.read_fieldbus_parameters()

    while param[sdas_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    sdas_data = m.read_channel(sdas_channel, full_size=True)
    assert len(sdas_data) == 8

    sdas_data = sdas_data[:2]  # only two bytes relevant

    process_data = int.from_bytes(sdas_data, byteorder="big")

    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    assert 0 <= pdv <= 4095

    assert m[sdas_channel] == m.read_channel(sdas_channel)

    m.write_module_parameter("Port Mode", "DEACTIVATED", sdas_channel)

    while param[sdas_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ehps(test_cpxap):
    m = test_cpxap.modules[4]

    time.sleep(0.05)

    def read_process_data_in(module, channel):
        # ehps provides 3 x 16bit "process data in".
        data = module.read_channel(channel)
        # unpack it to 3x 16 bit uint
        ehps_data = struct.unpack(">HHH", data)

        process_data_in = {}

        process_data_in["Error"] = bool((ehps_data[0] >> 15) & 1)
        process_data_in["DirectionCloseFlag"] = bool((ehps_data[0] >> 14) & 1)
        process_data_in["DirectionOpenFlag"] = bool((ehps_data[0] >> 13) & 1)
        process_data_in["LatchDataOk"] = bool((ehps_data[0] >> 12) & 1)
        process_data_in["UndefinedPositionFlag"] = bool((ehps_data[0] >> 11) & 1)
        process_data_in["ClosedPositionFlag"] = bool((ehps_data[0] >> 10) & 1)
        process_data_in["GrippedPositionFlag"] = bool((ehps_data[0] >> 9) & 1)
        process_data_in["OpenedPositionFlag"] = bool((ehps_data[0] >> 8) & 1)

        process_data_in["Ready"] = bool((ehps_data[0] >> 6) & 1)

        process_data_in["ErrorNumber"] = ehps_data[1]
        process_data_in["ActualPosition"] = ehps_data[2]

        return process_data_in

    # example EHPS-20-A-LK on port 1
    ehps_channel = 1

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ehps_channel)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ehps_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    # wait for ready
    process_data_in = read_process_data_in(m, ehps_channel)
    while not process_data_in["Ready"]:
        process_data_in = read_process_data_in(m, ehps_channel)

    # demo of process data out
    control_word_msb = 0x00
    control_word_lsb = 0x01  # latch
    gripping_mode = 0x46  # universal
    workpiece_no = 0x00
    gripping_position = 0x03E8
    gripping_force = 0x03  # ca. 85%
    gripping_tolerance = 0x0A

    data = [
        control_word_lsb + (control_word_msb << 8),
        workpiece_no + (gripping_mode << 8),
        gripping_position,
        gripping_tolerance + (gripping_force << 8),
    ]

    # init
    # this pack is not good, just for testing I can use legacy code
    process_data_out = struct.pack(">HHHH", *data)
    m.write_channel(ehps_channel, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    data[0] = 0x0100
    process_data_out = struct.pack(">HHHH", *data)
    m.write_channel(ehps_channel, process_data_out)

    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(m, ehps_channel)
        time.sleep(0.05)

    # Close command 0x 0200
    data[0] = 0x0200
    process_data_out = struct.pack(">HHHH", *data)
    m.write_channel(ehps_channel, process_data_out)

    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(m, ehps_channel)
        time.sleep(0.05)

    assert process_data_in["Error"] is False
    assert process_data_in["ClosedPositionFlag"] is True
    assert process_data_in["OpenedPositionFlag"] is False

    m.write_module_parameter("Port Mode", "DEACTIVATED", ehps_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ehps_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ethrottle(test_cpxap):
    m = test_cpxap.modules[4]

    def read_process_data_in(module, channel):
        data = module.read_channel(channel)
        # register order is [msb, ... , ... , lsb]
        # this unpack is not good, just for testing I can use legacy code
        data = struct.unpack(">Q", data)[0]
        process_input_data = {
            "Actual Position": data,
            "Homing Valid": bool(data & 0b1000),
            "Motion Complete": bool(data & 0b100),
            "Proximity Switch": bool(data & 0b10),
            "Reduced Speed": bool(data & 0b1000),
        }
        return process_input_data

    ethrottle_channel = 2

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ethrottle_channel)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    process_input_data = read_process_data_in(m, ethrottle_channel)

    if not process_input_data["Homing Valid"]:
        process_output_data = [1]
        process_output_data = struct.pack(">Q", *process_output_data)
        m.write_channel(ethrottle_channel, process_output_data)

        while not process_input_data["Homing Valid"]:
            process_input_data = read_process_data_in(m, ethrottle_channel)

    process_output_data = [0xF00]  # setpoint 0xF00
    process_output_data = struct.pack(">Q", *process_output_data)
    m.write_channel(ethrottle_channel, process_output_data)

    time.sleep(0.1)

    while not process_input_data["Motion Complete"]:
        process_input_data = read_process_data_in(m, ethrottle_channel)

    m.write_module_parameter("Port Mode", "DEACTIVATED", ethrottle_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ethrottle_isdu_read(test_cpxap):
    m = test_cpxap.modules[4]
    ethrottle_channel = 2

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ethrottle_channel)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    assert (m.read_isdu(ethrottle_channel, 16, 0)[:5]) == b"Festo"

    m.write_module_parameter("Port Mode", "DEACTIVATED", ethrottle_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ethrottle_isdu_write_1byte(test_cpxap):
    m = test_cpxap.modules[4]
    ethrottle_channel = 2

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ethrottle_channel)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    function_tag_idx = 25
    # write something different first
    m.write_isdu(b"\x12\x34", ethrottle_channel, function_tag_idx, 0)
    time.sleep(0.05)
    m.write_isdu(b"\xCA", ethrottle_channel, function_tag_idx, 0)

    assert m.read_isdu(ethrottle_channel, function_tag_idx, 0)[:2] == b"\xCA\x00"

    m.write_module_parameter("Port Mode", "DEACTIVATED", ethrottle_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ethrottle_isdu_write_2byte(test_cpxap):
    m = test_cpxap.modules[4]
    ethrottle_channel = 2

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ethrottle_channel)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    function_tag_idx = 25
    m.write_isdu(b"\x06\x07", ethrottle_channel, function_tag_idx, 0)

    assert m.read_isdu(ethrottle_channel, function_tag_idx, 0)[:2] == b"\x06\x07"

    m.write_module_parameter("Port Mode", "DEACTIVATED", ethrottle_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_ethrottle_isdu_write_4byte(test_cpxap):
    m = test_cpxap.modules[4]
    ethrottle_channel = 2

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", ethrottle_channel)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    function_tag_idx = 25
    m.write_isdu(b"\x01\x02\x03\x04", ethrottle_channel, function_tag_idx, 0)

    assert (
        m.read_isdu(ethrottle_channel, function_tag_idx, 0)[:4] == b"\x01\x02\x03\x04"
    )

    m.write_module_parameter("Port Mode", "DEACTIVATED", ethrottle_channel)
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[ethrottle_channel]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_read_pqi(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter("Port Mode", "IOL_AUTOSTART", 0)
    m.write_module_parameter("Port Mode", "DEACTIVATED", 1)

    time.sleep(0.05)

    # wait for operate
    param = m.read_fieldbus_parameters()
    while param[0]["Port status information"] != "OPERATE":
        param = m.read_fieldbus_parameters()

    pqi = m.read_pqi()
    assert pqi[0]["Port Qualifier"] == "input data is valid"
    assert pqi[1]["Port Qualifier"] == "input data is invalid"

    m.write_module_parameter("Port Mode", "DEACTIVATED")
    # wait for inactive
    param = m.read_fieldbus_parameters()
    while param[0]["Port status information"] != "DEACTIVATED":
        param = m.read_fieldbus_parameters()


def test_4iol_parameter_write_load(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter(20022, 0)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0

    m.write_module_parameter(20022, 2)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2

    m.write_module_parameter(20022, 1)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1


def test_4iol_parameter_rw_strings_load(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring inactive"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 0
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring inactive"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC", "Load supply monitoring active"
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 2
    assert m.read_module_parameter_enum_str(20022) == "Load supply monitoring active"

    m.write_module_parameter(
        "Setup monitoring load supply (PL) 24 V DC",
        "Load supply monitoring active, diagnosis suppressed in case of switch-off",
    )
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20022]) == 1
    assert (
        m.read_module_parameter_enum_str(20022)
        == "Load supply monitoring active, diagnosis suppressed in case of switch-off"
    )


def test_4iol_parameter_write_lost(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter(20050, False)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20050]) is False

    m.write_module_parameter(20050, True)
    time.sleep(0.05)
    assert m.base.read_parameter(m.position, m.module_dicts.parameters[20050]) is True


def test_4iol_parameter_rw_strings_lost(test_cpxap):
    m = test_cpxap.modules[4]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", False)
    time.sleep(0.05)
    assert (
        m.base.read_parameter(m.position, m.module_dicts.parameters[20050], 0) is False
    )
    assert m.read_module_parameter(20050) == [False, False, False, False]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True, [1, 2])
    time.sleep(0.05)
    assert (
        m.base.read_parameter(m.position, m.module_dicts.parameters[20050], 0) is False
    )
    assert m.read_module_parameter(20050) == [False, True, True, False]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True, 3)
    time.sleep(0.05)
    assert (
        m.base.read_parameter(m.position, m.module_dicts.parameters[20050], 0) is False
    )
    assert m.read_module_parameter(20050) == [False, True, True, True]

    m.write_module_parameter("Enable diagnosis of IO-Link device lost", True)
    time.sleep(0.05)
    assert (
        m.base.read_parameter(m.position, m.module_dicts.parameters[20050], 0) is True
    )
    assert m.read_module_parameter(20050) == [True, True, True, True]


def test_4iol_other_parameters_rw(test_cpxap):
    m = test_cpxap.modules[4]

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
    m = test_cpxap.modules[5]

    assert m.read_channels() == [False] * 32


def test_vabx_read_channel(test_cpxap):
    m = test_cpxap.modules[5]

    for i in range(32):
        assert m.read_channel(i) is False


def test_vabx_write(test_cpxap):
    m = test_cpxap.modules[5]

    for i in range(32):
        m.write_channel(i, True)
        time.sleep(0.05)
        assert m.read_channel(i) is True
        time.sleep(0.05)
        m.write_channel(i, False)
        time.sleep(0.05)
        assert m.read_channel(i) is False


def test_vabx_set_clear_toggle(test_cpxap):
    m = test_cpxap.modules[5]

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
    m = test_cpxap.modules[5]
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
