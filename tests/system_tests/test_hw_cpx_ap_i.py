"""Tests for cpx-ap system"""

import time
import pytest
import struct

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol
from cpx_io.cpx_system.cpx_ap.vabx_ap import VabxAP
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import (
    LoadSupply,
    FailState,
    ChannelRange,
    TempUnit,
    PortMode,
)


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


def test_timeout(test_cpxap):
    "test timeout"
    reg = test_cpxap.read_reg_data(14000, 2)[::-1]
    data = struct.unpack(">I", reg)[0]
    assert data == 100


def test_set_timeout():
    "test timeout"
    with CpxAp(ip_address="172.16.1.41", timeout=0.5) as cpxap:
        reg = cpxap.read_reg_data(14000, 2)[::-1]
        data = struct.unpack(">I", reg)[0]
        assert data == 500


def test_read_module_information(test_cpxap):
    modules = []
    time.sleep(0.05)
    cnt = test_cpxap.read_module_count()
    for i in range(cnt):
        modules.append(test_cpxap.read_module_information(i))
    assert modules[0].module_code in CpxApEp.module_codes


def test_module_naming(test_cpxap):
    assert isinstance(test_cpxap.cpxap8di, CpxAp8Di)
    test_cpxap.cpxap8di.name = "test"
    assert test_cpxap.test.read_channel(0) is False


def test_modules(test_cpxap):
    assert isinstance(test_cpxap.modules[0], CpxApEp)
    assert isinstance(test_cpxap.modules[1], CpxAp8Di)
    assert isinstance(test_cpxap.modules[2], CpxAp4Di4Do)
    assert isinstance(test_cpxap.modules[3], CpxAp4AiUI)
    assert isinstance(test_cpxap.modules[4], CpxAp4Iol)
    assert isinstance(test_cpxap.modules[5], VabxAP)
    assert isinstance(test_cpxap.modules[6], CpxAp4Di)

    assert all(isinstance(item, CpxApModule) for item in test_cpxap.modules)

    for m in test_cpxap.modules:
        assert m.information.input_size >= 0

    assert test_cpxap.modules[0].information.module_code in CpxApEp.module_codes
    assert test_cpxap.modules[0].position == 0

    assert test_cpxap.modules[1].information.module_code in CpxAp8Di.module_codes
    assert test_cpxap.modules[1].position == 1

    assert test_cpxap.modules[2].information.module_code in CpxAp4Di4Do.module_codes
    assert test_cpxap.modules[2].position == 2

    assert test_cpxap.modules[3].information.module_code in CpxAp4AiUI.module_codes
    assert test_cpxap.modules[3].position == 3

    assert test_cpxap.modules[4].information.module_code in CpxAp4Iol.module_codes
    assert test_cpxap.modules[4].position == 4

    assert test_cpxap.modules[5].information.module_code in VabxAP.module_codes
    assert test_cpxap.modules[5].position == 5

    assert test_cpxap.modules[6].information.module_code in CpxAp4Di.module_codes
    assert test_cpxap.modules[6].position == 6

    assert test_cpxap.modules[0].output_register is None  # EP
    assert test_cpxap.modules[1].output_register == 0  # 8DI
    assert test_cpxap.modules[2].output_register == 0  # 4DI4DO, adds 1
    assert test_cpxap.modules[3].output_register == 1  # 4AIUI
    assert test_cpxap.modules[4].output_register == 1  # 4IOL, adds 16
    assert test_cpxap.modules[5].output_register == 17  # VABX adds 2
    assert test_cpxap.modules[6].output_register == 19  # 4Di

    assert test_cpxap.modules[0].input_register is None  # EP
    assert test_cpxap.modules[1].input_register == 5000  # 8DI, adds 1
    assert test_cpxap.modules[2].input_register == 5001  # 4DI4DO, adds 1
    assert test_cpxap.modules[3].input_register == 5002  # 4AIUI, adds 4
    assert test_cpxap.modules[4].input_register == 5006  # 4IOL, adds 18
    assert test_cpxap.modules[5].input_register == 5024  # VABX
    assert test_cpxap.modules[6].input_register == 5024  # 4Di


