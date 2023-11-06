import pytest

import time

from cpx_io.cpx_system.cpx_e import *
from cpx_io.cpx_system.cpx_base import CpxInitError


@pytest.fixture(scope="function")
def test_cpxe():
    with CpxE(host="172.16.1.40", tcp_port=502, timeout=500) as cpxe:
        yield cpxe

def test_init(test_cpxe):
    assert test_cpxe

def test_readFunctionNumber(test_cpxe):
    response = test_cpxe.read_function_number(1)
    assert response == [0]

def test_writeFunctionNumber(test_cpxe):
    response = test_cpxe.write_function_number(23,1)
    assert response == None

def test_module_count(test_cpxe):
    response = test_cpxe.module_count()
    assert response == 6

def test_fault_detection(test_cpxe):
    response = test_cpxe.fault_detection()
    assert response == [False] * 24 

def test_status_register(test_cpxe):
    response = test_cpxe.status_register()
    assert response == (False, False) 

def test_device_identification(test_cpxe):
    response = test_cpxe.read_device_identification()
    assert response in range(1,6)

def test_add_module(test_cpxe):
    assert isinstance(test_cpxe.modules[0], CpxEEp)
    assert test_cpxe._next_output_register == 40003  
    assert test_cpxe._next_input_register == 45395 

def test_module_not_initialized(test_cpxe):
    e8do = CpxE8Do()
    with pytest.raises(CpxInitError):
        e8do.set_channel(0)

def test_1module(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    assert e16di.output_register == None
    assert e16di.input_register == 45395
    assert test_cpxe._next_output_register == 40003
    assert test_cpxe._next_input_register == 45397

    assert e16di.position == 1

    # set up channel 1 to True (hardwire, hardcode)
    data = [False] * 16
    data[1] = True
    assert e16di.read_channels() == data
    assert e16di.read_channel(0) == False
    assert e16di.read_channel(1) == True
    assert all(isinstance(item, CpxE) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[1], CpxE16Di)
    assert test_cpxe.modules[1] == e16di

def test_2modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    assert e8do.output_register == 40003
    assert e8do.input_register == 45397
    assert test_cpxe._next_output_register == 40004
    assert test_cpxe._next_input_register == 45399
    assert e8do.position == 2

    assert e8do.read_channels() == [False] * 8 
    assert e8do.read_channel(0) == False
    time.sleep(.1)
    
    # set up channel 0 to True on 8DO, 
    # this is routed to channel 0 16DI.
    # channel 1 of 16DI is still True (hardwired)
    data = [False] * 8
    data[0] = True
    assert e8do.write_channels(data) == None
    assert e8do.read_channels() == data
    assert e8do.read_channel(0) == True
    time.sleep(.1)
    assert e16di.read_channel(0) == True

    assert e8do.set_channel(0) == None
    assert e8do.read_channel(0) == True
    time.sleep(.1)
    assert e16di.read_channel(0) == True

    assert e8do.clear_channel(0) == None
    assert e8do.read_channel(0) == False
    time.sleep(.1)
    assert e16di.read_channel(0) == False

    assert e8do.toggle_channel(0) == None
    assert e8do.read_channel(0) == True
    time.sleep(.1)
    assert e16di.read_channel(0) == True

    assert e8do.clear_channel(0) == None
    assert e8do.read_channel(0) == False
    time.sleep(.1)
    assert e16di.read_channel(0) == False

    time.sleep(.1)
    assert e8do.read_channels() == [False] * 8
    
    assert all(isinstance(item, CpxE) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[2], CpxE8Do)
    assert test_cpxe.modules[2] == e8do
    
def test_8DO_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())

    e8do.configure_diagnostics(short_circuit=False, undervoltage=False)
    time.sleep(.01)
    assert e8do.base.read_function_number(4828 + 64*2) == [0]

    e8do.configure_diagnostics(short_circuit=True, undervoltage=False)
    time.sleep(.01)
    assert e8do.base.read_function_number(4828 + 64*2) == [2]

    e8do.configure_diagnostics(short_circuit=False, undervoltage=True)
    time.sleep(.01)
    assert e8do.base.read_function_number(4828 + 64*2) == [4]

    e8do.configure_diagnostics(short_circuit=True, undervoltage=True)
    time.sleep(.01)
    assert e8do.base.read_function_number(4828 + 64*2) == [6]

