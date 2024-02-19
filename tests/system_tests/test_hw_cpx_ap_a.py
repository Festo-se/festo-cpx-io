"""Tests for cpx-ap system"""

import time
import struct
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.ap16di import CpxAp16Di
from cpx_io.cpx_system.cpx_ap.ap12di4do import CpxAp12Di4Do
from cpx_io.cpx_system.cpx_ap.ap8do import CpxAp8Do
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.42") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 6


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


def test_read_module_information(test_cpxap):
    modules = []
    time.sleep(0.05)
    cnt = test_cpxap.read_module_count()
    for i in range(cnt):
        modules.append(test_cpxap.read_module_information(i))
    assert modules[0].module_code in CpxApEp.module_codes


def test_read_diagnostic_status(test_cpxap):

    diagnostics = test_cpxap.modules[0].read_diagnostic_status()
    assert len(diagnostics) == test_cpxap.read_module_count() + 1
    assert all(isinstance(d, CpxApEp.Diagnostics) for d in diagnostics)


def test_read_bootloader_version(test_cpxap):

    value = test_cpxap.modules[0].read_bootloader_version()
    assert value == "1.2.3"


def test_module_naming(test_cpxap):
    assert isinstance(test_cpxap.cpxap8di, CpxAp8Di)
    test_cpxap.cpxap8di.name = "test"
    assert test_cpxap.test.read_channel(0) is False


def test_modules(test_cpxap):
    assert isinstance(test_cpxap.modules[0], CpxApEp)
    assert isinstance(test_cpxap.modules[1], CpxAp16Di)
    assert isinstance(test_cpxap.modules[2], CpxAp12Di4Do)
    assert isinstance(test_cpxap.modules[3], CpxAp8Do)
    assert isinstance(test_cpxap.modules[4], CpxAp8Di)
    assert isinstance(test_cpxap.modules[5], CpxAp4Iol)

    assert all(isinstance(item, CpxApModule) for item in test_cpxap.modules)

    for m in test_cpxap.modules:
        assert m.information.input_size >= 0

    assert test_cpxap.modules[0].information.module_code in CpxApEp.module_codes
    assert test_cpxap.modules[0].position == 0

    assert test_cpxap.modules[1].information.module_code in CpxAp16Di.module_codes
    assert test_cpxap.modules[1].position == 1

    assert test_cpxap.modules[2].information.module_code in CpxAp12Di4Do.module_codes
    assert test_cpxap.modules[2].position == 2

    assert test_cpxap.modules[3].information.module_code in CpxAp8Do.module_codes
    assert test_cpxap.modules[3].position == 3

    assert test_cpxap.modules[4].information.module_code in CpxAp8Di.module_codes
    assert test_cpxap.modules[4].position == 4

    assert test_cpxap.modules[5].information.module_code in CpxAp4Iol.module_codes
    assert test_cpxap.modules[5].position == 5

    assert test_cpxap.modules[0].output_register is None  # EP
    assert test_cpxap.modules[1].output_register == 0  # 16di
    assert test_cpxap.modules[2].output_register == 0  # 12DiDo, adds 1
    assert test_cpxap.modules[3].output_register == 1  # 8Do, adds 1
    assert test_cpxap.modules[4].output_register == 2  # 8Di
    assert test_cpxap.modules[5].output_register == 2  # 4Iol

    assert test_cpxap.modules[0].input_register is None  # EP
    assert test_cpxap.modules[1].input_register == 5000  # 16Di, adds 1
    assert test_cpxap.modules[2].input_register == 5001  # 12DiDo, adds 1
    assert test_cpxap.modules[3].input_register == 5002  # 8Do
    assert test_cpxap.modules[4].input_register == 5002  # 8Di, adds 1
    assert test_cpxap.modules[5].input_register == 5003  # 4Iol


def test_16Di(test_cpxap):
    assert test_cpxap.modules[1].read_channels() == [False] * 16


