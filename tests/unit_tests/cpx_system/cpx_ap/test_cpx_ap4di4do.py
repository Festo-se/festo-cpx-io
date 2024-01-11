"""Contains tests for CpxAp4Di4Do class"""
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.utils.boollist import boollist_to_int


class TestCpxAp4Di4Do:
    "Test CpxAp4Di4Do"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap4di4do = CpxAp4Di4Do()

        # Assert
        assert isinstance(cpxap4di4do, CpxAp4Di4Do)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        # return [input reg, output reg]
        cpxap4di4do.base.read_reg_data.side_effect = [[0xDEAD], [0xBEEF]]

        # Act
        channel_values = cpxap4di4do.read_channels()

        # Assert
        # first 4 inputs, then 4 outputs, always in lsb nibble
        assert channel_values == [True, False, True, True, True, True, True, True]

    def test_read_channel_correct_values_output_numbering_false(self):
        """Test read channel"""
        # Arrange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        cpxap4di4do.read_channels = Mock(return_value=[True, False] * 4)

        # Act
        channel_values = [cpxap4di4do.read_channel(idx) for idx in range(8)]

        # Assert
        assert channel_values == [True, False] * 4

    def test_read_channel_correct_values_output_numbering_true(self):
        """Test read channel"""
        # Arrange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        cpxap4di4do.read_channels = Mock(
            return_value=[False, False, False, False, True, False, True, False]
        )

        # Act
        channel_values = [
            cpxap4di4do.read_channel(idx, output_numbering=True) for idx in range(4)
        ]

        # Assert
        assert channel_values == [True, False, True, False]

    def test_read_channel_correct_values_output_numbering_true_error(self):
        """Test read channel"""
        # Arrange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        cpxap4di4do.read_channels = Mock(return_value=[True, False, True, False])

        # Act

        # Assert
        with pytest.raises(IndexError):
            cpxap4di4do.read_channel(4, output_numbering=True)

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        # return [input reg, output reg]
        cpxap4di4do.base.read_reg_data.side_effect = [[0xDEAD], [0xBEEF]] * 8

        # Act
        channel_values = [cpxap4di4do[idx] for idx in range(8)]

        # Assert
        # first 4 inputs, then 4 outputs, always in lsb nibble
        assert channel_values == [True, False, True, True, True, True, True, True]

    def test_write_channels_correct_values(self):
        """Test write channels"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.output_register = 0

        # Act
        bool_list = [False, True, False, True]
        data = boollist_to_int(bool_list)

        cpxap4di4do.write_channels(bool_list)

        # Assert
        cpxap4di4do.base.write_reg_data.assert_called_with(data, 0)

    def test_write_channels_too_long(self):
        """Test write channels, expect error"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(ValueError):
            cpxap4di4do.write_channels([1, 2, 3, 4, 5])

    def test_write_channels_too_short(self):
        """Test write channels, expect error"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(ValueError):
            cpxap4di4do.write_channels([1, 2, 3])

    def test_write_channels_wrong_type(self):
        """Test write channels, expect error"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(TypeError):
            cpxap4di4do.write_channels(0)

    def test_write_channel_true(self):
        """Test write channel"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap4di4do.output_register = 0

        # Act
        cpxap4di4do.write_channel(0, True)

        # Assert
        cpxap4di4do.base.write_reg_data.assert_called_with(0xBB, 0)

    def test_write_channel_false(self):
        """Test write channel"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap4di4do.output_register = 0

        # Act
        cpxap4di4do.write_channel(1, False)

        # Assert
        cpxap4di4do.base.write_reg_data.assert_called_with(0xB8, 0)

    def test_set_channel(self):
        """Test set channel"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.write_channel = Mock()

        # Act
        cpxap4di4do.set_channel(0)

        # Assert
        cpxap4di4do.write_channel.assert_called_with(0, True)

    def test_clear_channel(self):
        """Test clear channel"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.write_channel = Mock()

        # Act
        cpxap4di4do.clear_channel(0)

        # Assert
        cpxap4di4do.write_channel.assert_called_with(0, False)

    def test_toggle_channel(self):
        """Test toggle channel"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock(write_reg_data=Mock())
        cpxap4di4do.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        cpxap4di4do.write_channel = Mock()

        # Act
        cpxap4di4do.toggle_channel(0)

        # Assert
        cpxap4di4do.write_channel.assert_called_with(0, True)

    def test_set_item(self):
        """Test set item"""
        # Arange
        cpxap4di4do = CpxAp4Di4Do()

        cpxap4di4do.base = Mock()
        cpxap4di4do.write_channel = Mock()

        # Act
        cpxap4di4do[0] = True
        cpxap4di4do[1] = False
        cpxap4di4do[2] = True
        cpxap4di4do[3] = False

        # Assert
        cpxap4di4do.write_channel.assert_has_calls(
            [call(0, True), call(1, False), call(2, True), call(3, False)]
        )

    @pytest.mark.parametrize(
        "input_value, expected_value", [(0, 0), (1, 1), (2, 2), (3, 3)]
    )
    def test_configure_debounce_time(self, input_value, expected_value):
        """Test configure_debounce_time and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20014  # pylint: disable=invalid-name
        cpxap4di4do.configure_debounce_time(input_value)

        # Assert
        cpxap4di4do.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_raise_error(self, input_value):
        """Test configure_debounce_time and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4di4do.configure_debounce_time(input_value)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (1, 1), (2, 2)])
    def test_configure_monitoring_load_supply(self, input_value, expected_value):
        """Test configure_monitoring_load_supply and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20022  # pylint: disable=invalid-name
        cpxap4di4do.configure_monitoring_load_supply(input_value)

        # Assert
        cpxap4di4do.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4di4do.configure_monitoring_load_supply(input_value)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (1, 1)])
    def test_configure_behaviour_in_fail_state(self, input_value, expected_value):
        """Test configure_behaviour_in_fail_state and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20052  # pylint: disable=invalid-name
        cpxap4di4do.configure_behaviour_in_fail_state(input_value)

        # Assert
        cpxap4di4do.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 2])
    def test_configure_behaviour_in_fail_state_raise_error(self, input_value):
        """Test configure_behaviour_in_fail_state and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4di4do = CpxAp4Di4Do()
        cpxap4di4do.position = MODULE_POSITION

        cpxap4di4do.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4di4do.configure_behaviour_in_fail_state(input_value)
