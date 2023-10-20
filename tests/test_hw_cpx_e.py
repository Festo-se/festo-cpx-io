import pytest

import time

import sys
sys.path.append(".")

from src.cpx_io.cpx_system.cpx_e import *

def test_init():
    cpxe = CPX_E(host="172.16.1.40", tcpPort=502, timeout=1)
    assert cpxe
    cpxe.__del__()

def test_readFunctionNumber():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.readFunctionNumber(1)
    assert response == [0]
    cpxe.__del__()

def test_writeFunctionNumber():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.writeFunctionNumber(23,1)
    assert response == None
    cpxe.__del__()

def test_module_count():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.module_count()
    assert response == 6
    cpxe.__del__()

def test_fault_detection():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.fault_detection()
    assert response == [False] * 24 
    cpxe.__del__()

def test_status_register():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.status_register()
    assert response == (False, False) 
    cpxe.__del__()

def test_device_identification():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.read_device_identification()
    assert response in range(1,6)
    cpxe.__del__()


def test_add_module():
    cpxe = CPX_E(host="172.16.1.40")
    assert cpxe.modules == {"CPX-E-EP": 0} 
    assert cpxe._next_output_register == 40003  
    assert cpxe._next_input_register == 45395 
    cpxe.__del__()


def test_1module():
    cpxe = CPX_E(host="172.16.1.40")
    e16di = cpxe.add_module(CPX_E_16DI())
    assert e16di.output_register == None
    assert e16di.input_register == 45395
    assert cpxe._next_output_register == 40003
    assert cpxe._next_input_register == 45397

    assert e16di.position == 1
    data = [False] * 16
    data[0] = True 
    test = e16di.read_channels()
    assert e16di.read_channels() == data
    assert e16di.read_channel(0) == True
    assert e16di.read_channel(1) == False
    assert cpxe.modules == {"CPX-E-EP": 0, "CPX-E-16DI": 1}   
    cpxe.__del__()


def test_2modules():
    #time.sleep(10)
    cpxe = CPX_E(host="172.16.1.40", timeout=200)
    e16di = cpxe.add_module(CPX_E_16DI())
    e8do = cpxe.add_module(CPX_E_8DO())
    assert e8do.output_register == 40003
    assert e8do.input_register == 45397
    assert cpxe._next_output_register == 40004
    assert cpxe._next_input_register == 45399

    assert e8do.position == 2
    assert e8do.read_channels() == [False] * 8 
    assert e8do.read_channel(0) == False
    '''
    data = [False] * 8
    data[0] = True
    assert e8do.write_channels(data) == None
    #time.sleep(.1)
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
    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2
                            } 

    response = e8do.read_channels()   
    assert response == [False] * 8                      
    cpxe.__del__()


def test_3modules():
    cpxe = CPX_E(host="172.16.1.40", timeout=200)
    e16di = cpxe.add_module(CPX_E_16DI())
    e8do = cpxe.add_module(CPX_E_8DO())
    e4ai = cpxe.add_module(CPX_E_4AI_U_I())
    assert e4ai.output_register == None
    assert e4ai.input_register == 45399
    assert cpxe._next_output_register == 40004
    assert cpxe._next_input_register == 45404

    assert e4ai.read_status() == [False] * 16 

    assert e4ai.position == 3
    assert e4ai.set_channel_range(0, "0-10V") == None
    assert e4ai.set_channel_smothing(0, 2) == None
    assert e4ai.read_channels() == [0] * 4
    assert e4ai.read_channel(0) == 0  

    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3
                            }                   
    cpxe.__del__()


def test_4modules():
    cpxe = CPX_E(host="172.16.1.40", timeout=200)
    e16di = cpxe.add_module(CPX_E_16DI())
    e8do = cpxe.add_module(CPX_E_8DO())
    e4ai = cpxe.add_module(CPX_E_4AI_U_I())
    e4ao = cpxe.add_module(CPX_E_4AO_U_I())
    assert e4ao.output_register == 40004
    assert e4ao.input_register == 45404
    assert cpxe._next_output_register == 40008
    assert cpxe._next_input_register == 45409

    test = cpxe.read_device_identification()

    assert e4ao.read_status() == [False] * 16 

    assert e4ao.position == 4
    #assert e4ao.set_channel_range(0, "0-10V") == None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.write_channels([0]*4) == None
    assert e4ao.read_channels() == [0] * 4
    assert e4ao.read_channel(0) == 0    

    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3,
                            "CPX-E-4AO_U_I": 4
                            }                              
    cpxe.__del__()

def test_5modules():
    pass

def test_modules_with_init():
    modules = [CPX_E_EP(), 
               CPX_E_16DI(), 
               CPX_E_8DO(), 
               CPX_E_4AI_U_I(), 
               CPX_E_4AO_U_I()
               ]

    cpxe = CPX_E(host="172.16.1.40", modules=modules) 

    assert cpxe.modules == {"CPX-E-EP": 0,
                            "CPX-E-16DI": 1,
                            "CPX-E-8DO": 2,
                            "CPX-E-4AI_U_I": 3,
                            "CPX-E-4AO_U_I": 4
                            }        