def test_16Di_configure(test_cpxap):
    test_cpxap.modules[1].configure_debounce_time(1)


def test_12Di4Do(test_cpxap):
    assert test_cpxap.modules[2].read_channels() == [False] * 16

    data = [True, False, True, False]
    test_cpxap.modules[2].write_channels(data)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channels()[:12] == [False] * 12
    assert test_cpxap.modules[2].read_channels()[12:] == data

    data = [False, True, False, True]
    test_cpxap.modules[2].write_channels(data)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channels()[:12] == [False] * 12
    assert test_cpxap.modules[2].read_channels()[12:] == data

    test_cpxap.modules[2].write_channels([False, False, False, False])

    test_cpxap.modules[2].set_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is True
    assert test_cpxap.modules[2].read_channel(12) is True

    test_cpxap.modules[2].clear_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is False
    assert test_cpxap.modules[2].read_channel(12) is False

    test_cpxap.modules[2].toggle_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is True
    assert test_cpxap.modules[2].read_channel(12) is True

    test_cpxap.modules[2].clear_channel(0)


def test_8do(test_cpxap):
    a8do = test_cpxap.modules[3]
    assert a8do.read_channel(0) is False
    a8do.write_channel(0, True)
    time.sleep(0.05)
    assert a8do.read_channel(0) is True
    a8do.clear_channel(0)
    time.sleep(0.05)
    assert a8do.read_channel(0) is False
    a8do.toggle_channel(0)
    time.sleep(0.05)
    assert a8do.read_channel(0) is True


def test_8di(test_cpxap):
    a8di = test_cpxap.modules[4]
    assert a8di.read_channel(0) is False
    assert a8di.read_channels() == [False] * 8


def test_ep_param_read(test_cpxap):
    ep = test_cpxap.modules[0]
    param = ep.read_parameters()

    assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.42"
    assert param.active_subnet_mask == "255.255.255.0"
    assert param.active_gateway_address == "0.0.0.0"
    assert param.mac_address == "00:0e:f0:8e:ae:9e"
    assert param.setup_monitoring_load_supply == 1


def test_ep_configure(test_cpxap):
    ep = test_cpxap.modules[0]

    ep.configure_monitoring_load_supply(0)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 0

    ep.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 2

    ep.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 1


