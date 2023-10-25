import pytest

import time

from cpx_io.cpx_system.cpx_e import *

@pytest.fixture(scope="function")
def test_cpxe():
    cpxe = CpxE(host="172.16.1.40", tcp_port=502, timeout=1)
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
    data = [False] * 16
    data[0] = True 
    test = e16di.read_channels()
    assert e16di.read_channels() == data
    assert e16di.read_channel(0) == True
    assert e16di.read_channel(1) == False
    assert test_cpxe.modules == {"CPX-E-EP": 0, "CPX-E-16DI": 1}   


def test_2modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    assert e8do.output_register == 40003
    assert e8do.input_register == 45397
    assert test_cpxe._next_output_register == 40004
    assert test_cpxe._next_input_register == 45399

    assert e8do.position == 2
    #assert e8do.read_channels() == [False] * 8 
    #assert e8do.read_channel(0) == False
    
    data = [False] * 8
    data[0] = True
    assert e8do.write_channels(data) == None
    #time.sleep(.1)
    '''
    assert e16di.read_channel(1) == True
    #assert e8do.read_channels() == data
    #assert e8do.read_channel(0) == True

    assert e8do.set_channel(0) == None
    #time.sleep(.1)
    assert e16di.read_channel(1) == True
    #assert e8do.read_channel(0) == True
    assert e8do.clear_channel(0) == None
    #time.sleep(.1)
    assert e16di.read_channel(1) == False
    #assert e8do.read_channel(0) == False
    assert e8do.toggle_channel(0) == None
    #time.sleep(.1)
    assert e16di.read_channel(1) == True
    #assert e8do.read_channel(0) == True
    assert e8do.clear_channel(0) == None
    #time.sleep(.1)
    assert e16di.read_channel(1) == False
    '''
    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2
                            } 

    #response = e8do.read_channels()   
    #assert response == [False] * 8


def test_3modules(test_cpxe): 
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUi())
    assert e4ai.output_register == None
    assert e4ai.input_register == 45399
    assert test_cpxe._next_output_register == 40004
    assert test_cpxe._next_input_register == 45404

    assert e4ai.read_status() == [False] * 16 

    assert e4ai.position == 3
    assert e4ai.set_channel_range(0, "0-10V") == None
    assert e4ai.set_channel_smothing(0, 2) == None
    assert e4ai.read_channels() == [0] * 4
    assert e4ai.read_channel(0) == 0  

    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3
                            }                   


def test_4modules(test_cpxe):
    e16di = test_cpxe.add_module(CpxE16Di())
    e8do = test_cpxe.add_module(CpxE8Do())
    e4ai = test_cpxe.add_module(CpxE4AiUi())
    e4ao = test_cpxe.add_module(CpxE4AoUi())
    assert e4ao.output_register == 40004
    assert e4ao.input_register == 45404
    assert test_cpxe._next_output_register == 40008
    assert test_cpxe._next_input_register == 45409

    assert e4ao.read_status() == [False] * 16 

    assert e4ao.position == 4
    #assert e4ao.set_channel_range(0, "0-10V") == None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.write_channels([0]*4) == None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.read_channel(0) == 0    

    assert test_cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3,
                            "CPX-E-4AO_U_I": 4
                            }                              

def test_5modules(test_cpxe):
    pass

def test_modules_with_init():
    modules = [CpxEEp(), 
               CpxE16Di(), 
               CpxE8Do(), 
               CpxE4AiUi(), 
               CpxE4AoUi()
               ]

    cpxe = CpxE(host="172.16.1.40", modules=modules) 

    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3,
                            "CPX-E-4AO_U_I": 4
                            }        