def test_8Di(test_cpxap):
    assert test_cpxap.modules[1].read_channels() == [False] * 8


def test_8Di_configure(test_cpxap):
    test_cpxap.modules[1].configure_debounce_time(1)


def test_vabx_read_channels(test_cpxap):
    "test vabx"
    POSITION = 5
    assert isinstance(test_cpxap.modules[POSITION], VabxAP)
    channels = test_cpxap.modules[POSITION].read_channels()
    assert channels == [False] * 32


def test_vabx_read_channel(test_cpxap):
    "test vabx"
    POSITION = 5
    assert isinstance(test_cpxap.modules[POSITION], VabxAP)
    channels = test_cpxap.modules[POSITION].read_channel(0)
    assert channels is False


def test_vabx_write(test_cpxap):
    "test vabx"
    POSITION = 5
    assert isinstance(test_cpxap.modules[POSITION], VabxAP)
    test_cpxap.modules[POSITION].write_channel(0, True)
    time.sleep(0.05)
    assert test_cpxap.modules[POSITION].read_channel(0) is True
    time.sleep(0.05)
    test_cpxap.modules[POSITION].write_channel(0, False)
    time.sleep(0.05)
    assert test_cpxap.modules[POSITION].read_channel(0) is False


def test_4Di(test_cpxap):
    POSITION = 6
    assert isinstance(test_cpxap.modules[POSITION], CpxAp4Di)
    assert test_cpxap.modules[POSITION].read_channels() == [False] * 4


def test_4Di4Do(test_cpxap):
    assert test_cpxap.modules[2].read_channels() == [False] * 8

    data = [True, False, True, False]
    test_cpxap.modules[2].write_channels(data)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channels()[:4] == [False] * 4
    assert test_cpxap.modules[2].read_channels()[4:] == data

    data = [False, True, False, True]
    test_cpxap.modules[2].write_channels(data)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channels()[:4] == [False] * 4
    assert test_cpxap.modules[2].read_channels()[4:] == data

    test_cpxap.modules[2].write_channels([False, False, False, False])

    test_cpxap.modules[2].set_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is True
    assert test_cpxap.modules[2].read_channel(4) is True

    test_cpxap.modules[2].clear_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is False
    assert test_cpxap.modules[2].read_channel(4) is False

    test_cpxap.modules[2].toggle_channel(0)
    time.sleep(0.05)
    assert test_cpxap.modules[2].read_channel(0, output_numbering=True) is True
    assert test_cpxap.modules[2].read_channel(4) is True

    test_cpxap.modules[2].clear_channel(0)


