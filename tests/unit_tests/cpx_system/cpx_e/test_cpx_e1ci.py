"""Contains tests for cpx_e1ci class"""
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci


class TestCpxE1Ci:
    """Test cpx-e-16di"""

    def test_default_constructor(self):
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
        cpx_e = CpxE()

        # Act
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Assert
        assert cpxe1ci.position == 1

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

        # Act
        status = cpxe1ci.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_value(self):
        """Test read channels"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=[0xCAFE, 0xBEEF]))

        # Act
        value = cpxe1ci.read_value()

        # Assert
        assert value == 0xBEEFCAFE
        cpxe1ci.base.read_reg_data.assert_called_with(cpxe1ci.input_register, length=2)

    def test_read_latching_value(self):
        """Test read_latching_value"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=[0xCAFE, 0xBEEF]))

        # Act
        latching_value = cpxe1ci.read_latching_value()

        # Assert
        assert latching_value == 0xBEEFCAFE
        cpxe1ci.base.read_reg_data.assert_called_with(
            cpxe1ci.input_register + 2, length=2
        )

    def test_read_status_word(self):
        """Test read_status_word"""
        # Arramge
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

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

        cpxe1ci.base.read_reg_data.assert_called_with(cpxe1ci.input_register + 4)

    def test_read_process_data(self):
        """Test read_process_data"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(read_reg_data=Mock(return_value=[0xAA]))

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

        cpxe1ci.base.read_reg_data.assert_called_with(cpxe1ci.input_register + 6)

    def test_write_process_data_setting_di2_true(self):
        """Test write_process_data"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_reg_data=Mock(return_value=[0xAA]), write_reg_data=Mock()
        )

        cpxe1ci.write_process_data(enable_setting_di2=True)
        cpxe1ci.base.write_reg_data.assert_called_with(0xAB, cpxe1ci.output_register)

    def test_write_process_data_block_latching_false(self):
        """Test write_process_data"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_reg_data=Mock(return_value=[0xAA]), write_reg_data=Mock()
        )

        cpxe1ci.write_process_data(block_latching=False)
        cpxe1ci.base.write_reg_data.assert_called_with(0x2A, cpxe1ci.output_register)

    def test_configure_signal_type_0(self):
        """Test configure_signal_type"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_type(0)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 6, 0xA8)

    def test_configure_signal_type_3(self):
        """Test configure_signal_type"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_type(3)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 6, 0xAB)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_signal_type_raise_error(self, input_value):
        """Test configure_signal_type"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_type(input_value)

    def test_configure_signal_evaluation_0(self):
        """Test configure_signal_evaluation"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_evaluation(0)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 7, 0xA8)

    def test_configure_signal_evaluation_3(self):
        """Test configure_signal_evaluation"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_signal_evaluation(3)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 7, 0xAB)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_signal_evaluation_raise_error(self, input_value):
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_evaluation(input_value)

    def test_configure_monitoring_of_cable_brake_true(self):
        """Test configure_monitoring_of_cable_brake"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_cable_brake(True)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 8, 0xAB)

    def test_configure_monitoring_of_cable_brake_false(self):
        """Test configure_monitoring_of_cable_brake"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_cable_brake(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 8, 0xAA)

    def test_configure_monitoring_of_tracking_error_true(self):
        """Test configure_monitoring_of_cable_brake enable"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_tracking_error(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 9, 0xAA)

    def test_configure_monitoring_of_tracking_error_false(self):
        """Test configure_monitoring_of_cable_brake disable"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_tracking_error(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 9, 0xAA)

    def test_configure_monitoring_of_zero_pulse_true(self):
        """Test configure_monitoring_of_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_zero_pulse(True)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 10, 0xAB)

    def test_configure_monitoring_of_zero_pulse_false(self):
        """Test configure_monitoring_of_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_monitoring_of_zero_pulse(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 10, 0xAA)

    def test_configure_pulses_per_zero_pulse_0(self):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_pulses_per_zero_pulse(0)

        # Assert
        calls = [call(4828 + 64 + 11, 0), call(4828 + 64 + 12, 0)]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_pulses_per_zero_pulse_65535(self):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_pulses_per_zero_pulse(65535)

        # Assert
        calls = [call(4828 + 64 + 11, 0xFF), call(4828 + 64 + 12, 0xFF)]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_pulses_per_zero_pulse_0xCAFE(self):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_pulses_per_zero_pulse(0xCAFE)

        # Assert
        calls = [call(4828 + 64 + 11, 0xFE), call(4828 + 64 + 12, 0xCA)]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    @pytest.mark.parametrize("input_value", [-1, 65536])
    def test_configure_pulses_per_zero_pulse_raise_error(self, input_value):
        """Test configure_pulses_per_zero_pulse"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_pulses_per_zero_pulse(input_value)

    def test_configure_latching_signal_true(self):
        """Test configure_latching_signal"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_signal(True)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 13, 0xAB)

    def test_configure_latching_signal_false(self):
        """Test configure_latching_signal"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_signal(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 13, 0xAA)

    def test_configure_latching_event_0(self):
        """Test configure_latching_event"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_event(0)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 14, 0xA8)

    def test_configure_latching_event_3(self):
        """Test configure_latching_event"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_event(3)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 14, 0xAB)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_latching_event_raise_error(self, input_value):
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_latching_event(input_value)

    def test_configure_latching_response_true(self):
        """Test configure_latching_response"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_response(True)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 15, 0xAB)

    def test_configure_latching_response_false(self):
        """Test configure_latching_response"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_latching_response(False)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 15, 0xAA)

    def test_configure_upper_counter_limit_0(self):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_upper_counter_limit(0)

        # Assert
        calls = [
            call(4828 + 64 + 16, 0),
            call(4828 + 64 + 17, 0),
            call(4828 + 64 + 18, 0),
            call(4828 + 64 + 19, 0),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_upper_counter_limit_0xFFFFFFFF(self):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_upper_counter_limit(2**32 - 1)

        # Assert
        calls = [
            call(4828 + 64 + 16, 0xFF),
            call(4828 + 64 + 17, 0xFF),
            call(4828 + 64 + 18, 0xFF),
            call(4828 + 64 + 19, 0xFF),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_upper_counter_limit_0xCAFEBEEF(self):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_upper_counter_limit(0xCAFEBEEF)

        # Assert
        calls = [
            call(4828 + 64 + 16, 0xEF),
            call(4828 + 64 + 17, 0xBE),
            call(4828 + 64 + 18, 0xFE),
            call(4828 + 64 + 19, 0xCA),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    @pytest.mark.parametrize("input_value", [-1, 2**32])
    def test_configure_upper_counter_limit_raise_error(self, input_value):
        """Test configure_upper_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_upper_counter_limit(input_value)

    def test_configure_lower_counter_limit_0(self):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_lower_counter_limit(0)

        # Assert
        calls = [
            call(4828 + 64 + 20, 0),
            call(4828 + 64 + 21, 0),
            call(4828 + 64 + 22, 0),
            call(4828 + 64 + 23, 0),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_lower_counter_limit_0xFFFFFFFF(self):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_lower_counter_limit(2**32 - 1)

        # Assert
        calls = [
            call(4828 + 64 + 20, 0xFF),
            call(4828 + 64 + 21, 0xFF),
            call(4828 + 64 + 22, 0xFF),
            call(4828 + 64 + 23, 0xFF),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls[4:8], any_order=False)

    def test_configure_lower_counter_limit_0xCAFEBEEF(self):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_lower_counter_limit(0xCAFEBEEF)

        # Assert
        calls = [
            call(4828 + 64 + 20, 0xEF),
            call(4828 + 64 + 21, 0xBE),
            call(4828 + 64 + 22, 0xFE),
            call(4828 + 64 + 23, 0xCA),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    @pytest.mark.parametrize("input_value", [-1, 2**32])
    def test_configure_lower_counter_limit_raise_error(self, input_value):
        """Test configure_lower_counter_limit"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_lower_counter_limit(input_value)

    def test_configure_load_value_0(self):
        """Test configure_load_value"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_load_value(0)

        # Assert
        calls = [
            call(4828 + 64 + 24, 0),
            call(4828 + 64 + 25, 0),
            call(4828 + 64 + 26, 0),
            call(4828 + 64 + 27, 0),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_load_value_0xFFFFFFFF(self):
        """Test configure_load_value"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_load_value(2**32 - 1)

        # Assert
        calls = [
            call(4828 + 64 + 24, 0xFF),
            call(4828 + 64 + 25, 0xFF),
            call(4828 + 64 + 26, 0xFF),
            call(4828 + 64 + 27, 0xFF),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    def test_configure_load_value_0xCAFEBEEF(self):
        """Test configure_load_value"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(write_function_number=Mock())

        # Act
        cpxe1ci.configure_load_value(0xCAFEBEEF)

        # Assert
        calls = [
            call(4828 + 64 + 24, 0xEF),
            call(4828 + 64 + 25, 0xBE),
            call(4828 + 64 + 26, 0xFE),
            call(4828 + 64 + 27, 0xCA),
        ]
        cpxe1ci.base.write_function_number.assert_has_calls(calls, any_order=False)

    @pytest.mark.parametrize("input_value", [-1, 2**32 + 1])
    def test_configure_load_value_raise_error(self, input_value):
        """Test configure_load_value"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_load_value(input_value)

    def test_configure_debounce_time_for_digital_inputs_0(self):
        """Test configure_debounce_time_for_digital_inputs"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_debounce_time_for_digital_inputs(0)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 28, 0xA8)

    def test_configure_debounce_time_for_digital_inputs_3(self):
        """Test configure_debounce_time_for_digital_inputs"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_debounce_time_for_digital_inputs(3)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 28, 0xAB)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_for_digital_inputs_raise_error(self, input_value):
        """Test configure_debounce_time_for_digital_inputs"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_debounce_time_for_digital_inputs(input_value)

    def test_configure_integration_time_for_speed_measurement_0(self):
        """Test configure_integration_time_for_speed_measurement"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_integration_time_for_speed_measurement(0)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 29, 0xA8)

    def test_configure_integration_time_for_speed_measurement_3(self):
        """Test configure_integration_time_for_speed_measurement"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        cpxe1ci.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe1ci.configure_integration_time_for_speed_measurement(3)

        # Assert
        cpxe1ci.base.write_function_number.assert_called_with(4828 + 64 + 29, 0xAB)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_integration_time_for_speed_measurement_raise_error(
        self, input_value
    ):
        """Test configure_integration_time_for_speed_measurement"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe1ci.configure_integration_time_for_speed_measurement(input_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        # Act
        module_repr = repr(cpxe1ci)

        # Assert
        assert module_repr == "cpxe1ci (idx: 1, type: CpxE1Ci)"