def test_8DO_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())

    e8do.configure_power_reset(True)
    time.sleep(.1)
    assert e8do.base.read_function_number(4828 + 64*2 + 1) == [2]

    e8do.configure_power_reset(False)
    time.sleep(.1)
    assert e8do.base.read_function_number(4828 + 64*2 + 1) == [0]

def test_16DI_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    e16di.configure_diagnostics(False)
    time.sleep(.1)
    assert e16di.base.read_function_number(4828 + 64*1) == [0]

    e16di.configure_diagnostics(True)
    time.sleep(.1)
    assert e16di.base.read_function_number(4828 + 64*1) == [1]

def test_16DI_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    e16di.configure_power_reset(False)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0x01) == 0

    e16di.configure_power_reset(True)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0x01) == 1

def test_16DI_configure_debounce_time(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    val = 2
    e16di.configure_debounce_time(val)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0b00110000) >> 4 == val

    val = 1
    e16di.configure_debounce_time(val)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0b00110000) >> 4 == val

    with pytest.raises(ValueError):
        e16di.configure_debounce_time(-1)

    with pytest.raises(ValueError):
        e16di.configure_debounce_time(4)

def test_16DI_configure_signal_extension_time(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())

    val = 2
    e16di.configure_signal_extension_time(val)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0b11000000) >> 6 == val

    val = 1
    e16di.configure_signal_extension_time(val)
    time.sleep(.1)
    assert (e16di.base.read_function_number(4828 + 64*1 + 1)[0] & 0b11000000) >> 6 == val

    with pytest.raises(ValueError):
        e16di.configure_signal_extension_time(-1)

    with pytest.raises(ValueError):
        e16di.configure_signal_extension_time(4)

def test_3modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    assert e4ai.output_register == None
    assert e4ai.input_register == 45399
    assert test_cpxe._next_output_register == 40004
    assert test_cpxe._next_input_register == 45404

    assert e4ai.read_status() == [False] * 16 
    assert e4ai.position == 3
    
    assert e4ai.configure_channel_range(3, "0-10V") == None
    assert e4ai.configure_channel_smoothing(3, 2) == None
    time.sleep(.1)
    data0 = e4ai.read_channel(3)
    assert -10 < data0 < 10
    assert -10 < e4ai.read_channels()[3] < 10
    
    assert all(isinstance(item, CpxE) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[3], CpxE4AiUI)
    assert test_cpxe.modules[3] == e4ai             

def test_4AI_configure_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_diagnostics(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 0)[0] & 0x01) == 0

    e4ai.configure_diagnostics(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 0)[0] & 0x01) == 1

def test_4AI_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_power_reset(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 1)[0] & 0x01) == 0

    e4ai.configure_power_reset(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 1)[0] & 0x01) == 1
    
def test_4AI_configure_data_format(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_data_format(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0x01) == 1

    e4ai.configure_data_format(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0x01) == 0
    
def test_4AI_configure_sensor_supply(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_sensor_supply(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b00100000) >> 5 == 0

    e4ai.configure_sensor_supply(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b00100000) >> 5 == 1
 
def test_4AI_configure_diagnostics_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_diagnostics_overload(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b01000000) >> 6 == 0

    e4ai.configure_diagnostics_overload(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b01000000) >> 6 == 1

def test_4AI_configure_behaviour_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())

    e4ai.configure_behaviour_overload(False)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b10000000) >> 7 == 0

    e4ai.configure_behaviour_overload(True)
    time.sleep(.1)
    assert (e4ai.base.read_function_number(4828 + 64*3 + 6)[0] & 0b10000000) >> 7 == 1

