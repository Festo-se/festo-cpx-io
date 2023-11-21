"""Contains tests for cpx_e8do class"""
import unittest
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_e import CpxE, CpxE8Do


class TestCpxE8Do(unittest.TestCase):
    """Test cpx-e-8do"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe8do = CpxE8Do()

        assert cpxe8do.base is None
        assert cpxe8do.position is None

        cpxe8do = cpx_e.add_module(cpxe8do)

        mocked_base = Mock()
        cpxe8do.base = mocked_base

        assert cpxe8do.base == mocked_base
        assert cpxe8do.position == 1

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe8do.base = mocked_base

        assert cpxe8do.read_status() == [
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

    def test_read_channel_0_to_7(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        cpxe8do.base = mocked_base

        assert cpxe8do.read_channel(0) is False
        assert cpxe8do.read_channel(1) is True
        assert cpxe8do.read_channel(2) is True
        assert cpxe8do.read_channel(3) is True
        assert cpxe8do.read_channel(4) is False
        assert cpxe8do.read_channel(5) is True
        assert cpxe8do.read_channel(6) is False
        assert cpxe8do.read_channel(7) is True
        mocked_base.read_reg_data.assert_called_with(cpxe8do.input_register)

    def test_getitem_0_to_7(self):
        """Test get item"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        cpxe8do.base = mocked_base

        # Exercise
        assert cpxe8do[0] is False
        assert cpxe8do[1] is True
        assert cpxe8do[2] is True
        assert cpxe8do[3] is True
        assert cpxe8do[4] is False
        assert cpxe8do[5] is True
        assert cpxe8do[6] is False
        assert cpxe8do[7] is True
        mocked_base.read_reg_data.assert_called_with(cpxe8do.input_register)

    def test_write_channel_0_true(self):
        """test write channel true"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.write_channel(0, True)
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_write_channel_1_false(self):
        """Test write channel false"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.write_channel(1, False)
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )

    def test_setitem_0_true(self):
        """Test set item true"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do[0] = True
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_setitem_1_false(self):
        """Test set item false"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do[1] = False
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )

    def test_set_channel_0(self):
        """Test set channel"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.set_channel(0)
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_clear_channel_1(self):
        """Test clear channel"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.clear_channel(1)
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )

    def test_toggle_channel_2(self):
        """Test toggle channel"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.toggle_channel(2)
        mocked_base.write_reg_data.assert_called_with(
            0b10101010, cpxe8do.output_register
        )

    def test_configure_diagnostics(self):
        """Test diagnostics"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=[0xAA])
        mocked_base.write_function_number = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.configure_diagnostics()
        mocked_base.write_function_number.assert_called_with(4892, 0xAA)

        cpxe8do.configure_diagnostics(short_circuit=False)
        mocked_base.write_function_number.assert_called_with(4892, 0xA8)

        cpxe8do.configure_diagnostics(undervoltage=True)
        mocked_base.write_function_number.assert_called_with(4892, 0xAE)

        cpxe8do.configure_diagnostics(short_circuit=False, undervoltage=True)
        mocked_base.write_function_number.assert_called_with(4892, 0xAC)

    def test_configure_power_reset(self):
        """Test power reset"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=[0xAA])
        mocked_base.write_function_number = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.configure_power_reset(True)
        mocked_base.write_function_number.assert_called_with(4893, 0xAA)

        cpxe8do.configure_power_reset(False)
        mocked_base.write_function_number.assert_called_with(4893, 0xA8)

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxe8do = cpx_e.add_module(CpxE8Do())

        mocked_base = Mock()
        cpxe8do.base = mocked_base

        self.assertEqual(repr(cpxe8do), "cpxe8do at position 1")
