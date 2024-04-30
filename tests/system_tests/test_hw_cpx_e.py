"""Tests for cpx-e system"""

import struct
import time
import pytest

from cpx_io.cpx_system.cpx_base import CpxInitError

from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_module import CpxModule

from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol
from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci
from cpx_io.cpx_system.cpx_e.cpx_e_enums import ChannelRange, OperatingMode


@pytest.fixture(scope="function")
def test_cpxe():
    with CpxE(ip_address="172.16.1.40") as cpxe:
        yield cpxe


def test_init(test_cpxe):
    assert test_cpxe


def test_readFunctionNumber(test_cpxe):
    response = test_cpxe.read_function_number(1)
    assert response == 0


def test_writeFunctionNumber(test_cpxe):
    response = test_cpxe.write_function_number(23, 1)
    assert response == None


def test_module_count(test_cpxe):
    response = test_cpxe.module_count()
    assert response == 7


def test_fault_detection(test_cpxe):
    response = test_cpxe.read_fault_detection()
    assert len(response) == 24


def test_status_register(test_cpxe):
    response = test_cpxe.read_status()
    assert response == (False, False)


def test_device_identification(test_cpxe):
    response = test_cpxe.read_device_identification()
    assert response in range(1, 6)


def test_add_module(test_cpxe):
    assert isinstance(test_cpxe.modules[0], CpxEEp)
    assert test_cpxe.next_output_register == 40003
    assert test_cpxe.next_input_register == 45395


def test_module_notconfigured(test_cpxe):
    e8do = CpxE8Do()
    with pytest.raises(CpxInitError):
        e8do.set_channel(0)


def test_1module(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    assert e16di.output_register == 40003
    assert e16di.input_register == 45395
    assert test_cpxe.next_output_register == 40003
    assert test_cpxe.next_input_register == 45397

    assert e16di.position == 1

    # set up channel 1 to True (hardwire, hardcode)
    data = [False] * 16
    data[1] = True
    assert e16di.read_channels() == data
    assert e16di.read_channel(0) is False
    assert e16di.read_channel(1) is True

    assert all(isinstance(item, CpxModule) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[1], CpxE16Di)
    assert test_cpxe.modules[1] == e16di


def test_module_naming(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    assert e16di == test_cpxe.cpxe16di
    test_cpxe.cpxe16di.name = "test"
    assert test_cpxe.test.read_channel(0) is False


def test_2modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    assert e8do.output_register == 40003
    assert e8do.input_register == 45397
    assert test_cpxe.next_output_register == 40004
    assert test_cpxe.next_input_register == 45399
    assert e8do.position == 2

    assert e8do.read_channels() == [False] * 8
    assert e8do.read_channel(0) is False
    time.sleep(0.05)

    # set up channel 0 to True on 8DO,
    # this is routed to channel 0 16DI.
    # channel 1 of 16DI is still True (hardwired)
    data = [False] * 8
    data[0] = True
    assert e8do.write_channels(data) is None
    assert e8do.read_channels() == data
    assert e8do.read_channel(0) is True
    time.sleep(0.05)
    assert e16di.read_channel(0) is True

    assert e8do.set_channel(0) is None
    assert e8do.read_channel(0) is True
    time.sleep(0.05)
    assert e16di.read_channel(0) is True

    assert e8do.clear_channel(0) is None
    assert e8do.read_channel(0) is False
    time.sleep(0.05)
    assert e16di.read_channel(0) is False

    assert e8do.toggle_channel(0) is None
    assert e8do.read_channel(0) is True
    time.sleep(0.05)
    assert e16di.read_channel(0) is True

    assert e8do.clear_channel(0) is None
    assert e8do.read_channel(0) is False
    time.sleep(0.05)
    assert e16di.read_channel(0) is False

    time.sleep(0.05)
    assert e8do.read_channels() == [False] * 8

    assert all(isinstance(item, CpxModule) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[2], CpxE8Do)
    assert test_cpxe.modules[2] == e8do


def test_8DO_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())

    e8do.configure_diagnostics(short_circuit=False, undervoltage=False)
    time.sleep(0.01)
    assert e8do.base.read_function_number(4828 + 64 * 2) == 0

    e8do.configure_diagnostics(short_circuit=True, undervoltage=False)
    time.sleep(0.01)
    assert e8do.base.read_function_number(4828 + 64 * 2) == 2

    e8do.configure_diagnostics(short_circuit=False, undervoltage=True)
    time.sleep(0.01)
    assert e8do.base.read_function_number(4828 + 64 * 2) == 4

    e8do.configure_diagnostics(short_circuit=True, undervoltage=True)
    time.sleep(0.01)
    assert e8do.base.read_function_number(4828 + 64 * 2) == 6


def test_8DO_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())

    e8do.configure_power_reset(True)
    time.sleep(0.05)
    assert e8do.base.read_function_number(4828 + 64 * 2 + 1) == 2

    e8do.configure_power_reset(False)
    time.sleep(0.05)
    assert e8do.base.read_function_number(4828 + 64 * 2 + 1) == 0