def test_4AiUI_None(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert len(a4aiui.read_channels()) == 4


def test_4AiUI_5V_CH1(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    a4aiui.configure_channel_range(1, ChannelRange.U_10V)
    time.sleep(0.05)
    a4aiui.configure_linear_scaling(1, False)
    time.sleep(0.05)

    assert 15900 < test_cpxap.modules[3].read_channel(1) < 16100


def test_4AiUI_5V_CH1_with_scaling(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    a4aiui.configure_channel_range(1, ChannelRange.U_10V)
    time.sleep(0.05)
    a4aiui.configure_channel_limits(1, upper=10000)
    time.sleep(0.05)
    a4aiui.configure_channel_limits(1, lower=0)
    time.sleep(0.05)

    assert 4900 < test_cpxap.modules[3].read_channel(1) < 5100

    a4aiui.configure_channel_limits(0, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(1, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(2, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(3, upper=32767, lower=-32768)
    time.sleep(0.05)
    a4aiui.configure_linear_scaling(1, False)


def test_ep_param_read(test_cpxap):
    ep = test_cpxap.modules[0]
    param = ep.read_parameters()

    # assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.41"
    assert param.active_subnet_mask == "255.255.255.0"
    assert param.active_gateway_address == "172.16.1.41"
    assert param.mac_address == "00:0e:f0:7d:3b:15"
    assert param.setup_monitoring_load_supply == 1


def test_ep_configure(test_cpxap):
    ep = test_cpxap.modules[0]
    param = ep.read_parameters()

    ep.configure_monitoring_load_supply(0)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, ParameterNameMap()["LoadSupplyDiagSetup"]) == 0

    ep.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, ParameterNameMap()["LoadSupplyDiagSetup"]) == 2

    ep.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    assert ep.base.read_parameter(0, ParameterNameMap()["LoadSupplyDiagSetup"]) == 1


def test_4AiUI_configures_channel_unit(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)

    a4aiui.configure_channel_temp_unit(0, TempUnit.CELSIUS)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["TemperatureUnit"], 0) == 0

    a4aiui.configure_channel_temp_unit(1, TempUnit.FARENHEIT)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["TemperatureUnit"], 1) == 1

    a4aiui.configure_channel_temp_unit(2, TempUnit.KELVIN)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["TemperatureUnit"], 2) == 2

    a4aiui.configure_channel_temp_unit(3, TempUnit.FARENHEIT)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["TemperatureUnit"], 3) == 1

    # reset
    a4aiui.configure_channel_temp_unit(0, TempUnit.CELSIUS)
    a4aiui.configure_channel_temp_unit(1, TempUnit.CELSIUS)
    a4aiui.configure_channel_temp_unit(2, TempUnit.CELSIUS)
    a4aiui.configure_channel_temp_unit(3, TempUnit.CELSIUS)


def test_4AiUI_configures_channel_range(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)

    a4aiui.configure_channel_range(0, ChannelRange.B_10V)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["ChannelInputMode"], 0) == 1

    a4aiui.configure_channel_range(1, ChannelRange.U_10V)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["ChannelInputMode"], 1) == 3

    a4aiui.configure_channel_range(2, ChannelRange.B_5V)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["ChannelInputMode"], 2) == 2

    a4aiui.configure_channel_range(3, ChannelRange.U_1_5V)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["ChannelInputMode"], 3) == 4

    # reset
    a4aiui.configure_channel_range(0, ChannelRange.NONE)
    a4aiui.configure_channel_range(1, ChannelRange.NONE)
    a4aiui.configure_channel_range(2, ChannelRange.NONE)
    a4aiui.configure_channel_range(3, ChannelRange.NONE)


def test_4AiUI_configures_hysteresis_monitoring(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)
    time.sleep(0.05)

    a4aiui.configure_hysteresis_limit_monitoring(0, 101)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["DiagnosisHysteresis"], 0)
        == 101
    )

    a4aiui.configure_hysteresis_limit_monitoring(1, 0)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["DiagnosisHysteresis"], 1) == 0
    )

    a4aiui.configure_hysteresis_limit_monitoring(2, 65535)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["DiagnosisHysteresis"], 2)
        == 65535
    )

    a4aiui.configure_hysteresis_limit_monitoring(3, 99)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["DiagnosisHysteresis"], 3)
        == 99
    )

    # reset
    a4aiui.configure_hysteresis_limit_monitoring(0, 100)
    a4aiui.configure_hysteresis_limit_monitoring(1, 100)
    a4aiui.configure_hysteresis_limit_monitoring(2, 100)
    a4aiui.configure_hysteresis_limit_monitoring(3, 100)


def test_4AiUI_configures_channel_smoothing(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)

    a4aiui.configure_channel_smoothing(0, 1)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["SmoothFactor"], 0) == 1

    a4aiui.configure_channel_smoothing(1, 2)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["SmoothFactor"], 1) == 2

    a4aiui.configure_channel_smoothing(2, 3)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["SmoothFactor"], 2) == 3

    a4aiui.configure_channel_smoothing(3, 4)
    time.sleep(0.05)
    assert a4aiui.base.read_parameter(3, ParameterNameMap()["SmoothFactor"], 3) == 4

    # reset
    a4aiui.configure_channel_smoothing(0, 5)
    a4aiui.configure_channel_smoothing(1, 5)
    a4aiui.configure_channel_smoothing(2, 5)
    a4aiui.configure_channel_smoothing(3, 5)


