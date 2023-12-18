"""Contains tests for TestCpxApModule class"""
from unittest.mock import Mock, patch
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule


class TestCpxApModule:
    "Test CpxApModule"

    def test_constructor(self):
        """Test constructor"""

        module = CpxApModule()
        assert module.base is None
        assert module.position is None
        assert module.information is None
        assert module.output_register is None
        assert module.input_register is None

    def test_repr(self):
        """Test repr"""

        module = CpxApModule()
        module.information = {}
        module.information["Order Text"] = "text"
        module.information["Modul Code"] = "code"

        module.position = 1
        assert repr(module) == "code (idx: 1, type: CpxApModule)"

    def test_configure(self):
        """Test configure"""
        module = CpxApModule()

        mocked_base = Mock()
        module.base = mocked_base

        module.configure(mocked_base, 1)

        assert module.base == mocked_base
        assert module.position == 1

    def test_update_information(self):
        """Test update_information"""

        module = CpxApModule()
        module.information = {}

        module.update_information({"test": "information"})
        assert module.information == {"test": "information"}

    def test_read_ap_parameter(self):
        """Test read_ap_parameter"""
        module = CpxApModule()

        mocked_base = Mock()
        mocked_base.read_parameter = Mock(return_value=[0x01, 0x02])
        module.base = mocked_base

        ret = module.read_ap_parameter()

        assert ret["Fieldbus serial number"] == 131073
        assert ret["Product Key"] == "\x01\x00\x02"
        assert ret["Firmware Version"] == "\x01\x00\x02"
        assert ret["Module Code"] == 131073
        assert ret["Measured value of temperature AP-ASIC [°C]"] == 2
        assert ret["Current measured value of logic supply PS [mV]"] == 2
        assert ret["Current measured value of load supply PL [mV]"] == 2
        assert ret["Hardware Version"] == 1
