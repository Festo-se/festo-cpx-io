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
        MODULE_POSITION = 1  # pylint: disable=invalid-name
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

        module.base = Mock(read_parameter=Mock(return_value=131073))

        # Act
        ret = module.read_ap_parameter()

        # Assert
        # since the real read_parameter would return values dependent on the
        # parameter, this test only shows mostly, that all ap parameters are included
        assert ret.fieldbus_serial_number == 131073
        assert ret.product_key == 131073
        assert ret.firmware_version == 131073
        assert ret.module_code == 131073
        assert ret.temp_asic == 131073
        assert ret.logic_voltage == 131.073
        assert ret.load_voltage == 131.073
        assert ret.hw_version == 131073
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
