"""Contains tests for cpx_e4aiui class"""
from unittest.mock import Mock

import pytest


from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI


class TestCpxE4AiUI:
    """Test cpx-e-4aiui"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe4aiui = CpxE4AiUI()

        assert cpxe4aiui.base is None
        assert cpxe4aiui.position is None

        cpxe4aiui = cpx_e.add_module(cpxe4aiui)

        mocked_base = Mock()
        cpxe4aiui.base = mocked_base

        assert cpxe4aiui.base == mocked_base
        assert cpxe4aiui.position == 1

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe4aiui.base = mocked_base

        assert cpxe4aiui.read_status() == [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        ]

    def test_read_channel_0_to_3(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0, 1000, 2000, 3000])
        cpxe4aiui.base = mocked_base

        assert cpxe4aiui.read_channel(0) == 0
        assert cpxe4aiui.read_channel(1) == 1000
        assert cpxe4aiui.read_channel(2) == 2000
        assert cpxe4aiui.read_channel(3) == 3000
        mocked_base.read_reg_data.assert_called_with(cpxe4aiui.input_register, length=4)

    def test_getitem_0_to_3(self):
        """Test get item"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0, 1000, 2000, 3000])
        cpxe4aiui.base = mocked_base

        # Exercise
        assert cpxe4aiui[0] == 0
        assert cpxe4aiui[1] == 1000
        assert cpxe4aiui[2] == 2000
        assert cpxe4aiui[3] == 3000
        mocked_base.read_reg_data.assert_called_with(cpxe4aiui.input_register, length=4)

    def test_configure_channel_range(self):
        """Test channel range"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_channel_range(0, "0-10V")  # 0001
        mocked_base.write_function_number.assert_called_with(4892 + 13, 0xA1)

        cpxe4aiui.configure_channel_range(1, "4-20mA")  # 0110
        mocked_base.write_function_number.assert_called_with(4892 + 13, 0x6A)

        cpxe4aiui.configure_channel_range(2, "None")  # 0000
        mocked_base.write_function_number.assert_called_with(4892 + 14, 0xA0)

        cpxe4aiui.configure_channel_range(3, "0-10VoU")  # 1000
        mocked_base.write_function_number.assert_called_with(4892 + 14, 0x8A)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_range(0, "not_implemented")

        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_range(4, "None")

    def test_configure_channel_smoothing(self):
        """Test channel smoothing"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_channel_smoothing(0, 0)
        mocked_base.write_function_number.assert_called_with(4892 + 15, 0xA0)

        cpxe4aiui.configure_channel_smoothing(1, 2)
        mocked_base.write_function_number.assert_called_with(4892 + 15, 0x2A)

        cpxe4aiui.configure_channel_smoothing(2, 10)
        mocked_base.write_function_number.assert_called_with(4892 + 16, 0xAA)

        cpxe4aiui.configure_channel_smoothing(3, 15)
        mocked_base.write_function_number.assert_called_with(4892 + 16, 0xFA)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_smoothing(0, 16)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_channel_smoothing(4, 0)

    def test_configure_diagnostics(self):
        """Test diagnostics"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_diagnostics()
        mocked_base.write_function_number.assert_called_with(4892, 0xAA)

        cpxe4aiui.configure_diagnostics(short_circuit=True)
        mocked_base.write_function_number.assert_called_with(4892, 0xAB)

        cpxe4aiui.configure_diagnostics(param_error=False)
        mocked_base.write_function_number.assert_called_with(4892, 0x2A)

        cpxe4aiui.configure_diagnostics(short_circuit=True, param_error=False)
        mocked_base.write_function_number.assert_called_with(4892, 0x2B)

    def test_configure_power_reset(self):
        """Test power reset"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_power_reset(True)
        mocked_base.write_function_number.assert_called_with(4893, 0xAB)

        cpxe4aiui.configure_power_reset(False)
        mocked_base.write_function_number.assert_called_with(4893, 0xAA)

    def test_configure_data_format(self):
        """Test data format"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_data_format(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xAB)

        cpxe4aiui.configure_data_format(False)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

    def test_configure_sensor_supply(self):
        """Test sensor supply"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_sensor_supply(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

        cpxe4aiui.configure_sensor_supply(False)
        mocked_base.write_function_number.assert_called_with(4898, 0x8A)

    def test_configure_diagnostics_overload(self):
        """Test diagnostics overload"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_diagnostics_overload(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xEA)

        cpxe4aiui.configure_diagnostics_overload(False)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

    def test_configure_behaviour_overload(self):
        """Test behaviour overload"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_behaviour_overload(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

        cpxe4aiui.configure_behaviour_overload(False)
        mocked_base.write_function_number.assert_called_with(4898, 0x2A)

    def test_configure_hysteresis_limit_monitoring(self):
        """Test hysteresis limit monitoring"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aiui.base = mocked_base

        cpxe4aiui.configure_hysteresis_limit_monitoring(0)
        mocked_base.write_function_number.assert_called_with(4892 + 7, 0x00)

        cpxe4aiui.configure_hysteresis_limit_monitoring(0, 1)
        mocked_base.write_function_number.assert_called_with(4892 + 7, 0x00)

        cpxe4aiui.configure_hysteresis_limit_monitoring(lower=0xFE)
        mocked_base.write_function_number.assert_called_with(4892 + 7, 0xFE)

        cpxe4aiui.configure_hysteresis_limit_monitoring(upper=0xFE)
        mocked_base.write_function_number.assert_called_with(4892 + 8, 0xFE)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_hysteresis_limit_monitoring(lower=-1)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_hysteresis_limit_monitoring(upper=32768)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_hysteresis_limit_monitoring(lower=0, upper=-1)

        with pytest.raises(ValueError):
            cpxe4aiui.configure_hysteresis_limit_monitoring()

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxe4aiui = cpx_e.add_module(CpxE4AiUI())

        mocked_base = Mock()
        cpxe4aiui.base = mocked_base

        assert repr(cpxe4aiui) == "cpxe4aiui (idx: 1, type: CpxE4AiUI)"
