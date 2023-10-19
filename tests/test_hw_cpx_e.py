import pytest

import sys
sys.path.append(".")

from src.cpx_io.cpx_system.cpx_e import CPX_E

def test_init():
    cpxe = CPX_E(host="172.16.1.40", tcpPort=502, timeout=1)
    assert cpxe
    cpxe.__del__()

def test_readFunctionNumber():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.readFunctionNumber(1)
    assert response == [0]*16
    cpxe.__del__()

def test_writeFunctionNumber():
    cpxe = CPX_E(host="172.16.1.40")
    response = cpxe.writeFunctionNumber(1,1)
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



