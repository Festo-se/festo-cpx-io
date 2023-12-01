"""Contains tests for cpx_e4iol class"""
from unittest.mock import Mock, call

import pytest

from cpx_io.cpx_system.cpx_e import CpxE, CpxE4Iol


class TestCpxE4Iol:
    """Test cpx-e-4iol"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe4iol = CpxE4Iol()

        assert cpxe4iol.base is None
        assert cpxe4iol.position is None

        cpxe4iol = cpx_e.add_module(cpxe4iol)

        mocked_base = Mock()
        cpxe4iol.base = mocked_base

        assert cpxe4iol.base == mocked_base
        assert cpxe4iol.position == 1
        assert cpxe4iol.module_input_size == 1
        assert cpxe4iol.module_output_size == 1

    def test_initialize_8ae(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxe4iol = CpxE4Iol(8)

        assert cpxe4iol.base is None
        assert cpxe4iol.position is None

        cpxe4iol = cpx_e.add_module(cpxe4iol)

        mocked_base = Mock()
        cpxe4iol.base = mocked_base

        assert cpxe4iol.base == mocked_base
        assert cpxe4iol.position == 1
        assert cpxe4iol.module_input_size == 4
        assert cpxe4iol.module_output_size == 4

    def test_initialize_wrong(self):
        """Test initialize function"""

        with pytest.raises(ValueError):
            CpxE4Iol(3)

    def test_read_status(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAAAA])
        cpxe4iol.base = mocked_base

        assert cpxe4iol.read_status() == [
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

    def test_read_2byte_channel_0_to_3(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        cpxe4iol.base = mocked_base

        assert cpxe4iol.read_channel(0) == [0xAB00]
        assert cpxe4iol.read_channel(1) == [0xCD00]
        assert cpxe4iol.read_channel(2) == [0xEF00]
        assert cpxe4iol.read_channel(3) == [0x1200]
        mocked_base.read_reg_data.assert_called_with(cpxe4iol.input_register, length=4)

    def test_read_8byte_channel_0_to_3(self):
        """Test read channels"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol(8))

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(
            return_value=[
                0xA110,
                0xA111,
                0xA113,
                0xA114,
                0xB110,
                0xB111,
                0xB113,
                0xB114,
                0xC110,
                0xC111,
                0xC113,
                0xC114,
                0xD110,
                0xD111,
                0xD113,
                0xD114,
            ]
        )
        cpxe4iol.base = mocked_base

        assert cpxe4iol.read_channel(0) == [0x10A1, 0x11A1, 0x13A1, 0x14A1]
        assert cpxe4iol.read_channel(1) == [0x10B1, 0x11B1, 0x13B1, 0x14B1]
        assert cpxe4iol.read_channel(2) == [0x10C1, 0x11C1, 0x13C1, 0x14C1]
        assert cpxe4iol.read_channel(3) == [0x10D1, 0x11D1, 0x13D1, 0x14D1]
        mocked_base.read_reg_data.assert_called_with(cpxe4iol.input_register, length=16)

    def test_getitem_0_to_3(self):
        """Test get item"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        cpxe4iol.base = mocked_base

        # Exercise
        assert cpxe4iol[0] == [0xAB00]
        assert cpxe4iol[1] == [0xCD00]
        assert cpxe4iol[2] == [0xEF00]
        assert cpxe4iol[3] == [0x1200]
        mocked_base.read_reg_data.assert_called_with(cpxe4iol.input_register, length=4)

    def test_read_outputs_0_to_3(self):
        """Test read outputs"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        cpxe4iol.base = mocked_base

        # Exercise
        assert cpxe4iol.read_output_channel(0) == [0xAB00]
        assert cpxe4iol.read_output_channel(1) == [0xCD00]
        assert cpxe4iol.read_output_channel(2) == [0xEF00]
        assert cpxe4iol.read_output_channel(3) == [0x1200]
        mocked_base.read_reg_data.assert_called_with(
            cpxe4iol.input_register + 4, length=4
        )

    def test_write_channel(self):
        """test write channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.write_reg_data = Mock()
        cpxe4iol.base = mocked_base

        cpxe4iol.write_channel(0, [0xAB])
        mocked_base.write_reg_data.assert_called_with(
            [0xAB00], cpxe4iol.output_register + 0
        )

        cpxe4iol.write_channel(1, [0xCD])
        mocked_base.write_reg_data.assert_called_with(
            [0xCD00], cpxe4iol.output_register + 1
        )

    def test_set_channel_0(self):
        """Test set channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.write_reg_data = Mock()
        cpxe4iol.base = mocked_base

        cpxe4iol[0] = [0xFE]
        mocked_base.write_reg_data.assert_called_with(
            [0xFE00], cpxe4iol.output_register
        )

    def test_configure_monitoring_uload(self):
        """Test configure_monitoring_uload"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4iol.base = mocked_base

        cpxe4iol.configure_monitoring_uload(True)
        mocked_base.read_function_number.assert_called_with(4892)
        mocked_base.write_function_number.assert_called_with(4892, 0xAE)

        cpxe4iol.configure_monitoring_uload(False)
        mocked_base.read_function_number.assert_called_with(4892)
        mocked_base.write_function_number.assert_called_with(4892, 0xAA)

    def test_configure_behaviour_after_scl(self):
        """Test configure_behaviour_after_scl"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4iol.base = mocked_base

        cpxe4iol.configure_behaviour_after_scl(True)
        mocked_base.read_function_number.assert_called_with(4892 + 1)
        mocked_base.write_function_number.assert_called_with(4892 + 1, 0xAB)

        cpxe4iol.configure_behaviour_after_scl(False)
        mocked_base.read_function_number.assert_called_with(4892 + 1)
        mocked_base.write_function_number.assert_called_with(4892 + 1, 0xAA)

    def test_configure_ps_supply(self):
        """Test configure_ps_supply"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        mocked_base.write_function_number = Mock()
        cpxe4iol.base = mocked_base

        cpxe4iol.configure_ps_supply(True)
        mocked_base.read_function_number.assert_called_with(4892 + 6)
        mocked_base.write_function_number.assert_called_with(4892 + 6, 0xAB)

        cpxe4iol.configure_ps_supply(False)
        mocked_base.read_function_number.assert_called_with(4892 + 6)
        mocked_base.write_function_number.assert_called_with(4892 + 6, 0xAA)

    def test_configure_cycle_time(self):
        """Test configure_cycle_time per channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        cpxe4iol.base = mocked_base

        expected_calls = [
            call(4892 + 8, 10),
            call(4892 + 9, 20),
            call(4892 + 12, 10),
            call(4892 + 13, 20),
            call(4892 + 16, 10),
            call(4892 + 17, 20),
            call(4892 + 20, 10),
            call(4892 + 21, 20),
        ]

        cpxe4iol.configure_cycle_time((10, 20))
        mocked_base.write_function_number.assert_has_calls(
            expected_calls, any_order=False
        )

        cpxe4iol.configure_cycle_time((10, 20), 0)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls[:2], any_order=False
        )

        cpxe4iol.configure_cycle_time((10, 20), [1, 2])
        mocked_base.write_function_number.assert_has_calls(
            expected_calls[2:6], any_order=False
        )

        with pytest.raises(ValueError):
            cpxe4iol.configure_operating_mode(True, -1)
            cpxe4iol.configure_operating_mode(True, 4)

    def test_configure_pl_supply(self):
        """Test configure_cycle_time per channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        cpxe4iol.base = mocked_base

        expected_calls_true = [
            call(4892 + 10, 0xAB),
            call(4892 + 14, 0xAB),
            call(4892 + 18, 0xAB),
            call(4892 + 22, 0xAB),
        ]

        expected_calls_false = [
            call(4892 + 10, 0xAA),
            call(4892 + 14, 0xAA),
            call(4892 + 18, 0xAA),
            call(4892 + 22, 0xAA),
        ]

        cpxe4iol.configure_pl_supply(True)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_true, any_order=False
        )

        cpxe4iol.configure_pl_supply(False)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_false, any_order=False
        )

        cpxe4iol.configure_pl_supply(True, 0)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_true[:1], any_order=False
        )

        cpxe4iol.configure_pl_supply(True, 0)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_false[:1], any_order=False
        )

        cpxe4iol.configure_pl_supply(True, [1, 2])
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_true[1:3], any_order=False
        )

        cpxe4iol.configure_pl_supply(True, [1, 2])
        mocked_base.write_function_number.assert_has_calls(
            expected_calls_false[1:3], any_order=False
        )

        with pytest.raises(ValueError):
            cpxe4iol.configure_operating_mode(True, -1)
            cpxe4iol.configure_operating_mode(True, 4)

    def test_configure_operating_mode(self):
        """Test configure_cycle_time per channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.write_function_number = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAA)
        cpxe4iol.base = mocked_base

        expected_calls = [
            call(4892 + 11, 0xAB),
            call(4892 + 15, 0xAB),
            call(4892 + 19, 0xAB),
            call(4892 + 23, 0xAB),
        ]

        cpxe4iol.configure_operating_mode(3)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls, any_order=False
        )

        cpxe4iol.configure_operating_mode(3, 0)
        mocked_base.write_function_number.assert_has_calls(
            expected_calls[:1], any_order=False
        )

        cpxe4iol.configure_operating_mode(3, [1, 2])
        mocked_base.write_function_number.assert_has_calls(
            expected_calls[1:3], any_order=False
        )

        with pytest.raises(ValueError):
            cpxe4iol.configure_operating_mode(4, 0)
            cpxe4iol.configure_operating_mode(-1, 0)
            cpxe4iol.configure_operating_mode(0, [-1])
            cpxe4iol.configure_operating_mode(0, [4])
            cpxe4iol.configure_operating_mode(0, -1)
            cpxe4iol.configure_operating_mode(0, 4)

    def test_read_line_state(self):
        """Test read_line_state per channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAD)
        cpxe4iol.base = mocked_base

        expected_calls = [
            call(4892 + 24),
            call(4892 + 27),
            call(4892 + 30),
            call(4892 + 33),
        ]

        state = cpxe4iol.read_line_state()
        mocked_base.read_function_number.assert_has_calls(
            expected_calls, any_order=False
        )
        assert state == ["OPERATE"] * 4

        state = cpxe4iol.read_line_state(0)
        mocked_base.read_function_number.assert_has_calls(
            expected_calls, any_order=False
        )

        assert state == "OPERATE"

        state = cpxe4iol.read_line_state([1, 2])
        mocked_base.read_function_number.assert_has_calls(
            expected_calls[1:3], any_order=False
        )

        assert state == ["OPERATE"] * 2

        with pytest.raises(ValueError):
            cpxe4iol.read_line_state([4])
            cpxe4iol.read_line_state([-1])
            cpxe4iol.read_line_state(4)
            cpxe4iol.read_line_state(-1)

    def test_read_device_error(self):
        """Test read_device_error per channel"""
        cpx_e = CpxE()
        cpxe4iol = cpx_e.add_module(CpxE4Iol())

        mocked_base = Mock()
        mocked_base.read_function_number = Mock(return_value=0xAB)
        cpxe4iol.base = mocked_base

        expected_calls = [
            call(4892 + 25),
            call(4892 + 26),
            call(4892 + 28),
            call(4892 + 29),
            call(4892 + 31),
            call(4892 + 32),
            call(4892 + 34),
            call(4892 + 35),
        ]

        state = cpxe4iol.read_device_error()
        mocked_base.read_function_number.assert_has_calls(
            expected_calls, any_order=False
        )
        assert state == [("0xb", "0xb")] * 4

        state = cpxe4iol.read_device_error(0)
        mocked_base.read_function_number.assert_has_calls(
            expected_calls, any_order=False
        )

        assert state == ("0xb", "0xb")

        state = cpxe4iol.read_device_error([1, 2])
        mocked_base.read_function_number.assert_has_calls(
            expected_calls[1:3], any_order=False
        )

        assert state == [("0xb", "0xb")] * 2

        with pytest.raises(ValueError):
            cpxe4iol.read_line_state([4])
            cpxe4iol.read_line_state([-1])
            cpxe4iol.read_line_state(4)
            cpxe4iol.read_line_state(-1)
