"""Tests for cpx base class"""

import pytest

from cpx_io.cpx_system.cpx_base import CpxBase


@pytest.fixture(scope="module")
def test_cpx_base():
    base = CpxBase(ip_address="172.16.1.40")
    yield base


def test_init(test_cpx_base):
    assert test_cpx_base


def test_read_reg_data(test_cpx_base):
    data = test_cpx_base.read_reg_data(40001)
    assert data == b"\00\00"


def test_read_reg_data_more(test_cpx_base):
    data = test_cpx_base.read_reg_data(40001, 2)
    assert data == b"\00\00\00\00"


def test_write_reg_data_wrong_type(test_cpx_base):
    with pytest.raises(TypeError):
        test_cpx_base.write_reg_data("test", 40001)


def test_read_device_info(test_cpx_base):
    info = test_cpx_base.read_device_info()
    assert info["vendor_name"] == "Festo AG & Co. KG"
    assert info["product_code"] == "CPX-E-EP"
    assert info["revision"] == "1.2"
    assert info["vendor_url"] == "http://www.festo.com"
    assert info["product_name"] == "Modbus TCP"
    assert info["model_name"] == "CPX-E-Terminal"


def test_read_device_info_cpx_ap_i():
    cpx_base = CpxBase(ip_address="172.16.1.41")
    info = cpx_base.read_device_info()
    assert info["vendor_name"] == "Festo SE & Co. KG"
    assert info["product_code"] == "CPX-AP-EP"
    assert info["revision"] == "1.6.3"
    assert info["vendor_url"] == "http://www.festo.com"
    assert info["product_name"] == "CPX-AP-EtherNet/IP (Modbus mode)"
    assert info["model_name"] == "CPX-AP Node"


def test_read_device_info_cpx_ap_a():
    cpx_base = CpxBase(ip_address="172.16.1.42")
    info = cpx_base.read_device_info()
    assert info["vendor_name"] == "Festo SE & Co. KG"
    assert info["product_code"] == "CPX-AP-EP"
    assert info["revision"] == "1.6.3"
    assert info["vendor_url"] == "http://www.festo.com"
    assert info["product_name"] == "CPX-AP-EtherNet/IP (Modbus mode)"
    assert info["model_name"] == "CPX-AP Node"


def test_read_device_info_cpx_ap_mpa():
    cpx_base = CpxBase(ip_address="172.16.1.43")
    info = cpx_base.read_device_info()
    assert info["vendor_name"] == "Festo SE & Co. KG"
    assert info["product_code"] == "CPX-AP-EP"
    assert info["revision"] == "1.6.3"
    assert info["vendor_url"] == "http://www.festo.com"
    assert info["product_name"] == "CPX-AP-EtherNet/IP (Modbus mode)"
    assert info["model_name"] == "CPX-AP Node"