def test_12Di4Do_configures(test_cpxap):
    idx = 2
    a12di4do = test_cpxap.modules[idx]
    assert isinstance(a12di4do, CpxAp12Di4Do)
    time.sleep(0.05)

    a12di4do.configure_debounce_time(3)
    time.sleep(0.05)
    assert a12di4do.base.read_parameter(idx, cpx_ap_parameters.INPUT_DEBOUNCE_TIME) == 3

    a12di4do.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert (
        a12di4do.base.read_parameter(idx, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 2
    )

    a12di4do.configure_behaviour_in_fail_state(1)
    time.sleep(0.05)
    assert (
        a12di4do.base.read_parameter(idx, cpx_ap_parameters.FAIL_STATE_BEHAVIOUR) == 1
    )

    time.sleep(0.05)
    # reset to default
    a12di4do.configure_debounce_time(1)
    time.sleep(0.05)
    a12di4do.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    a12di4do.configure_behaviour_in_fail_state(0)


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


def test_read_ap_parameter(test_cpxap):
    info = test_cpxap.modules[1].information
    ap = test_cpxap.modules[1].read_ap_parameter()
    assert ap.module_code == info.module_code

    info = test_cpxap.modules[2].information
    ap = test_cpxap.modules[2].read_ap_parameter()
    assert ap.module_code == info.module_code

    info = test_cpxap.modules[3].information
    ap = test_cpxap.modules[3].read_ap_parameter()
    assert ap.module_code == info.module_code

    info = test_cpxap.modules[4].information
    ap = test_cpxap.modules[4].read_ap_parameter()
    assert ap.module_code == info.module_code

    info = test_cpxap.modules[5].information
    ap = test_cpxap.modules[5].read_ap_parameter()
    assert ap.module_code == info.module_code


def test_4iol_sdas(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_port_mode(2, channel=0)

    time.sleep(0.05)

    # example SDAS-MHS on port 0
    param = a4iol.read_fieldbus_parameters()
    assert param[0]["Port status information"] == "OPERATE"

    sdas_data = a4iol.read_channel(0)
    assert len(sdas_data) == 2

    process_data = int.from_bytes(sdas_data, byteorder="big")

    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    assert 0 <= pdv <= 4095

    assert a4iol[0] == a4iol.read_channel(0)


def test_4iol_sdas_full(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_port_mode(2, channel=0)

    time.sleep(0.05)

    # example SDAS-MHS on port 0
    param = a4iol.read_fieldbus_parameters()
    assert param[0]["Port status information"] == "OPERATE"

    sdas_data = a4iol.read_channel(0, full_size=True)
    assert len(sdas_data) == 8

    sdas_data = sdas_data[:2]  # only two bytes relevant

    process_data = int.from_bytes(sdas_data, byteorder="big")

    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    assert 0 <= pdv <= 4095

    assert a4iol[0] == a4iol.read_channel(0)


def test_4iol_ehps(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
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
    a4iol.configure_port_mode(2, channel=ehps_channel)

    time.sleep(0.05)

    param = a4iol.read_fieldbus_parameters()
    assert param[ehps_channel]["Port status information"] == "OPERATE"

    process_data_in = read_process_data_in(a4iol, ehps_channel)
    assert process_data_in["Ready"] is True

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
    a4iol.write_channel(ehps_channel, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    data[0] = 0x0100
    process_data_out = struct.pack(">HHHH", *data)
    a4iol.write_channel(ehps_channel, process_data_out)

    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(a4iol, ehps_channel)
        time.sleep(0.05)

    # Close command 0x 0200
    data[0] = 0x0200
    process_data_out = struct.pack(">HHHH", *data)
    a4iol.write_channel(ehps_channel, process_data_out)

    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(a4iol, ehps_channel)
        time.sleep(0.05)

    assert process_data_in["Error"] is False
    assert process_data_in["ClosedPositionFlag"] is True
    assert process_data_in["OpenedPositionFlag"] is False


def test_4iol_ethrottle(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)

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

    a4iol.configure_port_mode(2, channel=ethrottle_channel)

    time.sleep(0.05)

    param = a4iol.read_fieldbus_parameters()
    assert param[ethrottle_channel]["Port status information"] == "OPERATE"

    process_input_data = read_process_data_in(a4iol, ethrottle_channel)

    if not process_input_data["Homing Valid"]:
        process_output_data = [1]
        process_output_data = struct.pack(">Q", *process_output_data)
        a4iol.write_channel(ethrottle_channel, process_output_data)

        while not process_input_data["Homing Valid"]:
            process_input_data = read_process_data_in(a4iol, ethrottle_channel)

    process_output_data = [0xF00]  # setpoint 0xF00
    process_output_data = struct.pack(">Q", *process_output_data)
    a4iol.write_channel(ethrottle_channel, process_output_data)

    time.sleep(0.1)

    while not process_input_data["Motion Complete"]:
        process_input_data = read_process_data_in(a4iol, ethrottle_channel)


def test_4iol_ethrottle_isdu_read(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    ethrottle_channel = 2
    time.sleep(0.05)
    a4iol.configure_port_mode(2, ethrottle_channel)
    time.sleep(0.05)

    assert a4iol.read_isdu(ethrottle_channel, 16, 0)[:17] == b"Festo SE & Co. KG"


def test_4iol_ethrottle_isdu_write(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    ethrottle_channel = 2
    function_tag_idx = 25
    a4iol.write_isdu(b"\x01\x02\x03\x04", ethrottle_channel, function_tag_idx, 0)

    assert (
        a4iol.read_isdu(ethrottle_channel, function_tag_idx, 0)[:4]
        == b"\x01\x02\x03\x04"
    )


def test_4iol_configure_monitoring_load_supply(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)

    a4iol.configure_monitoring_load_supply(0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 0

    a4iol.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 1

    a4iol.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP) == 2

    a4iol.configure_monitoring_load_supply(1)


def test_4iol_configure_target_cycle_time(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)

    time.sleep(0.05)
    a4iol.configure_target_cycle_time(16, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 0) == 16

    a4iol.configure_target_cycle_time(73, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 1) == 73
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 2) == 73

    a4iol.configure_target_cycle_time(158)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 0) == 158
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 1) == 158
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 2) == 158
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_CYCLE_TIME, 3) == 158

    a4iol.configure_target_cycle_time(0)


def test_4iol_configure_device_lost_diagnostics(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_device_lost_diagnostics(False, channel=0)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE)
        is False
    )

    a4iol.configure_device_lost_diagnostics(False, channel=[1, 2])
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 1)
        is False
    )
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 2)
        is False
    )

    a4iol.configure_device_lost_diagnostics(False)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 0)
        is False
    )
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 1)
        is False
    )
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 2)
        is False
    )
    assert (
        a4iol.base.read_parameter(5, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, 3)
        is False
    )

    a4iol.configure_device_lost_diagnostics(True)


