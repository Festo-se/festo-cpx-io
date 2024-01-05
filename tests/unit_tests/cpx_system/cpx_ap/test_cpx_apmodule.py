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
        module.name = "code"

        module.position = 1
        assert repr(module) == "code (idx: 1, type: CpxApModule)"

    def test_configure(self):
        """Test configure"""
        module = CpxApModule()

        mocked_base = Mock()
        mocked_base.next_output_register = 0
        mocked_base.next_input_register = 0
        module.base = mocked_base
        module.information = CpxAp.ModuleInformation(
            module_code=0,
            module_class=1,
            communication_profiles=2,
            input_size=3,
            input_channels=4,
            output_size=5,
            output_channels=6,
            hw_version=7,
            fw_version="fw",
            serial_number="sn",
            product_key="pk",
            order_text="ot",
        )

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

        assert ret.fieldbus_serial_number == 131073
        assert ret.product_key == "\x01\x00\x02"
        assert ret.firmware_version == "\x01\x00\x02"
        assert ret.module_code == 131073
        assert ret.temp_asic == 2
        assert ret.logic_voltage == 2
        assert ret.load_voltage == 2
        assert ret.hw_version == 1
        assert ret.io_link_variant == "n.a."
        assert ret.operating_supply is False