def test_4AI_configure_hysteresis_limit_monitoring(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    time.sleep(.05)

    lower = 10
    upper = 20
    e4ai.configure_hysteresis_limit_monitoring(lower=lower)
    time.sleep(.1)
    assert e4ai.base.read_function_number(4828 + 64*3 + 7) == [10]

    e4ai.configure_hysteresis_limit_monitoring(upper=upper)
    time.sleep(.1)
    assert e4ai.base.read_function_number(4828 + 64*3 + 8) == [20]

    e4ai.configure_hysteresis_limit_monitoring(lower=0, upper=0)
    assert e4ai.base.read_function_number(4828 + 64*3 + 7) == [0]
    assert e4ai.base.read_function_number(4828 + 64*3 + 8) == [0]

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
    assert test_cpxe._next_output_register == 40008
    assert test_cpxe._next_input_register == 45409

    assert e4ao.read_status() == [False] * 16 
    assert e4ao.position == 4

    assert e4ao.read_channels() == [0] * 4
    assert e4ao.write_channels([0]*4) == None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.read_channel(0) == 0

    assert e4ao.write_channels([20]*4) == None
    assert e4ao.read_channels() == [20] * 4

    assert e4ao.write_channel(0, 40) == None
    assert e4ao.read_channel(0) == 40
    
    assert all(isinstance(item, CpxE) for item in test_cpxe.modules)
    assert isinstance(test_cpxe.modules[4], CpxE4AoUI)
    assert test_cpxe.modules[4] == e4ao                        

def test_5modules(test_cpxe):
    # TODO: IO-LINK master
    pass

def test_modules_with_init():
    modules = [CpxEEp(), 
               CpxE16Di(), 
               CpxE8Do(), 
               CpxE4AiUI(), 
               CpxE4AoUI()
               ]

    cpxe = CpxE(host="172.16.1.40", modules=modules)
    
    assert all(isinstance(item, CpxE) for item in cpxe.modules)
    assert all([cpxe.modules[i] == modules[i] for i in range(len(modules))])

def test_4AO_configure_diagnostics(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_diagnostics(short_circuit=False, undervoltage=False, param_error=False)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 0)[0] & 0b10000110) == 0

    e4ao.configure_diagnostics(short_circuit=True, undervoltage=True, param_error=True)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 0)[0] & 0b10000110) == 0b10000110

def test_4AO_configure_power_reset(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_power_reset(False)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 1)[0] & 0x02) >> 1 == 0

    e4ao.configure_power_reset(True)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 1)[0] & 0x02) >> 1 == 1

def test_4AO_configure_behaviour_overload(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_behaviour_overload(False)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 1)[0] & 0x08) >> 3 == 0

    e4ao.configure_behaviour_overload(True)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 1)[0] & 0x08) >> 3 == 1
    
def test_4AO_configure_data_format(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_data_format(True)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 6)[0] & 0x01) == 1

    e4ao.configure_data_format(False)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 6)[0] & 0x01) == 0
    
def test_4AO_configure_actuator_supply(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_actuator_supply(False)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 6)[0] & 0b00100000) >> 5 == 0

    e4ao.configure_actuator_supply(True)
    time.sleep(.1)
    assert (e4ao.base.read_function_number(4828 + 64*4 + 6)[0] & 0b00100000) >> 5 == 1
 

def test_analog_io(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.configure_channel_range(0,'0-10V')
    e4ao.configure_channel_range(1,'0-10V')
    e4ao.configure_channel_range(2,'0-10V')
    e4ao.configure_channel_range(3,'0-10V')

    e4ai.configure_channel_range(0,'0-10V')
    e4ai.configure_channel_range(1,'0-10V')
    e4ai.configure_channel_range(2,'0-10V')
    e4ai.configure_channel_range(3,'0-10V')
    time.sleep(.1)

    values = [0, 1000, 5000, 13000]

    e4ao.write_channel(0, values[0])
    e4ao.write_channel(1, values[1])
    e4ao.write_channel(2, values[2])
    e4ao.write_channel(3, values[3])
    time.sleep(.1)

    result = e4ai.read_channels()

    for i, v in enumerate(values):
        assert v - 50 < result[i] < v + 50