def test_4iol_configure_port_mode(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_port_mode(0, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 0) == 0

    a4iol.configure_port_mode(3, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 1) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 2) == 3

    a4iol.configure_port_mode(97)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 0) == 97
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 1) == 97
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 2) == 97
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.PORT_MODE, 3) == 97

    a4iol.configure_port_mode(0)


def test_4iol_configure_review_and_backup(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_review_and_backup(1, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 0) == 1

    a4iol.configure_review_and_backup(2, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 1) == 2
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 2) == 2

    a4iol.configure_review_and_backup(3)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 0) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 1) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 2) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.VALIDATION_AND_BACKUP, 3) == 3

    a4iol.configure_review_and_backup(0)


def test_4iol_configure_target_vendor_id(test_cpxap):
    a4iol = test_cpxap.modules[5]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_target_vendor_id(1, channel=0)
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 0) == 1

    a4iol.configure_target_vendor_id(2, channel=[1, 2])
    a4iol.configure_port_mode(1, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 1) == 2
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 2) == 2

    a4iol.configure_target_vendor_id(3)
    a4iol.configure_port_mode(1)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 0) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 1) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 2) == 3
    assert a4iol.base.read_parameter(5, cpx_ap_parameters.NOMINAL_VENDOR_ID, 3) == 3

    a4iol.configure_target_vendor_id(0)
    a4iol.configure_port_mode(0)


def test_4iol_configure_setpoint_device_id(test_cpxap):

    channel = 2
    position = 5
    a4iol = test_cpxap.modules[position]
    assert isinstance(a4iol, CpxAp4Iol)

    a4iol.configure_port_mode(0)
    time.sleep(0.05)

    a4iol.configure_setpoint_device_id(1, channel=channel)
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=channel)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(
            position, cpx_ap_parameters.NOMINAL_DEVICE_ID, channel
        )
        == 1
    )

    a4iol.configure_setpoint_device_id(2, channel=[channel])
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=[channel])
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(
            position, cpx_ap_parameters.NOMINAL_DEVICE_ID, channel
        )
        == 2
    )

    a4iol.configure_setpoint_device_id(3)
    time.sleep(0.05)
    a4iol.configure_port_mode(1)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(
            position, cpx_ap_parameters.NOMINAL_DEVICE_ID, channel
        )
        == 3
    )

    a4iol.configure_setpoint_device_id(0)
    time.sleep(0.05)
    a4iol.configure_port_mode(0)
