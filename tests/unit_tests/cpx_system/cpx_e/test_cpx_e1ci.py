"""Contains tests for cpx_e1ci class"""

from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci
from cpx_io.cpx_system.cpx_e.cpx_e_enums import (
    DigInDebounceTime,
    IntegrationTime,
    SignalType,
    SignalEvaluation,
    LatchingEvent,
)
from cpx_io.cpx_system.cpx_dataclasses import SystemEntryRegisters


class TestCpxE1Ci:
    """Test cpx-e-16di"""

    def test_constructor_default(self):
        """Test default constructor"""
        # Arrange

        # Act
        cpxe1ci = CpxE1Ci()

        # Assert
        assert cpxe1ci.base is None
        assert cpxe1ci.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        mocked_base = Mock(next_input_register=0, next_output_register=0, modules=[])

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        cpxe1ci.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe1ci.base == mocked_base
        assert cpxe1ci.position == MODULE_POSITION

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=b"\xAA\xAA"))

        # Act
        status = cpxe1ci.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_value(self):
        """Test read channels"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=b"\xFE\xCA\xEF\xBE"))

        # Act
        value = cpxe1ci.read_value()

        # Assert
        assert value == 0xBEEFCAFE
        cpxe1ci.base.read_reg_data.assert_called_with(
            cpxe1ci.system_entry_registers.inputs, length=2
        )

    def test_read_latching_value(self):
        """Test read_latching_value"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=b"\xFE\xCA\xEF\xBE"))

        # Act
        latching_value = cpxe1ci.read_latching_value()

        # Assert
        assert latching_value == 0xBEEFCAFE
        cpxe1ci.base.read_reg_data.assert_called_with(
            cpxe1ci.system_entry_registers.inputs + 2, length=2
        )

    def test_read_status_word(self):
        """Test read_status_word"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=b"\xAA\xAA"))

        # Act
        sw = cpxe1ci.read_status_word()

        # Assert
        assert sw.di0 is False
        assert sw.di1 is True
        assert sw.di2 is False
        assert sw.di3 is True
        assert sw.latchin_missed is True
        assert sw.latching_set is False
        assert sw.lower_cl_exceeded is False
        assert sw.upper_cl_exceeded is True
        assert sw.counting_direction is False
        assert sw.counter_blocked is True
        assert sw.counter_set is False
        assert sw.enable_di2 is True
        assert sw.enable_zero is False
        assert sw.speed_measurement is True

        cpxe1ci.base.read_reg_data.assert_called_with(
            cpxe1ci.system_entry_registers.inputs + 4
        )

    def test_read_process_data(self):
        """Test read_process_data"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=b"\xAA\xAA"))

        # Act
        pd = cpxe1ci.read_process_data()

        # Assert
        assert pd.enable_setting_di2 is False
        assert pd.enable_setting_zero is True
        assert pd.set_counter is False
        assert pd.block_counter is True
        assert pd.overrun_cl_confirm is False
        assert pd.speed_measurement is True
        assert pd.confirm_latching is False
        assert pd.block_latching is True

        cpxe1ci.base.read_reg_data.assert_called_with(
            cpxe1ci.system_entry_registers.inputs + 6
        )

    def test_write_process_data_setting_di2(self):
        """Test write_process_data"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(
            read_reg_data=Mock(return_value=b"\xAA"), write_reg_data=Mock()
        )

        # Act
        cpxe1ci.write_process_data(enable_setting_di2=True)

        # Assert
        cpxe1ci.base.write_reg_data.assert_called_with(
            b"\xAB", cpxe1ci.system_entry_registers.outputs
        )

    def test_write_process_data_block_latching(self):
        """Test write_process_data"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe1ci.base = Mock(
            read_reg_data=Mock(return_value=b"\xAA"), write_reg_data=Mock()
        )

        # Act
        cpxe1ci.write_process_data(block_latching=False)

        # Assert
        cpxe1ci.base.write_reg_data.assert_called_with(
            b"\x2A", cpxe1ci.system_entry_registers.outputs
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, (4828 + 64 + 6, 0xA8)),
            (1, (4828 + 64 + 6, 0xA9)),
            (2, (4828 + 64 + 6, 0xAA)),
            (SignalType.ENCODER_5V_DIFFERENTIAL, (4828 + 64 + 6, 0xA8)),
            (SignalType.ENCODER_5V_SINGLE_ENDED, (4828 + 64 + 6, 0xA9)),
            (SignalType.ENCODER_24V_SINGLE_ENDED, (4828 + 64 + 6, 0xAA)),
        ],
    )
    def test_configure_signal_type(self, input_value, expected_value):
        """Test configure_signal_type"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_type(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_signal_type_raise_error(self, input_value):
        """Test configure_signal_type"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_type(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, (4828 + 64 + 7, 0xA8)),
            (3, (4828 + 64 + 7, 0xAB)),
            (SignalEvaluation.INCREMENTAL_SINGLE_EVALUATION, (4828 + 64 + 7, 0xA8)),
            (SignalEvaluation.PULSE_GENERATOR, (4828 + 64 + 7, 0xAB)),
        ],
    )
    def test_configure_signal_evaluation(self, input_value, expected_value):
        """Test configure_signal_evaluation"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_evaluation(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_signal_evaluation_raise_error(self, input_value):
        """Test configure_signal_evaluation"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_evaluation(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(True, (4828 + 64 + 8, 0xAB)), (False, (4828 + 64 + 8, 0xAA))],
    )
    def test_configure_monitoring_of_cable_brake(self, input_value, expected_value):
        """Test configure_monitoring_of_cable_brake"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_cable_brake(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(True, (4828 + 64 + 9, 0xAB)), (False, (4828 + 64 + 9, 0xAA))],
    )
    def test_configure_monitoring_of_tracking_error(self, input_value, expected_value):
        """Test configure_monitoring_of_cable_brake enable"""
        # Arrange
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_tracking_error(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(True, (4828 + 64 + 10, 0xAB)), (False, (4828 + 64 + 10, 0xAA))],
    )
    def test_configure_monitoring_of_zero_pulse(self, input_value, expected_value):
        """Test configure_monitoring_of_zero_pulse"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_zero_pulse(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, [call(4828 + 64 + 11, 0), call(4828 + 64 + 12, 0)]),
            (65535, [call(4828 + 64 + 11, 0xFF), call(4828 + 64 + 12, 0xFF)]),
            (0xCAFE, [call(4828 + 64 + 11, 0xFE), call(4828 + 64 + 12, 0xCA)]),
        ],
    )
    def test_configure_pulses_per_zero_pulse(self, input_value, expected_value):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act
        cpxe1ci.configure_pulses_per_zero_pulse(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize("input_value", [-1, 65536])
    def test_configure_pulses_per_zero_pulse_raise_error(self, input_value):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_pulses_per_zero_pulse(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(True, (4828 + 64 + 13, 0xAB)), (False, (4828 + 64 + 13, 0xAA))],
    )
    def test_configure_latching_signal(self, input_value, expected_value):
        """Test configure_latching_signal"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_signal(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (1, (4828 + 64 + 14, 0xA9)),
            (3, (4828 + 64 + 14, 0xAB)),
            (LatchingEvent.RISING_EDGE, (4828 + 64 + 14, 0xA9)),
            (LatchingEvent.BOTH_EDGES, (4828 + 64 + 14, 0xAB)),
        ],
    )
    def test_configure_latching_event(self, input_value, expected_value):
        """Test configure_latching_event"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_event(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [0, 4])
    def test_configure_latching_event_raise_error(self, input_value):
        """Test configure_latching_event"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_latching_event(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(True, (4828 + 64 + 15, 0xAB)), (False, (4828 + 64 + 15, 0xAA))],
    )
    def test_configure_latching_response(self, input_value, expected_value):
        """Test configure_latching_response"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_response(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                0,
                [
                    call(4828 + 64 + 16, 0),
                    call(4828 + 64 + 17, 0),
                    call(4828 + 64 + 18, 0),
                    call(4828 + 64 + 19, 0),
                ],
            ),
            (
                2**32 - 1,
                [
                    call(4828 + 64 + 16, 0xFF),
                    call(4828 + 64 + 17, 0xFF),
                    call(4828 + 64 + 18, 0xFF),
                    call(4828 + 64 + 19, 0xFF),
                ],
            ),
            (
                0xCAFEBEEF,
                [
                    call(4828 + 64 + 16, 0xEF),
                    call(4828 + 64 + 17, 0xBE),
                    call(4828 + 64 + 18, 0xFE),
                    call(4828 + 64 + 19, 0xCA),
                ],
            ),
        ],
    )
    def test_configure_upper_counter_limit(self, input_value, expected_value):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act
        cpxe1ci.configure_upper_counter_limit(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize("input_value", [-1, 2**32])
    def test_configure_upper_counter_limit_raise_error(self, input_value):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_upper_counter_limit(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                0,
                [
                    call(4828 + 64 + 20, 0),
                    call(4828 + 64 + 21, 0),
                    call(4828 + 64 + 22, 0),
                    call(4828 + 64 + 23, 0),
                ],
            ),
            (
                2**32 - 1,
                [
                    call(4828 + 64 + 20, 0xFF),
                    call(4828 + 64 + 21, 0xFF),
                    call(4828 + 64 + 22, 0xFF),
                    call(4828 + 64 + 23, 0xFF),
                ],
            ),
            (
                0xCAFEBEEF,
                [
                    call(4828 + 64 + 20, 0xEF),
                    call(4828 + 64 + 21, 0xBE),
                    call(4828 + 64 + 22, 0xFE),
                    call(4828 + 64 + 23, 0xCA),
                ],
            ),
        ],
    )
    def test_configure_lower_counter_limit(self, input_value, expected_value):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act
        cpxe1ci.configure_lower_counter_limit(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize("input_value", [-1, 2**32])
    def test_configure_lower_counter_limit_raise_error(self, input_value):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_lower_counter_limit(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                0,
                [
                    call(4828 + 64 + 24, 0),
                    call(4828 + 64 + 25, 0),
                    call(4828 + 64 + 26, 0),
                    call(4828 + 64 + 27, 0),
                ],
            ),
            (
                2**32 - 1,
                [
                    call(4828 + 64 + 24, 0xFF),
                    call(4828 + 64 + 25, 0xFF),
                    call(4828 + 64 + 26, 0xFF),
                    call(4828 + 64 + 27, 0xFF),
                ],
            ),
            (
                0xCAFEBEEF,
                [
                    call(4828 + 64 + 24, 0xEF),
                    call(4828 + 64 + 25, 0xBE),
                    call(4828 + 64 + 26, 0xFE),
                    call(4828 + 64 + 27, 0xCA),
                ],
            ),
        ],
    )
    def test_configure_load_value(self, input_value, expected_value):
        """Test configure_load_value"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act
        cpxe1ci.configure_load_value(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize("input_value", [-1, 2**32 + 1])
    def test_configure_load_value_raise_error(self, input_value):
        """Test configure_load_value"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_load_value(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, (4828 + 64 + 28, 0xA8)),
            (2, (4828 + 64 + 28, 0xAA)),
            (DigInDebounceTime.T_20US, (4828 + 64 + 28, 0xA8)),
            (DigInDebounceTime.T_3MS, (4828 + 64 + 28, 0xAA)),
        ],
    )
    def test_configure_debounce_time_for_digital_inputs(
        self, input_value, expected_value
    ):
        """Test configure_debounce_time_for_digital_inputs"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_debounce_time_for_digital_inputs(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_debounce_time_for_digital_inputs_raise_error(self, input_value):
        """Test configure_debounce_time_for_digital_inputs"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_debounce_time_for_digital_inputs(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, (4828 + 64 + 29, 0xA8)),
            (2, (4828 + 64 + 29, 0xAA)),
            (IntegrationTime.T_1MS, (4828 + 64 + 29, 0xA8)),
            (IntegrationTime.T_100MS, (4828 + 64 + 29, 0xAA)),
        ],
    )
    def test_configure_integration_time_for_speed_measurement(
        self, input_value, expected_value
    ):
        """Test configure_integration_time_for_speed_measurement"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_integration_time_for_speed_measurement(input_value)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_integration_time_for_speed_measurement_raise_error(
        self, input_value
    ):
        """Test configure_integration_time_for_speed_measurement"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_integration_time_for_speed_measurement(input_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxe1ci = CpxE1Ci()
        cpxe1ci.position = 1
        cpxe1ci.base = Mock()

        # Act
        module_repr = repr(cpxe1ci)

        # Assert
        assert module_repr == "cpxe1ci (idx: 1, type: CpxE1Ci)"
