"""Contains tests for CpxAp4Di class"""
import pytest
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di


class TestCpxAp4Di:
    "Test CpxAp4Di"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap4di = CpxAp4Di()

        # Assert
        assert isinstance(cpxap4di, CpxAp4Di)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap4di = CpxAp4Di()

        cpxap4di.base = Mock(read_reg_data=Mock(return_value=[0xFA]))

        # Act
        channel_values = cpxap4di.read_channels()

        # Assert
        assert channel_values == [False, True, False, True]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        cpxap4di = CpxAp4Di()

        cpxap4di.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

        # Act
        channel_values = [cpxap4di.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap4di = CpxAp4Di()

        cpxap4di.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

        # Act
        channel_values = [cpxap4di[idx] for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

    @pytest.mark.parametrize("input_value, expected_value", [(1, 1), (2, 2), (3, 3)])
    def test_configure_debounce_time_successful_configuration(
        self, input_value, expected_value
    ):
        """Test configure_debounce_time and expect success"""
        # Arrange
        MODULE_POSITION = 1

        cpxap4di = CpxAp4Di()
        cpxap4di.position = MODULE_POSITION

        cpxap4di.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20014
        cpxap4di.configure_debounce_time(input_value)

        # Assert
        cpxap4di.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_raise_error(self, input_value):
        # Arrange
        MODULE_POSITION = 1

        cpxap4di = CpxAp4Di()
        cpxap4di.position = MODULE_POSITION

        cpxap4di.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4di.configure_debounce_time(input_value)
