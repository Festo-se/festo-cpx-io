"""Contains tests for cpx_e4aoui class"""
from unittest.mock import Mock

import pytest


from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI


class TestCpxE4AoUI:
    """Test cpx-e-4aoui"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe4aoui = CpxE4AoUI()

        assert cpxe4aoui.base is None
        assert cpxe4aoui.position is None

        cpxe4aoui = cpx_e.add_module(cpxe4aoui)

        mocked_base = Mock()
        cpxe4aoui.base = mocked_base

        assert cpxe4aoui.base == mocked_base
        assert cpxe4aoui.position == 1

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe4aoui.base = mocked_base

        assert cpxe4aoui.read_status() == [
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
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0, 1000, 2000, 3000])
        cpxe4aoui.base = mocked_base

        assert cpxe4aoui.read_channel(0) == 0
        assert cpxe4aoui.read_channel(1) == 1000
        assert cpxe4aoui.read_channel(2) == 2000
        assert cpxe4aoui.read_channel(3) == 3000
        mocked_base.read_reg_data.assert_called_with(cpxe4aoui.input_register, length=4)

    def test_getitem_0_to_3(self):
        """Test get item"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0, 1000, 2000, 3000])
        cpxe4aoui.base = mocked_base

        # Exercise
        assert cpxe4aoui[0] == 0
        assert cpxe4aoui[1] == 1000
        assert cpxe4aoui[2] == 2000
        assert cpxe4aoui[3] == 3000
        mocked_base.read_reg_data.assert_called_with(cpxe4aoui.input_register, length=4)

    def test_write_channel(self):
        """test write channel"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.write_reg_data = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.write_channel(0, 1000)
        mocked_base.write_reg_data.assert_called_with(
            1000, cpxe4aoui.output_register + 0
        )

        cpxe4aoui.write_channel(1, 2000)
        mocked_base.write_reg_data.assert_called_with(
            2000, cpxe4aoui.output_register + 1
        )

    def test_write_channels(self):
        """test write channels"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.write_reg_data = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.write_channels([0, 1, 2, 3])
        mocked_base.write_reg_data.assert_called_with(
            [0, 1, 2, 3], cpxe4aoui.output_register, length=4
        )

    def test_set_channel_0(self):
        """Test set channel"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.write_reg_data = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui[0] = 1000
        mocked_base.write_reg_data.assert_called_with(1000, cpxe4aoui.output_register)

    def test_configure_channel_range(self):
        """Test channel range"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_channel_range(0, "0-10V")  # 0001
        mocked_base.write_function_number.assert_called_with(4892 + 11, 0xA1)

        cpxe4aoui.configure_channel_range(1, "4-20mA")  # 0110
        mocked_base.write_function_number.assert_called_with(4892 + 11, 0x6A)

        cpxe4aoui.configure_channel_range(2, "1-5V")  # 0100
        mocked_base.write_function_number.assert_called_with(4892 + 12, 0xA4)

        cpxe4aoui.configure_channel_range(3, "-20-+20mA")  # 0111
        mocked_base.write_function_number.assert_called_with(4892 + 12, 0x7A)

        with pytest.raises(ValueError):
            cpxe4aoui.configure_channel_range(0, "not_implemented")

        with pytest.raises(ValueError):
            cpxe4aoui.configure_channel_range(4, "0-10V")

    def test_configure_diagnostics(self):
        """Test diagnostics"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_diagnostics()
        mocked_base.write_function_number.assert_called_with(4892, 0xAA)

        cpxe4aoui.configure_diagnostics(short_circuit=False)
        mocked_base.write_function_number.assert_called_with(4892, 0xA8)

        cpxe4aoui.configure_diagnostics(param_error=False)
        mocked_base.write_function_number.assert_called_with(4892, 0x2A)

        cpxe4aoui.configure_diagnostics(undervoltage=True)
        mocked_base.write_function_number.assert_called_with(4892, 0xAE)

        cpxe4aoui.configure_diagnostics(
            short_circuit=False, param_error=False, undervoltage=True
        )
        mocked_base.write_function_number.assert_called_with(4892, 0x2C)

    def test_configure_power_reset(self):
        """Test power reset"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_power_reset(True)
        mocked_base.write_function_number.assert_called_with(4893, 0xAA)

        cpxe4aoui.configure_power_reset(False)
        mocked_base.write_function_number.assert_called_with(4893, 0xA8)

    def test_configure_behaviour_overload(self):
        """Test behaviour overload"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_behaviour_overload(True)
        mocked_base.write_function_number.assert_called_with(4893, 0xAA)

        cpxe4aoui.configure_behaviour_overload(False)
        mocked_base.write_function_number.assert_called_with(4893, 0xA2)

    def test_configure_data_format(self):
        """Test data format"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_data_format(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xAB)

        cpxe4aoui.configure_data_format(False)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

    def test_configure_actuator_supply(self):
        """Test actuator supply"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4aoui.base = mocked_base

        cpxe4aoui.configure_actuator_supply(True)
        mocked_base.write_function_number.assert_called_with(4898, 0xAA)

        cpxe4aoui.configure_actuator_supply(False)
        mocked_base.write_function_number.assert_called_with(4898, 0x8A)

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxe4aoui = cpx_e.add_module(CpxE4AoUI())

        mocked_base = Mock()
        cpxe4aoui.base = mocked_base

        assert repr(cpxe4aoui) == "cpxe4aoui (idx: 1, type: CpxE4AoUI)"
