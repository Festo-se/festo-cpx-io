"""Contains tests for CpxAp4AiUI class"""
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI


class TestCpxAp4AiUI:
    "Test CpxAp4AiUI"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap4aiui = CpxAp4AiUI()

        # Assert
        assert isinstance(cpxap4aiui, CpxAp4AiUI)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap4aiui = CpxAp4AiUI()

        cpxap4aiui.base = Mock(
            read_reg_data=Mock(return_value=[0, 32767, 32768, 65535])
        )

        # Act
        channel_values = cpxap4aiui.read_channels()

        # Assert
        # signed int: values over 32767 are negative
        assert channel_values == [0, 32767, -32768, -1]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        cpxap4aiui = CpxAp4AiUI()

        cpxap4aiui.base = Mock(
            read_reg_data=Mock(return_value=[0, 32767, 32768, 65535])
        )
        # Act
        channel_values = [cpxap4aiui.read_channel(idx) for idx in range(4)]

        # Assert
        # signed int: values over 32767 are negative
        assert channel_values == [0, 32767, -32768, -1]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap4aiui = CpxAp4AiUI()

        cpxap4aiui.base = Mock(
            read_reg_data=Mock(return_value=[0, 32767, 32768, 65535])
        )

        # Act
        channel_values = [cpxap4aiui[idx] for idx in range(4)]

        # Assert
        # signed int: values over 32767 are negative
        assert channel_values == [0, 32767, -32768, -1]

    @pytest.mark.parametrize(
        "input_value, expected_value", [("C", 0), ("F", 1), ("K", 2)]
    )
    def configure_channel_temp_unit(self, input_value, expected_value):
        """Test configure_channel_temp_unit and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20032  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_temp_unit(0, input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", ["A", "1"])
    def test_configure_channel_temp_unit_raise_error(self, input_value):
        """Test configure_channel_temp_unit and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_temp_unit(0, input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_channel_temp_unit_wrong_channel(self, input_value):
        """Test configure_channel_temp_unit and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_temp_unit(input_value, "None")

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ("None", 0),
            ("-10-+10V", 1),
            ("-5-+5V", 2),
            ("0-10V", 3),
            ("1-5V", 4),
            ("0-20mA", 5),
            ("4-20mA", 6),
            ("0-500R", 7),
            ("PT100", 8),
            ("NI100", 9),
        ],
    )
    def configure_channel_range(self, input_value, expected_value):
        """Test configure_channel_range and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20043  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_range(0, input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", ["A", "1"])
    def test_configure_channel_range_raise_error(self, input_value):
        """Test configure_channel_range and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_range(0, input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_channel_range_wrong_channel(self, input_value):
        """Test configure_channel_range and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_range(input_value, "None")

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (-32768, -32768),
            (32767, 32767),
        ],
    )
    def test_configure_channel_limits_upper(self, input_value, expected_value):
        """Test configure_channel_limits and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20044  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_limits(0, upper=input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (-32768, -32768),
            (32767, 32767),
        ],
    )
    def test_configure_channel_limits_lower(self, input_value, expected_value):
        """Test configure_channel_limits_lower and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20045  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_limits(0, lower=input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (-32768, -32768),
            (32767, 32767),
        ],
    )
    def test_configure_channel_limits_both(self, input_value, expected_value):
        """Test configure_channel_limits_lower and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID_UPPER = 20044  # pylint: disable=invalid-name
        PARAMETER_ID_LOWER = 20045  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_limits(0, upper=input_value, lower=input_value)

        # Assert
        cpxap4aiui.base.write_parameter.has_calls(
            call(MODULE_POSITION, PARAMETER_ID_UPPER, 0, expected_value),
            call(MODULE_POSITION, PARAMETER_ID_LOWER, 0, expected_value),
            any_order=True,
        )

    @pytest.mark.parametrize("input_value", [-32769, 32768])
    def test_configure_channel_limits_raise_error_upper(self, input_value):
        """Test configure_channel_limits and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_limits(0, upper=input_value)

    @pytest.mark.parametrize("input_value", [-32769, 32768])
    def test_configure_channel_limits_raise_error_lower(self, input_value):
        """Test configure_channel_limits and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_limits(0, lower=input_value)

    @pytest.mark.parametrize("input_value", [-32769, 32768])
    def test_configure_channel_limits_raise_error_both(self, input_value):
        """Test configure_channel_limits and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_limits(0, lower=input_value, upper=input_value)

    def test_configure_channel_limits_raise_error_none(self):
        """Test configure_channel_limits and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_limits(0)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_channel_limits_wrong_channel(self, input_value):
        """Test configure_channel_limits and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_limits(input_value, 0)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (65535, 65535),
        ],
    )
    def test_configure_hysteresis_limit_monitoring(self, input_value, expected_value):
        """Test configure_hysteresis_limit_monitoring and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20046  # pylint: disable=invalid-name
        cpxap4aiui.configure_hysteresis_limit_monitoring(0, input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 65536])
    def test_configure_hysteresis_limit_monitoring_wrong_input(self, input_value):
        """Test configure_hysteresis_limit_monitoring and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_hysteresis_limit_monitoring(0, input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_hysteresis_limit_monitoring_wrong_channel(self, input_value):
        """Test configure_hysteresis_limit_monitoring and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_hysteresis_limit_monitoring(input_value, 0)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (15, 15),
        ],
    )
    def test_configure_channel_smoothing(self, input_value, expected_value):
        """Test configure_channel_smoothing and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20107  # pylint: disable=invalid-name
        cpxap4aiui.configure_channel_smoothing(0, input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 16])
    def test_configure_channel_smoothing_wrong_input(self, input_value):
        """Test configure_channel_smoothing and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_smoothing(0, input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_channel_smoothing_wrong_channel(self, input_value):
        """Test configure_channel_smoothing and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_channel_smoothing(input_value, 0)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, True),
            (False, False),
            (0, 0),
            (1, 1),
        ],
    )
    def test_configure_linear_scaling(self, input_value, expected_value):
        """Test configure_linear_scaling and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20111  # pylint: disable=invalid-name
        cpxap4aiui.configure_linear_scaling(0, input_value)

        # Assert
        cpxap4aiui.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [1, "A"])
    def test_configure_linear_scaling_wrong_input(self, input_value):
        """Test configure_linear_scaling and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(TypeError):
            cpxap4aiui.configure_linear_scaling(0, input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_linear_scaling_wrong_channel(self, input_value):
        """Test configure_linear_scaling and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4aiui = CpxAp4AiUI()
        cpxap4aiui.position = MODULE_POSITION

        cpxap4aiui.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4aiui.configure_linear_scaling(input_value, 0)
