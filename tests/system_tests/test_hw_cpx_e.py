import pytest

import time

from cpx_io.cpx_system.cpx_e import *

@pytest.fixture(scope="function")
def test_cpxe():
    cpxe = CpxE(host="172.16.1.40", tcp_port=502, timeout=500)
    yield cpxe

    cpxe.__del__()

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

def test_signed16_to_int():
    module = CpxE8Do()

    assert module.signed16_to_int(0x0000) == 0
    assert module.signed16_to_int(0x0001) == 1
    assert module.signed16_to_int(0xFFFF) == -1
    assert module.signed16_to_int(0xFFFE) == -2
    assert module.signed16_to_int(0xCAFE) == -13570
    
    with pytest.raises(ValueError):
        module.int_to_signed16(0x1FFFF)

def test_int_to_signed16():
    module = CpxE8Do()

    assert module.int_to_signed16(0) == 0x0000
    assert module.int_to_signed16(1) == 0x0001
    assert module.int_to_signed16(-1) == 0xFFFF
    assert module.int_to_signed16(-2) == 0xFFFE
    assert module.int_to_signed16(-13570) == 0xCAFE
    
    with pytest.raises(ValueError):
        module.int_to_signed16(32769)

    with pytest.raises(ValueError):
        module.int_to_signed16(-32769)


def test_add_module(test_cpxe):
    assert test_cpxe.modules == {"CPX-E-EP": 0} 
    assert test_cpxe._next_output_register == 40003  
    assert test_cpxe._next_input_register == 45395 

def test_module_not_initialized(test_cpxe):
    e8do = CpxE8Do()
    with pytest.raises(InitError):
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
    assert test_cpxe.modules == {"CPX-E-EP": 0, "CPX-E-16DI": 1}   


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

    assert e8do.read_channels() == [False] * 8
    
    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2
                            } 
    
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
    
    # channel 3 is hardwired to 5 Vdc, this is around 13800 digits
    assert e4ai.set_channel_range(3, "0-10V") == None
    assert e4ai.set_channel_smothing(3, 2) == None
    time.sleep(.1)
    data0 = e4ai.read_channel(3)
    assert -10 < data0 < 10
    assert -10 < e4ai.read_channels()[3] < 10
    
    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI-U-I": 3
                            }                  


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

    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI-U-I": 3,
                            "CPX-E-4AO-U-I": 4
                            }                           

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

    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI-U-I": 3,
                            "CPX-E-4AO-U-I": 4
                            }        

def test_analog_io(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUI())
    e4ao = test_cpxe.add_module(CpxE4AoUI())

    e4ao.set_channel_range(0,'0-10V')
    e4ao.set_channel_range(1,'0-10V')
    e4ao.set_channel_range(2,'0-10V')
    e4ao.set_channel_range(3,'0-10V')

    e4ai.set_channel_range(0,'0-10V')
    e4ai.set_channel_range(1,'0-10V')
    e4ai.set_channel_range(2,'0-10V')
    e4ai.set_channel_range(3,'0-10V')
    time.sleep(.05)

    values = [0, 1000, 5000, 13000]

    e4ao.write_channel(0, values[0])
    e4ao.write_channel(1, values[1])
    e4ao.write_channel(2, values[2])
    e4ao.write_channel(3, values[3])
    time.sleep(.05)

    result = e4ai.read_channels()

    for i, v in enumerate(values):
        assert v - 50 < result[i] < v + 50