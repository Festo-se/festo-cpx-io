import pytest

import sys
sys.path.append(".")

from src.cpx_io.cpx_system import cpx_e

def test_init():
    cpxe = cpx_e.CPX_E(host="192.168.1.3", tcpPort=502, timeout=1)
    cpxe.moduleCount
    cpxe.moduleInformation
    cpxe.__del__()

def test_readRegData():
    cpxe = cpx_e.CPX_E(host="192.168.1.3")
    reg = cpxe.readRegData(40001, length=1, type="input_register")
    print(reg)