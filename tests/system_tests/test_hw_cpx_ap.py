import pytest

import time

from cpx_io.cpx_system.cpx_ap import *


@pytest.fixture(scope="function")
def test_cpxap():
    cpxap = CpxAP(host="172.16.1.41", tcp_port=502, timeout=500)
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
    