def test_4AiUI_configures_linear_scaling(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)

    a4aiui.configure_linear_scaling(0, True)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LinearScalingEnable"], 0)
        is True
    )

    a4aiui.configure_linear_scaling(1, False)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LinearScalingEnable"], 1)
        is False
    )

    a4aiui.configure_linear_scaling(2, True)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LinearScalingEnable"], 2)
        is True
    )

    a4aiui.configure_linear_scaling(3, False)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LinearScalingEnable"], 3)
        is False
    )

    # reset
    a4aiui.configure_linear_scaling(0, False)
    a4aiui.configure_linear_scaling(1, False)
    a4aiui.configure_linear_scaling(2, False)
    a4aiui.configure_linear_scaling(3, False)


def test_4AiUI_configures_channel_limits(test_cpxap):
    a4aiui = test_cpxap.modules[3]
    assert isinstance(a4aiui, CpxAp4AiUI)

    a4aiui.configure_channel_limits(0, upper=1111, lower=-1111)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["UpperThresholdValue"], 0)
        == 1111
    )
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LowerThresholdValue"], 0)
        == -1111
    )

    a4aiui.configure_channel_limits(1, upper=2222, lower=-2222)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["UpperThresholdValue"], 1)
        == 2222
    )
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LowerThresholdValue"], 1)
        == -2222
    )

    a4aiui.configure_channel_limits(2, upper=3333, lower=-3333)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["UpperThresholdValue"], 2)
        == 3333
    )
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LowerThresholdValue"], 2)
        == -3333
    )

    a4aiui.configure_channel_limits(3, upper=4444, lower=-4444)
    time.sleep(0.05)
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["UpperThresholdValue"], 3)
        == 4444
    )
    assert (
        a4aiui.base.read_parameter(3, ParameterNameMap()["LowerThresholdValue"], 3)
        == -4444
    )

    # reset
    a4aiui.configure_channel_limits(0, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(1, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(2, upper=32767, lower=-32768)
    a4aiui.configure_channel_limits(3, upper=32767, lower=-32768)


def test_4Di4Do_configures(test_cpxap):
    a4di4do = test_cpxap.modules[2]
    assert isinstance(a4di4do, CpxAp4Di4Do)
    time.sleep(0.05)

    a4di4do.configure_debounce_time(3)
    time.sleep(0.05)
    assert a4di4do.base.read_parameter(2, ParameterNameMap()["InputDebounceTime"]) == 3

    a4di4do.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert (
        a4di4do.base.read_parameter(2, ParameterNameMap()["LoadSupplyDiagSetup"]) == 2
    )

    a4di4do.configure_behaviour_in_fail_state(1)
    time.sleep(0.05)
    assert a4di4do.base.read_parameter(2, ParameterNameMap()["FailStateBehaviour"]) == 1

    time.sleep(0.05)
    # reset to default
    a4di4do.configure_debounce_time(1)
    time.sleep(0.05)
    a4di4do.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    a4di4do.configure_behaviour_in_fail_state(0)


def test_getter(test_cpxap):
    a8di = test_cpxap.modules[1]
    a4di4do = test_cpxap.modules[2]
    a4ai = test_cpxap.modules[3]

    assert a8di[0] == a8di.read_channel(0)
    assert a4di4do[0] == a4di4do.read_channel(0)
    assert a4di4do[4] == a4di4do.read_channel(4)
    assert a4ai[0] == a4ai.read_channel(0)


def test_setter(test_cpxap):
    a4di4do = test_cpxap.modules[2]

    a4di4do[0] = True
    time.sleep(0.05)
    # read back the first output channel (it's on index 4)
    assert a4di4do[4] is True

    a4di4do[0] = False
    time.sleep(0.05)
    # read back the first output channel (it's on index 4)
    assert a4di4do[4] is False


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


def test_4iol_sdas(test_cpxap):
    a4iol = test_cpxap.modules[4]
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
    a4iol = test_cpxap.modules[4]
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
    a4iol = test_cpxap.modules[4]
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
    a4iol.configure_port_mode(PortMode.IOL_AUTOSTART, channel=ehps_channel)

    # wait for operate
    param = a4iol.read_fieldbus_parameters()
    while param[ehps_channel]["Port status information"] != "OPERATE":
        param = a4iol.read_fieldbus_parameters()

    # wait for ready
    process_data_in = read_process_data_in(a4iol, ehps_channel)
    while not process_data_in["Ready"]:
        process_data_in = read_process_data_in(a4iol, ehps_channel)

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

    a4iol.configure_port_mode(PortMode.DEACTIVATED, channel=ehps_channel)
    # wait for inactive
    param = a4iol.read_fieldbus_parameters()
    while param[ehps_channel]["Port status information"] != "DEACTIVATED":
        param = a4iol.read_fieldbus_parameters()


def test_4iol_ethrottle(test_cpxap):
    a4iol = test_cpxap.modules[4]
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
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    ethrottle_channel = 2

    assert (a4iol.read_isdu(ethrottle_channel, 16, 0)[:17]) == b"Festo SE & Co. KG"


def test_4iol_ethrottle_isdu_write(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    ethrottle_channel = 2
    function_tag_idx = 25
    a4iol.write_isdu(b"\x01\x02\x03\x04", ethrottle_channel, function_tag_idx, 0)

    assert (
        a4iol.read_isdu(ethrottle_channel, function_tag_idx, 0)[:4]
        == b"\x01\x02\x03\x04"
    )


def test_read_pqi(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_port_mode(2, channel=0)
    a4iol.configure_port_mode(0, channel=1)
    time.sleep(0.05)

    pqi = a4iol.read_pqi()
    assert pqi[0]["Port Qualifier"] == "input data is valid"
    assert pqi[1]["Port Qualifier"] == "input data is invalid"


def test_4iol_configure_monitoring_load_supply(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)

    a4iol.configure_monitoring_load_supply(0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["LoadSupplyDiagSetup"]) == 0

    a4iol.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["LoadSupplyDiagSetup"]) == 1

    a4iol.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["LoadSupplyDiagSetup"]) == 2

    a4iol.configure_monitoring_load_supply(1)


def test_4iol_configure_target_cycle_time(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)

    time.sleep(0.05)
    a4iol.configure_target_cycle_time(16, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 0) == 16

    a4iol.configure_target_cycle_time(73, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 1) == 73
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 2) == 73

    a4iol.configure_target_cycle_time(158)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 0) == 158
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 1) == 158
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 2) == 158
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["NominalCycleTime"], 3) == 158
    )

    a4iol.configure_target_cycle_time(0)