def test_16DI_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    e16di.configure_diagnostics(False)
    time.sleep(0.05)
    assert e16di.base.read_function_number(4828 + 64 * 1) == 0

    e16di.configure_diagnostics(True)
    time.sleep(0.05)
    assert e16di.base.read_function_number(4828 + 64 * 1) == 1


def test_16DI_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    e16di.configure_power_reset(False)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0x01) == 0

    e16di.configure_power_reset(True)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0x01) == 1


def test_16DI_configure_debounce_time(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    val = 2
    e16di.configure_debounce_time(val)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0b00110000) >> 4 == val

    val = 1
    e16di.configure_debounce_time(val)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0b00110000) >> 4 == val

    with pytest.raises(ValueError):
        e16di.configure_debounce_time(-1)

    with pytest.raises(ValueError):
        e16di.configure_debounce_time(4)


def test_16DI_configure_signal_extension_time(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    val = 2
    e16di.configure_signal_extension_time(val)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0b11000000) >> 6 == val

    val = 1
    e16di.configure_signal_extension_time(val)
    time.sleep(0.05)
    assert (e16di.base.read_function_number(4828 + 64 * 1 + 1) & 0b11000000) >> 6 == val

    with pytest.raises(ValueError):
        e16di.configure_signal_extension_time(-1)

    with pytest.raises(ValueError):
        e16di.configure_signal_extension_time(4)


def test_3modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    assert e4ai.output_register == 40004
    assert e4ai.input_register == 45399
    assert test_cpxe.next_output_register == 40004
    assert test_cpxe.next_input_register == 45404

    assert e4ai.read_status() == [False] * 16
    assert e4ai.position == 3

    e4ai.configure_channel_range(3, ChannelRange.U_10V)
    e4ai.configure_channel_smoothing(3, 2)
    time.sleep(0.05)
    data0 = e4ai.read_channel(3)
    # assert -10 < data0 < 10
    # assert -10 < e4ai.read_channels()[3] < 10

    assert all(isinstance(item, CpxModule) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[3], CpxE4AiUI)
    assert test_cpxe.modules[3] == e4ai


def test_4AI_configure_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_diagnostics(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 0) & 0x01) == 0

    e4ai.configure_diagnostics(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 0) & 0x01) == 1


def test_4AI_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_power_reset(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 1) & 0x01) == 0

    e4ai.configure_power_reset(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 1) & 0x01) == 1


