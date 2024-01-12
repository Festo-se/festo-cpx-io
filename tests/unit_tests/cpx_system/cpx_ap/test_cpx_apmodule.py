"""Contains tests for TestCpxApModule class"""
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule


class TestCpxApModule:
    "Test CpxApModule"

    def test_constructor_attributes_none(self):
        """Test constructor"""
        # Arrange

        # Act
        module = CpxApModule()

        # Assert
        assert module.base is None
        assert module.position is None
        assert module.information is None
        assert module.output_register is None
        assert module.input_register is None

    def test_configure(self):
        """Test configure"""
        # Arrange
        module = CpxApModule()
        module.information = Mock(input_size=3, output_size=5)
        mocked_base = Mock(next_output_register=0, next_input_register=0, modules=[])

        # Act
        MODULE_POSITION = 1
        module.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert module.position == MODULE_POSITION

    def test_update_information(self):
        """Test update_information"""
        # Arrange
        module = CpxApModule()
        module.information = {}

        # Act
        module.update_information({"test": "information"})

        # Assert
        assert module.information == {"test": "information"}

    def test_read_ap_parameter(self):
        """Test read_ap_parameter"""
        # Arrange
        module = CpxApModule()

        module.base = Mock(read_parameter=Mock(return_value=[0x01, 0x02]))

        # Act
        ret = module.read_ap_parameter()

        # Assert
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

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        module = CpxApModule()
        module.name = "code"
        module.position = 1

        # Act
        module_repr = repr(module)

        # Assert
        assert module_repr == "code (idx: 1, type: CpxApModule)"