def test_4iol_configure_device_lost_diagnostics(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_device_lost_diagnostics(False, channel=0)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"])
        is False
    )

    a4iol.configure_device_lost_diagnostics(False, channel=[1, 2])
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 1)
        is False
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 2)
        is False
    )

    a4iol.configure_device_lost_diagnostics(False)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 0)
        is False
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 1)
        is False
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 2)
        is False
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["DeviceLostDiagnosisEnable"], 3)
        is False
    )

    a4iol.configure_device_lost_diagnostics(True)


def test_4iol_configure_port_mode(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_port_mode(0, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 0) == 0

    a4iol.configure_port_mode(3, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 1) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 2) == 3

    a4iol.configure_port_mode(97)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 0) == 97
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 1) == 97
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 2) == 97
    assert a4iol.base.read_parameter(4, ParameterNameMap()["PortMode"], 3) == 97

    a4iol.configure_port_mode(0)


def test_4iol_configure_review_and_backup(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_review_and_backup(1, channel=0)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 0) == 1
    )

    a4iol.configure_review_and_backup(2, channel=[1, 2])
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 1) == 2
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 2) == 2
    )

    a4iol.configure_review_and_backup(3)
    time.sleep(0.05)
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 0) == 3
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 1) == 3
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 2) == 3
    )
    assert (
        a4iol.base.read_parameter(4, ParameterNameMap()["ValidationAndBackup"], 3) == 3
    )

    a4iol.configure_review_and_backup(0)


