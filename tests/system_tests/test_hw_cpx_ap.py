import pytest

import time

from cpx_io.cpx_system.cpx_ap import *


@pytest.fixture(scope="function")
def test_cpxap():
    cpxap = CpxAp(host="172.16.1.41", tcp_port=502, timeout=500)
    yield cpxap

    cpxap.__del__()

def test_init(test_cpxap):
    assert test_cpxap

def test_module_count(test_cpxap):
    assert test_cpxap.read_module_count() == 6

def test_read_module_information(test_cpxap):
    modules = []
    time.sleep(.05)
    cnt = test_cpxap.read_module_count()
    for i in range(cnt):
        modules.append(test_cpxap.read_module_information(i))
    assert modules[0]["Module Code"] == 8323
    
def test_modules(test_cpxap):
    assert isinstance(test_cpxap.modules[0], CpxApEp)
    assert isinstance(test_cpxap.modules[1], CpxAp8Di)
    assert isinstance(test_cpxap.modules[2], CpxAp4Di4Do)
    assert isinstance(test_cpxap.modules[3], CpxAp4AiUI)
    assert isinstance(test_cpxap.modules[4], CpxAp4Iol)
    assert isinstance(test_cpxap.modules[5], CpxAp4Di)

    for m in test_cpxap.modules:
        assert m.information["Input Size"] >= 0

    assert test_cpxap.modules[0].information["Module Code"] == 8323
    assert test_cpxap.modules[0].position == 0 

    assert test_cpxap.modules[0].input_register == 5000
    assert test_cpxap.modules[1].input_register == 5000
    assert test_cpxap.modules[2].input_register == 5001
    assert test_cpxap.modules[3].input_register == 5002
    assert test_cpxap.modules[4].input_register == 5010
    assert test_cpxap.modules[5].input_register == 5046
    
def test_8Di(test_cpxap):
    assert test_cpxap.modules[1].read_channels() == [False] * 8

def test_4Di(test_cpxap):
    assert test_cpxap.modules[2].read_channels() == [False] * 4
    
