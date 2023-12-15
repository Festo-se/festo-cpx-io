"""Contains tests for cpx_e16di class"""
from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di


class TestCpxE16Di:
    """Test cpx-e-16di"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe16di = CpxE16Di()

        assert cpxe16di.base is None
        assert cpxe16di.position is None

        cpxe16di = cpx_e.add_module(cpxe16di)

        mocked_base = Mock()
        cpxe16di.base = mocked_base

        assert cpxe16di.base == mocked_base
        assert cpxe16di.position == 1

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe16di.base = mocked_base

        assert cpxe16di.read_status() == [False, True] * 8

    def test_read_channel_0_to_15(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b1100110010101110])
        cpxe16di.base = mocked_base

        assert cpxe16di.read_channel(0) is False
        assert cpxe16di.read_channel(1) is True
        assert cpxe16di.read_channel(2) is True
        assert cpxe16di.read_channel(3) is True
        assert cpxe16di.read_channel(4) is False
        assert cpxe16di.read_channel(5) is True
        assert cpxe16di.read_channel(6) is False
        assert cpxe16di.read_channel(7) is True
        assert cpxe16di.read_channel(8) is False
        assert cpxe16di.read_channel(9) is False
        assert cpxe16di.read_channel(10) is True
        assert cpxe16di.read_channel(11) is True
        assert cpxe16di.read_channel(12) is False
        assert cpxe16di.read_channel(13) is False
        assert cpxe16di.read_channel(14) is True
        assert cpxe16di.read_channel(15) is True
        mocked_base.read_reg_data.assert_called_with(cpxe16di.input_register)

    def test_getitem_0_to_15(self):
        """Test get item"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b1100110010101110])
        cpxe16di.base = mocked_base

        # Exercise
        assert cpxe16di[0] is False
        assert cpxe16di[1] is True
        assert cpxe16di[2] is True
        assert cpxe16di[3] is True
        assert cpxe16di[4] is False
        assert cpxe16di[5] is True
        assert cpxe16di[6] is False
        assert cpxe16di[7] is True
        assert cpxe16di[8] is False
        assert cpxe16di[9] is False
        assert cpxe16di[10] is True
        assert cpxe16di[11] is True
        assert cpxe16di[12] is False
        assert cpxe16di[13] is False
        assert cpxe16di[14] is True
        assert cpxe16di[15] is True
        mocked_base.read_reg_data.assert_called_with(cpxe16di.input_register)

    def test_configure_diagnostics(self):
        """Test diagnostics"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe16di.base = mocked_base

        cpxe16di.configure_diagnostics(False)
        mocked_base.write_function_number.assert_called_with(4892, 0xAA)

        cpxe16di.configure_diagnostics(True)
        mocked_base.write_function_number.assert_called_with(4892, 0xAB)

    def test_configure_power_reset(self):
        """Test power reset"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe16di.base = mocked_base

        cpxe16di.configure_power_reset(False)
        mocked_base.write_function_number.assert_called_with(4893, 0xAA)

        cpxe16di.configure_power_reset(True)
        mocked_base.write_function_number.assert_called_with(4893, 0xAB)

    def test_configure_debounce_time(self):
        """Test debounce time"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe16di.base = mocked_base

        cpxe16di.configure_debounce_time(0)
        mocked_base.write_function_number.assert_called_with(4893, 0x8A)

        cpxe16di.configure_debounce_time(3)
        mocked_base.write_function_number.assert_called_with(4893, 0xBA)

        with pytest.raises(ValueError):
            cpxe16di.configure_debounce_time(-1)

        with pytest.raises(ValueError):
            cpxe16di.configure_debounce_time(4)

    def test_configure_signal_extension_time(self):
        """Test debounce time"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe16di.base = mocked_base

        cpxe16di.configure_signal_extension_time(0)
        mocked_base.write_function_number.assert_called_with(4893, 0x2A)

        cpxe16di.configure_signal_extension_time(3)
        mocked_base.write_function_number.assert_called_with(4893, 0xEA)

        with pytest.raises(ValueError):
            cpxe16di.configure_signal_extension_time(-1)

        with pytest.raises(ValueError):
            cpxe16di.configure_signal_extension_time(4)

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxe16di = cpx_e.add_module(CpxE16Di())

        mocked_base = Mock()
        cpxe16di.base = mocked_base

        assert repr(cpxe16di) == "cpxe16di (idx: 1, type: CpxE16Di)"
