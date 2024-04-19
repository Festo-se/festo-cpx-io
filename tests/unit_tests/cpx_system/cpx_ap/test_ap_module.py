"""Contains tests for ApModule class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.ap_module import ApModule


class TestApModule:
    "Test ApModule"
    # TODO: fixture for digital, analog, io-link, ep module

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange
        module_information = ...
        input_channels = []
        output_channels = []
        parameters = []

        # Act
        module = ApModule()

        # Assert
        assert isinstance(module, ApModule)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        module = ApModule()
        ret_data = b"\xFA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == [False, True, False, True]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        module = ApModule()
        ret_data = b"\xAA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [module.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        module = ApModule()
        ret_data = b"\xAA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [module[idx] for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (DebounceTime.T_100US, 0),
            (DebounceTime.T_3MS, 1),
            (DebounceTime.T_10MS, 2),
            (DebounceTime.T_20MS, 3),
        ],
    )
    def test_configure_debounce_time_successful_configuration(
        self, input_value, expected_value
    ):
        """Test configure_debounce_time and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        module = ApModule()
        module.position = MODULE_POSITION

        module.base = Mock(write_parameter=Mock())

        # Act
        module.configure_debounce_time(input_value)

        # Assert
        module.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["InputDebounceTime"],
            expected_value,
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_raise_error(self, input_value):
        """Test configure_debounce_time and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        module = ApModule()
        module.position = MODULE_POSITION

        module.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            module.configure_debounce_time(input_value)
