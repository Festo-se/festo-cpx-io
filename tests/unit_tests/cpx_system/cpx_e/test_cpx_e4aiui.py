"""Contains tests for cpx_e4aiui class"""
from unittest.mock import Mock, call

import pytest

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI


class TestCpxE4AiUI:
    """Test cpx-e-4aiui"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxe4aiui = CpxE4AiUI()

        # Assert
        assert cpxe4aiui.base is None
        assert cpxe4aiui.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        mocked_base = Mock(next_input_register=0)

        # Act
        MODULE_POSITION = 1
        cpxe4aiui.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe4aiui.base == mocked_base
        assert cpxe4aiui.position == MODULE_POSITION

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.input_register = 0
        cpxe4aiui.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

        # Act
        status = cpxe4aiui.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_channel_0_to_3(self):
        """Test read channels"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.base = Mock(read_reg_data=Mock(return_value=[0, 1000, 2000, 3000]))

        # Act
        channel_values = [cpxe4aiui.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aiui.base.read_reg_data.assert_called_with(
            cpxe4aiui.input_register, length=4
        )

    def test_getitem_0_to_3(self):
        """Test get item"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.base = Mock(read_reg_data=Mock(return_value=[0, 1000, 2000, 3000]))

        # Act
        channel_values = [cpxe4aiui[idx] for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aiui.base.read_reg_data.assert_called_with(
            cpxe4aiui.input_register, length=4
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((None, None), (4892, 0xAA)),
            ((True, None), (4892, 0xAB)),
            ((None, False), (4892, 0x2A)),
            ((True, False), (4892, 0x2B)),
        ],
    )
    def test_configure_diagnostics(self, input_value, expected_value):
        """Test diagnostics"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_diagnostics(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4893, 0xAB)),
            (False, (4893, 0xAA)),
        ],
    )
    def test_configure_power_reset(self, input_value, expected_value):
        """Test power reset"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_power_reset(input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4898, 0xAB)),
            (False, (4898, 0xAA)),
        ],
    )
    def test_configure_data_format(self, input_value, expected_value):
        """Test data format"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_data_format(input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4898, 0xAA)),
            (False, (4898, 0x8A)),
        ],
    )
    def test_configure_sensor_supply(self, input_value, expected_value):
        """Test sensor supply"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_sensor_supply(input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4898, 0xEA)),
            (False, (4898, 0xAA)),
        ],
    )
    def test_configure_diagnostics_overload(self, input_value, expected_value):
        """Test diagnostics overload"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_diagnostics_overload(input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4898, 0xAA)),
            (False, (4898, 0x2A)),
        ],
    )
    def test_configure_behaviour_overload(self, input_value, expected_value):
        """Test behaviour overload"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_behaviour_overload(input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, None), (4892 + 7, 0x00)),
            ((0, 1), (4892 + 7, 0x00)),
            ((0xFE, None), (4892 + 7, 0xFE)),
            ((None, 0xFE), (4892 + 8, 0xFE)),
        ],
    )
    def test_configure_hysteresis_limit_monitoring(self, input_value, expected_value):
        """Test hysteresis limit monitoring"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe4aiui.configure_hysteresis_limit_monitoring(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value", [(-1, None), (None, 32768), (0, -1), (None, None)]
    )
    def test_configure_hysteresis_limit_monitoring_raise_error(self, input_value):
        """Test hysteresis limit monitoring"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_hysteresis_limit_monitoring(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True, None), (4892 + 9, 0xAB)),
            ((0, False, None), (4892 + 9, 0xAA)),
            ((1, None, True), (4892 + 10, 0xAA)),
            ((1, None, False), (4892 + 10, 0xA8)),
            ((2, True, False), (4892 + 11, 0xA9)),
            ((2, False, True), (4892 + 11, 0xAA)),
            ((3, None, None), (4892 + 12, 0xAA)),
        ],
    )
    def test_configure_channel_diagnostics_limits(self, input_value, expected_value):
        """Test configure_channel_diagnostics_limits"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_diagnostics_limits(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_channel_diagnostics_limits_raise_error(self, input_value):
        """Test configure_channel_diagnostics_limits"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_diagnostics_limits(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 9, 0xAE)),
            ((0, False), (4892 + 9, 0xAA)),
            ((1, True), (4892 + 10, 0xAE)),
            ((1, False), (4892 + 10, 0xAA)),
            ((2, True), (4892 + 11, 0xAE)),
            ((2, False), (4892 + 11, 0xAA)),
            ((3, True), (4892 + 12, 0xAE)),
            ((3, False), (4892 + 12, 0xAA)),
        ],
    )
    def test_configure_channel_diagnostics_wire_break(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_wire_break"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_diagnostics_wire_break(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [(-1, True), (4, False)])
    def test_configure_channel_diagnostics_wire_break_raise_error(self, input_value):
        """Test configure_channel_diagnostics_wire_break"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_diagnostics_wire_break(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 9, 0xAA)),
            ((0, False), (4892 + 9, 0xA2)),
            ((1, True), (4892 + 10, 0xAA)),
            ((1, False), (4892 + 10, 0xA2)),
            ((2, True), (4892 + 11, 0xAA)),
            ((2, False), (4892 + 11, 0xA2)),
            ((3, True), (4892 + 12, 0xAA)),
            ((3, False), (4892 + 12, 0xA2)),
        ],
    )
    def test_configure_channel_diagnostics_underflow_overflow(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_underflow_overflow"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_diagnostics_underflow_overflow(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [(-1, True), (4, False)])
    def test_configure_channel_diagnostics_underflow_overflow_raise_error(
        self, input_value
    ):
        """Test configure_channel_diagnostics_underflow_overflow"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_diagnostics_underflow_overflow(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 9, 0xAA)),
            ((0, False), (4892 + 9, 0x2A)),
            ((1, True), (4892 + 10, 0xAA)),
            ((1, False), (4892 + 10, 0x2A)),
            ((2, True), (4892 + 11, 0xAA)),
            ((2, False), (4892 + 11, 0x2A)),
            ((3, True), (4892 + 12, 0xAA)),
            ((3, False), (4892 + 12, 0x2A)),
        ],
    )
    def test_configure_channel_diagnostics_parameter_error(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_diagnostics_parameter_error(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [(-1, True), (4, False)])
    def test_configure_channel_diagnostics_parameter_error_raise_error(
        self, input_value
    ):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_diagnostics_parameter_error(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, "0-10V"), (4892 + 13, 0xA1)),
            ((1, "4-20mA"), (4892 + 13, 0x6A)),
            ((2, "None"), (4892 + 14, 0xA0)),
            ((3, "0-10VoU"), (4892 + 14, 0x8A)),
        ],
    )
    def test_configure_channel_range(self, input_value, expected_value):
        """Test channel range"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_range(*input_value)  # 0001

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [(0, "not_implemented"), (4, "None")])
    def test_configure_channel_range_raise_error(self, input_value):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_range(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, 0), (4892 + 15, 0xA0)),
            ((1, 2), (4892 + 15, 0x2A)),
            ((2, 10), (4892 + 16, 0xAA)),
            ((3, 15), (4892 + 16, 0xFA)),
        ],
    )
    def test_configure_channel_smoothing(self, input_value, expected_value):
        """Test channel smoothing"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aiui.configure_channel_smoothing(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [(0, 16), (4, 0)])
    def test_configure_channel_smoothing_raise_error(self, input_value):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_smoothing(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                (0, -32000, None),
                [call(4892 + 25, -32000 & 0xFF), call(4892 + 26, (-32000 >> 8) & 0xFF)],
            ),
            (
                (0, None, 32000),
                [call(4892 + 17, 32000 & 0xFF), call(4892 + 18, (32000 >> 8) & 0xFF)],
            ),
            (
                (0, -32000, 32000),
                [
                    call(4892 + 17, 32000 & 0xFF),
                    call(4892 + 18, (32000 >> 8) & 0xFF),
                    call(4892 + 25, -32000 & 0xFF),
                    call(4892 + 26, (-32000 >> 8) & 0xFF),
                ],
            ),
        ],
    )
    def test_configure_channel_limits(self, input_value, expected_value):
        """Test configure_channel_limits"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock(write_function_number=Mock())

        # Act
        cpxe4aiui.configure_channel_limits(*input_value)

        # Assert
        cpxe4aiui.base.write_function_number.assert_has_calls(expected_value)

    @pytest.mark.parametrize(
        "input_value", [(0, None, 50000), (0, -50000, None), (4, None, 0)]
    )
    def test_configure_channel_limits_raise_error(self, input_value):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1
        cpxe4aiui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_limits(*input_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxe4aiui = CpxE4AiUI()
        cpxe4aiui.position = 1

        # Act
        module_repr = repr(cpxe4aiui)

        # Assert
        assert module_repr == "cpxe4aiui (idx: 1, type: CpxE4AiUI)"
