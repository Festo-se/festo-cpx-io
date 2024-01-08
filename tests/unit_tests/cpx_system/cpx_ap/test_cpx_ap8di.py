"""Contains tests for CpxAp8Di class"""
import pytest
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di


class TestCpxAp8Di:
    "Test CpxAp8Di"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap8di = CpxAp8Di()

        # Assert
        assert isinstance(cpxap8di, CpxAp8Di)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap8di = CpxAp8Di()

        cpxap8di.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

        # Act
        channel_values = cpxap8di.read_channels()

        # Assert
        assert channel_values == [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        ]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        cpxap8di = CpxAp8Di()

        cpxap8di.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

        # Act
        channel_values = [cpxap8di.read_channel(idx) for idx in range(8)]

        # Assert
        assert channel_values == [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        ]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap8di = CpxAp8Di()

        cpxap8di.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

        # Act
        channel_values = [cpxap8di[idx] for idx in range(8)]

        # Assert
        assert channel_values == [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        ]

    @pytest.mark.parametrize("input_value, expected_value", [(1, 1), (2, 2), (3, 3)])
    def test_configure_debounce_time_successful_configuration(
        self, input_value, expected_value
    ):
        """Test configure_debounce_time and expect success"""
        # Arrange
        MODULE_POSITION = 1

        cpxap8di = CpxAp8Di()
        cpxap8di.position = MODULE_POSITION

        cpxap8di.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20014
        cpxap8di.configure_debounce_time(input_value)

        # Assert
        cpxap8di.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_raise_error(self, input_value):
        # Arrange
        MODULE_POSITION = 1

        cpxap8di = CpxAp8Di()
        cpxap8di.position = MODULE_POSITION

        cpxap8di.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap8di.configure_debounce_time(input_value)