def test_4AI_configure_data_format(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_data_format(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0x01) == 1

    e4ai.configure_data_format(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0x01) == 0


def test_4AI_configure_sensor_supply(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_sensor_supply(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b00100000) >> 5 == 0

    e4ai.configure_sensor_supply(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b00100000) >> 5 == 1


def test_4AI_configure_diagnostics_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_diagnostics_overload(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b01000000) >> 6 == 0

    e4ai.configure_diagnostics_overload(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b01000000) >> 6 == 1


def test_4AI_configure_behaviour_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_behaviour_overload(False)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b10000000) >> 7 == 0

    e4ai.configure_behaviour_overload(True)
    time.sleep(0.05)
    assert (e4ai.base.read_function_number(4828 + 64 * 3 + 6) & 0b10000000) >> 7 == 1


def test_4AI_configure_hysteresis_limit_monitoring(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    time.sleep(0.05)

    lower = 10
    upper = 20
    e4ai.configure_hysteresis_limit_monitoring(lower=lower)
    time.sleep(0.05)
    assert e4ai.base.read_function_number(4828 + 64 * 3 + 7) == 10

    e4ai.configure_hysteresis_limit_monitoring(upper=upper)
    time.sleep(0.05)
    assert e4ai.base.read_function_number(4828 + 64 * 3 + 8) == 20

    e4ai.configure_hysteresis_limit_monitoring(lower=0, upper=0)
    assert e4ai.base.read_function_number(4828 + 64 * 3 + 7) == 0
    assert e4ai.base.read_function_number(4828 + 64 * 3 + 8) == 0

    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(lower=-1)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(lower=32768)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(upper=-1)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(upper=32768)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(lower=-1, upper=-1)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring(lower=32768, upper=32768)
    with pytest.raises(ValueError):
        e4ai.configure_hysteresis_limit_monitoring()


def test_4modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())
    assert e4ao.output_register == 40004
    assert e4ao.input_register == 45404
    assert test_cpxe.next_output_register == 40008
    assert test_cpxe.next_input_register == 45409

    assert e4ao.read_status() == [False] * 16
    assert e4ao.position == 4

    assert e4ao.read_channels() == [0] * 4
    assert e4ao.write_channels([0] * 4) is None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.read_channel(0) == 0

    assert e4ao.write_channels([20] * 4) is None
    assert e4ao.read_channels() == [20] * 4

    assert e4ao.write_channel(0, 40) is None
    assert e4ao.read_channel(0) == 40

    assert all(isinstance(item, CpxModule) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[4], CpxE4AoUI)
    assert test_cpxe.modules[4] == e4ao


def test_modules_with_init():
    modules = [CpxEEp(), CpxE16Di(), CpxE8Do(), CpxE4AiUI(), CpxE4AoUI()]

    cpxe = CpxE(ip_address="172.16.1.40", modules=modules)

    assert all(isinstance(item, CpxModule) for item in cpxe.modules)
    assert all([cpxe.modules[i] == modules[i] for i in range(len(modules))])


def test_4AO_configure_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_diagnostics(
        short_circuit=False, undervoltage=False, param_error=False
    )
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 0) & 0b10000110) == 0

    e4ao.configure_diagnostics(short_circuit=True, undervoltage=True, param_error=True)
    time.sleep(0.05)
    assert (
        e4ao.base.read_function_number(4828 + 64 * 4 + 0) & 0b10000110
    ) == 0b10000110


def test_4AO_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_power_reset(False)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 1) & 0x02) >> 1 == 0

    e4ao.configure_power_reset(True)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 1) & 0x02) >> 1 == 1


def test_4AO_configure_behaviour_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_behaviour_overload(False)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 1) & 0x08) >> 3 == 0

    e4ao.configure_behaviour_overload(True)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 1) & 0x08) >> 3 == 1


def test_4AO_configure_data_format(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_data_format(True)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 6) & 0x01) == 1

    e4ao.configure_data_format(False)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 6) & 0x01) == 0


def test_4AO_configure_actuator_supply(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_actuator_supply(False)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 6) & 0b00100000) >> 5 == 0

    e4ao.configure_actuator_supply(True)
    time.sleep(0.05)
    assert (e4ao.base.read_function_number(4828 + 64 * 4 + 6) & 0b00100000) >> 5 == 1


