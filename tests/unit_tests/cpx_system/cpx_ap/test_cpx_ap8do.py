"""Contains tests for CpxAp8Do class"""
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_ap.ap8do import CpxAp8Do
from cpx_io.utils.boollist import boollist_to_int


class TestCpxAp8Do:
    "Test CpxAp8Do"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap8do = CpxAp8Do()

        # Assert
        assert isinstance(cpxap8do, CpxAp8Do)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))

        # Act
        channel_values = cpxap8do.read_channels()

        # Assert
        assert channel_values == [False, True, False, True, True, True, False, True]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))

        # Act
        channel_values = [cpxap8do.read_channel(idx) for idx in range(8)]

        # Assert
        assert channel_values == [False, True, False, True, True, True, False, True]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))

        # Act
        channel_values = [cpxap8do[idx] for idx in range(8)]

        # Assert
        assert channel_values == [False, True, False, True, True, True, False, True]

    def test_write_channels_correct_values(self):
        """Test write channels"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.output_register = 0

        # Act
        bool_list = [False, True, False, True, True, True, False, True]
        data = boollist_to_int(bool_list)

        cpxap8do.write_channels(bool_list)

        # Assert
        cpxap8do.base.write_reg_data.assert_called_with(data, 0)

    def test_write_channels_wrong_length(self):
        """Test write channels, expect error"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(ValueError):
            cpxap8do.write_channels([1, 2, 3, 4, 5, 6, 7])

    def test_write_channels_wrong_type(self):
        """Test write channels, expect error"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(TypeError):
            cpxap8do.write_channels(0)

    def test_write_channel_true(self):
        """Test write channel"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap8do.output_register = 0

        # Act
        cpxap8do.write_channel(0, True)

        # Assert
        cpxap8do.base.write_reg_data.assert_called_with(0xBB, 0)

    def test_set_item(self):
        """Test set item"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock()
        cpxap8do.write_channel = Mock()

        # Act
        cpxap8do[0] = True
        cpxap8do[1] = False
        cpxap8do[2] = True
        cpxap8do[3] = False

        # Assert
        cpxap8do.write_channel.assert_has_calls(
            [call(0, True), call(1, False), call(2, True), call(3, False)]
        )

    def test_write_channel_false(self):
        """Test write channel"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap8do.output_register = 0

        # Act
        cpxap8do.write_channel(1, False)

        # Assert
        cpxap8do.base.write_reg_data.assert_called_with(0xB8, 0)

    def test_set_channel(self):
        """Test set channel"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.write_channel = Mock()

        # Act
        cpxap8do.set_channel(0)

        # Assert
        cpxap8do.write_channel.assert_called_with(0, True)

    def test_clear_channel(self):
        """Test clear channel"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.write_channel = Mock()

        # Act
        cpxap8do.clear_channel(0)

        # Assert
        cpxap8do.write_channel.assert_called_with(0, False)

    def test_toggle_channel(self):
        """Test toggle channel"""
        # Arange
        cpxap8do = CpxAp8Do()

        cpxap8do.base = Mock(write_reg_data=Mock())
        cpxap8do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap8do.write_channel = Mock()

        # Act
        cpxap8do.toggle_channel(0)

        # Assert
        cpxap8do.write_channel.assert_called_with(0, True)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (1, 1), (2, 2)])
    def test_configure_monitoring_load_supply(self, input_value, expected_value):
        """Test configure_monitoring_load_supply and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap8do = CpxAp8Do()
        cpxap8do.position = MODULE_POSITION

        cpxap8do.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20022  # pylint: disable=invalid-name
        cpxap8do.configure_monitoring_load_supply(input_value)

        # Assert
        cpxap8do.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap8do = CpxAp8Do()
        cpxap8do.position = MODULE_POSITION

        cpxap8do.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap8do.configure_monitoring_load_supply(input_value)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (1, 1)])
    def test_configure_behaviour_in_fail_state(self, input_value, expected_value):
        """Test configure_behaviour_in_fail_state and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap8do = CpxAp8Do()
        cpxap8do.position = MODULE_POSITION

        cpxap8do.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20052  # pylint: disable=invalid-name
        cpxap8do.configure_behaviour_in_fail_state(input_value)

        # Assert
        cpxap8do.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 2])
    def test_configure_behaviour_in_fail_state_raise_error(self, input_value):
        """Test configure_behaviour_in_fail_state and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap8do = CpxAp8Do()
        cpxap8do.position = MODULE_POSITION

        cpxap8do.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap8do.configure_behaviour_in_fail_state(input_value)