def test_4iol_configure_target_vendor_id(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_target_vendor_id(1, channel=0)
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 0) == 1

    a4iol.configure_target_vendor_id(2, channel=[1, 2])
    a4iol.configure_port_mode(1, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 1) == 2
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 2) == 2

    a4iol.configure_target_vendor_id(3)
    a4iol.configure_port_mode(1)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 0) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 1) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 2) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalVendorID"], 3) == 3

    a4iol.configure_target_vendor_id(0)
    a4iol.configure_port_mode(0)


def test_4iol_configure_setpoint_device_id(test_cpxap):
    a4iol = test_cpxap.modules[4]
    assert isinstance(a4iol, CpxAp4Iol)
    time.sleep(0.05)

    a4iol.configure_setpoint_device_id(1, channel=0)
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=0)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 0) == 1

    a4iol.configure_setpoint_device_id(2, channel=[1, 2])
    time.sleep(0.05)
    a4iol.configure_port_mode(1, channel=[1, 2])
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 1) == 2
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 2) == 2

    a4iol.configure_setpoint_device_id(3)
    time.sleep(0.05)
    a4iol.configure_port_mode(1)
    time.sleep(0.05)
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 0) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 1) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 2) == 3
    assert a4iol.base.read_parameter(4, ParameterNameMap()["NominalDeviceID"], 3) == 3

    a4iol.configure_setpoint_device_id(0)
    time.sleep(0.05)
    a4iol.configure_port_mode(0)


def test_vabx_configures(test_cpxap):
    "test configure functions of vabx"
    POSITION = 5
    vabx = test_cpxap.modules[POSITION]

    vabx.configure_diagnosis_for_defect_valve(False)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.VALVE_DEFECT_DIAG_ENABLE)
        == 0
    )

    vabx.configure_monitoring_load_supply(2)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP)
        == 2
    )

    vabx.configure_behaviour_in_fail_state(1)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.FAIL_STATE_BEHAVIOUR) == 1
    )

    time.sleep(0.05)
    # reset to default
    vabx.configure_diagnosis_for_defect_valve(True)
    time.sleep(0.05)
    vabx.configure_monitoring_load_supply(1)
    time.sleep(0.05)
    vabx.configure_behaviour_in_fail_state(0)


def test_vabx_configures_enums(test_cpxap):
    "test configure functions of vabx"
    POSITION = 5
    vabx = test_cpxap.modules[POSITION]

    vabx.configure_diagnosis_for_defect_valve(False)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.VALVE_DEFECT_DIAG_ENABLE)
        == 0
    )

    vabx.configure_monitoring_load_supply(LoadSupply.ACTIVE)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP)
        == 2
    )

    vabx.configure_behaviour_in_fail_state(FailState.HOLD_LAST_STATE)
    time.sleep(0.05)
    assert (
        vabx.base.read_parameter(POSITION, cpx_ap_parameters.FAIL_STATE_BEHAVIOUR) == 1
    )

    time.sleep(0.05)
    # reset to default
    vabx.configure_diagnosis_for_defect_valve(True)
    time.sleep(0.05)
    vabx.configure_monitoring_load_supply(LoadSupply.ACTIVE_DIAG_OFF)
    time.sleep(0.05)
    vabx.configure_behaviour_in_fail_state(FailState.RESET_OUTPUTS)