def test_analog_io(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_channel_range(0, ChannelRange.U_10V)
    e4ao.configure_channel_range(1, ChannelRange.U_10V)
    e4ao.configure_channel_range(2, ChannelRange.U_10V)
    e4ao.configure_channel_range(3, ChannelRange.U_10V)

    e4ai.configure_channel_range(0, ChannelRange.U_10V)
    e4ai.configure_channel_range(1, ChannelRange.U_10V)
    e4ai.configure_channel_range(2, ChannelRange.U_10V)
    e4ai.configure_channel_range(3, ChannelRange.U_10V)
    time.sleep(0.05)

    values = [0, 1000, 5000, 13000]

    e4ao.write_channel(0, values[0])
    e4ao.write_channel(1, values[1])
    e4ao.write_channel(2, values[2])
    e4ao.write_channel(3, values[3])
    time.sleep(0.05)

    result = e4ai.read_channels()

    # for i, v in enumerate(values):
    #    assert v - 50 < result[i] < v + 50


def test_getter(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    assert e16di[0] == e16di.read_channel(0)
    assert e8do[0] == e8do.read_channel(0)
    # assert e4ai[0] == e4ai.read_channel(0)
    assert e4ao[0] == e4ao.read_channel(0)


def test_setter(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e8do[0] = True
    time.sleep(0.05)
    assert e8do[0] == True

    e8do[0] = False
    time.sleep(0.05)
    assert e8do[0] == False

    e4ao[0] = 5
    time.sleep(0.05)
    assert e4ao[0] == 5

    e4ao[0] = 0
    time.sleep(0.05)
    assert e4ao[0] == 0


def test_4iol_sdas(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())
    e4iol = test_cpxe.add_module(CpxE4Iol())

    assert isinstance(e4iol, CpxE4Iol)

    e4iol.configure_operating_mode(OperatingMode.IO_LINK, channel=0)
    state = ""
    # wait for state to change
    while state != "OPERATE":
        state = e4iol.read_line_state()[0]

    sdas_data = e4iol.read_channel(0)  # only two bytes relevant

    process_data = int.from_bytes(sdas_data, byteorder="big")

    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    assert 0 <= pdv <= 4095

    assert e4iol[0] == e4iol.read_channel(0)

    e4iol.configure_operating_mode(OperatingMode.INACTIVE, channel=0)
    state = ""
    # wait for state to change
    while state != "INACTIVE":
        state = e4iol.read_line_state()[0]


"""
def test_4iol_ehps(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())
    e4iol = test_cpxe.add_module(CpxE4Iol(8))

    assert isinstance(e4iol, CpxE4Iol)

    # process data decoding (device specific)
    def read_process_data_in(module, channel):
        # ehps provides 48 bit "process data in".
        data = module.read_channel(channel)
        ehps_data = struct.unpack(">HHHH", data)
        assert ehps_data[3] == 0

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

    # example EHPS-20-A-LK on port 2
    ehps_channel = 1

    # reset power
    e4iol.configure_pl_supply(False, ehps_channel)
    e4iol.configure_ps_supply(False)
    time.sleep(0.08)
    e4iol.configure_pl_supply(True, ehps_channel)
    e4iol.configure_ps_supply(True)
    time.sleep(0.08)

    e4iol.configure_operating_mode(OperatingMode.IO_LINK, channel=ehps_channel)

    state = ""
    # wait for state to change
    while state != "OPERATE":
        state = e4iol.read_line_state()[ehps_channel]

    # wait for ready
    ready = False
    while not ready:
        ready = read_process_data_in(e4iol, ehps_channel)["Ready"]

    # demo of process data out, also sent to initialize
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
    e4iol.write_channel(ehps_channel, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    data[0] = 0x0100
    process_data_out = struct.pack(">HHHH", *data)
    e4iol.write_channel(ehps_channel, process_data_out)

    process_data_in = read_process_data_in(e4iol, ehps_channel)
    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(e4iol, ehps_channel)
        time.sleep(0.05)

    # Close command 0x 0200
    data[0] = 0x0200
    process_data_out = struct.pack(">HHHH", *data)
    e4iol.write_channel(ehps_channel, process_data_out)

    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(e4iol, ehps_channel)
        time.sleep(0.05)

    assert process_data_in["Error"] is False
    assert process_data_in["ClosedPositionFlag"] is True
    assert process_data_in["OpenedPositionFlag"] is False

    e4iol.configure_operating_mode(OperatingMode.INACTIVE, channel=ehps_channel)
    state = ""
    # wait for state to change
    while state != "INACTIVE":
        state = e4iol.read_line_state()[ehps_channel]
"""


def test_1ci_module(test_cpxe):
    """Test ci module by toggling do channel 1 on input A and setting input B to 24 V"""
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())
    e4iol = test_cpxe.add_module(CpxE4Iol(8))
    e1ci = test_cpxe.add_module(CpxE1Ci())

    assert isinstance(e1ci, CpxE1Ci)

    assert e1ci.base.next_input_register == 45450
    assert e1ci.base.next_output_register == 40025

    status = e1ci.read_status()
    assert status == [False] * 16

    e1ci.configure_signal_type(2)
    e1ci.configure_signal_evaluation(3)
    e1ci.configure_load_value(0)
    time.sleep(0.05)
    e1ci.write_process_data(set_counter=True)

    while not e1ci.read_process_data().set_counter:
        continue
    e1ci.write_process_data(set_counter=False)
    while e1ci.read_process_data().set_counter:
        continue

    for _ in range(16):
        e8do.toggle_channel(1)
        time.sleep(0.05)

    assert e1ci.read_value() == 8
