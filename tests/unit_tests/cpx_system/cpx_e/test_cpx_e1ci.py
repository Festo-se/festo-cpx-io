"""Contains tests for cpx_e1ci class"""
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci


class TestCpxE1Ci:
    """Test cpx-e-16di"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe1ci = CpxE1Ci()

        assert cpxe1ci.base is None
        assert cpxe1ci.position is None

        cpxe1ci = cpx_e.add_module(cpxe1ci)

        mocked_base = Mock()
        cpxe1ci.base = mocked_base

        assert cpxe1ci.base == mocked_base
        assert cpxe1ci.position == 1

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe1ci.base = mocked_base

        assert cpxe1ci.read_status() == [False, True] * 8

    def test_read_value(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xCAFE, 0xBEEF])
        cpxe1ci.base = mocked_base

        assert cpxe1ci.read_value() == 0xBEEFCAFE
        mocked_base.read_reg_data.assert_called_with(cpxe1ci.input_register, length=2)

    def test_read_latching_value(self):
        """Test read_latching_value"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xCAFE, 0xBEEF])
        cpxe1ci.base = mocked_base

        assert cpxe1ci.read_latching_value() == 0xBEEFCAFE
        mocked_base.read_reg_data.assert_called_with(
            cpxe1ci.input_register + 2, length=2
        )

    def test_read_status_word(self):
        """Test read_status_word"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe1ci.base = mocked_base

        assert cpxe1ci.read_status_word() == {
            "DI0": False,
            "DI1": True,
            "DI2": False,
            "DI3": True,
            "Latching missed": True,
            "Latching set": False,
            "Latching blocked": True,
            "Lower CL exceeded": False,
            "Upper CL exceeded": True,
            "Counting direction": False,
            "Counter blocked": True,
            "Counter set": False,
            "Enable DI2": True,
            "Enable zero": False,
            "Speed measurement": True,
        }
        mocked_base.read_reg_data.assert_called_with(cpxe1ci.input_register + 4)

    def test_read_process_data(self):
        """Test read_process_data"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAA])
        cpxe1ci.base = mocked_base

        assert cpxe1ci.read_process_data() == {
            "enable_setting_DI2": False,
            "enable_setting_zero": True,
            "set_counter": False,
            "block_counter": True,
            "overrun_cl_confirm": False,
            "speed_measurement": True,
            "confirm_latching": False,
            "block_latching": True,
        }
        mocked_base.read_reg_data.assert_called_with(cpxe1ci.input_register + 6)

    def test_write_process_data(self):
        """Test write_process_data"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAA])
        mocked_base.write_reg_data = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.write_process_data(enable_setting_DI2=True)
        mocked_base.write_reg_data.assert_called_with(0xAB, cpxe1ci.output_register)

        cpxe1ci.write_process_data(block_latching=False)
        mocked_base.write_reg_data.assert_called_with(0x2A, cpxe1ci.output_register)

    def test_configure_signal_type(self):
        """Test configure_signal_type"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_signal_type(0)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 6, 0xA8)

        cpxe1ci.configure_signal_type(3)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 6, 0xAB)

        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_type(-1)

        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_type(4)

    def test_configure_signal_evaluation(self):
        """Test configure_signal_evaluation"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_signal_evaluation(0)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 7, 0xA8)

        cpxe1ci.configure_signal_evaluation(3)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 7, 0xAB)

        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_evaluation(-1)

        with pytest.raises(ValueError):
            cpxe1ci.configure_signal_evaluation(4)

    def test_configure_monitoring_of_cable_brake(self):
        """Test configure_monitoring_of_cable_brake"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_monitoring_of_cable_brake(True)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 8, 0xAB)

        cpxe1ci.configure_monitoring_of_cable_brake(False)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 8, 0xAA)

    def test_configure_monitoring_of_tracking_error(self):
        """Test configure_monitoring_of_cable_brake"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_monitoring_of_tracking_error(True)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 9, 0xAB)

        cpxe1ci.configure_monitoring_of_tracking_error(False)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 9, 0xAA)

    def test_configure_monitoring_of_zero_pulse(self):
        """Test configure_monitoring_of_zero_pulse"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_monitoring_of_zero_pulse(True)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 10, 0xAB)

        cpxe1ci.configure_monitoring_of_zero_pulse(False)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 10, 0xAA)

    def test_configure_pulses_per_zero_pulse(self):
        """Test configure_pulses_per_zero_pulse"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        calls = [
            call(4828 + 64 + 11, 0),
            call(4828 + 64 + 12, 0),
            call(4828 + 64 + 11, 0xFF),
            call(4828 + 64 + 12, 0xFF),
            call(4828 + 64 + 11, 0xFE),
            call(4828 + 64 + 12, 0xCA),
        ]

        cpxe1ci.configure_pulses_per_zero_pulse(0)
        mocked_base.write_function_number.assert_has_calls(calls[:2], any_order=False)

        cpxe1ci.configure_pulses_per_zero_pulse(65535)
        mocked_base.write_function_number.assert_has_calls(calls[2:4], any_order=False)

        cpxe1ci.configure_pulses_per_zero_pulse(0xCAFE)
        mocked_base.write_function_number.assert_has_calls(calls[4:6], any_order=False)

        with pytest.raises(ValueError):
            cpxe1ci.configure_pulses_per_zero_pulse(-1)
        with pytest.raises(ValueError):
            cpxe1ci.configure_pulses_per_zero_pulse(65536)

    def test_configure_latching_signal(self):
        """Test configure_latching_signal"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_latching_signal(True)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 13, 0xAB)

        cpxe1ci.configure_latching_signal(False)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 13, 0xAA)

    def test_configure_latching_event(self):
        """Test configure_latching_event"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_latching_event(0)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 14, 0xA8)

        cpxe1ci.configure_latching_event(3)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 14, 0xAB)

        with pytest.raises(ValueError):
            cpxe1ci.configure_latching_event(-1)

        with pytest.raises(ValueError):
            cpxe1ci.configure_latching_event(4)

    def test_configure_latching_response(self):
        """Test configure_latching_response"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_latching_response(True)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 15, 0xAB)

        cpxe1ci.configure_latching_response(False)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 15, 0xAA)

    def test_configure_upper_counter_limit(self):
        """Test configure_upper_counter_limit"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        calls = [
            call(4828 + 64 + 16, 0),
            call(4828 + 64 + 17, 0),
            call(4828 + 64 + 18, 0),
            call(4828 + 64 + 19, 0),
            call(4828 + 64 + 16, 0xFF),
            call(4828 + 64 + 17, 0xFF),
            call(4828 + 64 + 18, 0xFF),
            call(4828 + 64 + 19, 0xFF),
            call(4828 + 64 + 16, 0xEF),
            call(4828 + 64 + 17, 0xBE),
            call(4828 + 64 + 18, 0xFE),
            call(4828 + 64 + 19, 0xCA),
        ]

        cpxe1ci.configure_upper_counter_limit(0)
        mocked_base.write_function_number.assert_has_calls(calls[:4], any_order=False)

        cpxe1ci.configure_upper_counter_limit(2**32 - 1)
        mocked_base.write_function_number.assert_has_calls(calls[4:8], any_order=False)

        cpxe1ci.configure_upper_counter_limit(0xCAFEBEEF)
        mocked_base.write_function_number.assert_has_calls(calls[8:12], any_order=False)

        with pytest.raises(ValueError):
            cpxe1ci.configure_upper_counter_limit(-1)
        with pytest.raises(ValueError):
            cpxe1ci.configure_upper_counter_limit(2**32)

    def test_configure_lower_counter_limit(self):
        """Test configure_lower_counter_limit"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        calls = [
            call(4828 + 64 + 20, 0),
            call(4828 + 64 + 21, 0),
            call(4828 + 64 + 22, 0),
            call(4828 + 64 + 23, 0),
            call(4828 + 64 + 20, 0xFF),
            call(4828 + 64 + 21, 0xFF),
            call(4828 + 64 + 22, 0xFF),
            call(4828 + 64 + 23, 0xFF),
            call(4828 + 64 + 20, 0xEF),
            call(4828 + 64 + 21, 0xBE),
            call(4828 + 64 + 22, 0xFE),
            call(4828 + 64 + 23, 0xCA),
        ]

        cpxe1ci.configure_lower_counter_limit(0)
        mocked_base.write_function_number.assert_has_calls(calls[:4], any_order=False)

        cpxe1ci.configure_lower_counter_limit(2**32 - 1)
        mocked_base.write_function_number.assert_has_calls(calls[4:8], any_order=False)

        cpxe1ci.configure_lower_counter_limit(0xCAFEBEEF)
        mocked_base.write_function_number.assert_has_calls(calls[8:12], any_order=False)

        with pytest.raises(ValueError):
            cpxe1ci.configure_lower_counter_limit(-1)
        with pytest.raises(ValueError):
            cpxe1ci.configure_lower_counter_limit(2**32)

    def test_configure_load_value(self):
        """Test configure_load_value"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        calls = [
            call(4828 + 64 + 24, 0),
            call(4828 + 64 + 25, 0),
            call(4828 + 64 + 26, 0),
            call(4828 + 64 + 27, 0),
            call(4828 + 64 + 24, 0xFF),
            call(4828 + 64 + 25, 0xFF),
            call(4828 + 64 + 26, 0xFF),
            call(4828 + 64 + 27, 0xFF),
            call(4828 + 64 + 24, 0xEF),
            call(4828 + 64 + 25, 0xBE),
            call(4828 + 64 + 26, 0xFE),
            call(4828 + 64 + 27, 0xCA),
        ]

        cpxe1ci.configure_load_value(0)
        mocked_base.write_function_number.assert_has_calls(calls[:4], any_order=False)

        cpxe1ci.configure_load_value(2**32 - 1)
        mocked_base.write_function_number.assert_has_calls(calls[4:8], any_order=False)

        cpxe1ci.configure_load_value(0xCAFEBEEF)
        mocked_base.write_function_number.assert_has_calls(calls[8:12], any_order=False)

        with pytest.raises(ValueError):
            cpxe1ci.configure_load_value(-1)
        with pytest.raises(ValueError):
            cpxe1ci.configure_load_value(2**32 + 1)

    def test_configure_debounce_time_for_digital_inputs(self):
        """Test configure_debounce_time_for_digital_inputs"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_debounce_time_for_digital_inputs(0)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 28, 0xA8)

        cpxe1ci.configure_debounce_time_for_digital_inputs(3)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 28, 0xAB)

        with pytest.raises(ValueError):
            cpxe1ci.configure_debounce_time_for_digital_inputs(-1)

        with pytest.raises(ValueError):
            cpxe1ci.configure_debounce_time_for_digital_inputs(4)

    def test_configure_integration_time_for_speed_measurement(self):
        """Test configure_integration_time_for_speed_measurement"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe1ci.base = mocked_base

        cpxe1ci.configure_integration_time_for_speed_measurement(0)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 29, 0xA8)

        cpxe1ci.configure_integration_time_for_speed_measurement(3)
        mocked_base.write_function_number.assert_called_with(4828 + 64 + 29, 0xAB)

        with pytest.raises(ValueError):
            cpxe1ci.configure_integration_time_for_speed_measurement(-1)

        with pytest.raises(ValueError):
            cpxe1ci.configure_integration_time_for_speed_measurement(4)

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxe1ci = cpx_e.add_module(CpxE1Ci())

        mocked_base = Mock()
        cpxe1ci.base = mocked_base

        assert repr(cpxe1ci) == "cpxe1ci (idx: 1, type: CpxE1Ci)"
