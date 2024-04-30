"""Tests for cpx-ap system"""

import time
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import CpxModule


@pytest.fixture(scope="function")
def test_cpxap():
    """test fixture"""
    with CpxAp(ip_address="172.16.1.43") as cpxap:
        yield cpxap


def test_init(test_cpxap):
    "test init"
    assert test_cpxap


def test_module_count(test_cpxap):
    "test module_count"
    assert test_cpxap.read_module_count() == 6


def test_modules(test_cpxap):
    assert all(isinstance(m, CpxModule) for m in test_cpxap.modules)

    for i, m in enumerate(test_cpxap.modules):
        assert m.information.input_size >= 0
        assert test_cpxap.modules[i].position == i


def test_ep_read_system_parameters(test_cpxap):
    m = test_cpxap.modules[0]
    param = m.read_system_parameters()

    assert param.dhcp_enable is False
    assert param.active_ip_address == "172.16.1.43"
    assert param.active_subnet_mask == "255.255.255.0"
    assert param.active_gateway_address == "0.0.0.0"
    assert param.mac_address == "00:0e:f0:92:ef:72"
    assert param.setup_monitoring_load_supply == 1
