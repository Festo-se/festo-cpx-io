"""Contains tests for MotionHandler class"""
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_e import CpxE, CpxEEp, CpxE8Do


class TestCpxE8Do:
    def test_read_channel_0_to_7(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        cpxe8do.base = mocked_base

        assert cpxe8do.read_channel(0) == False
        assert cpxe8do.read_channel(1) == True
        assert cpxe8do.read_channel(2) == True
        assert cpxe8do.read_channel(3) == True
        assert cpxe8do.read_channel(4) == False
        assert cpxe8do.read_channel(5) == True
        assert cpxe8do.read_channel(6) == False
        assert cpxe8do.read_channel(7) == True
        mocked_base.read_reg_data.assert_called_with(cpxe8do.input_register)

    def test_getitem_0_to_7(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        cpxe8do.base = mocked_base

        # Exercise
        assert cpxe8do[0] == False
        assert cpxe8do[1] == True
        assert cpxe8do[2] == True
        assert cpxe8do[3] == True
        assert cpxe8do[4] == False
        assert cpxe8do[5] == True
        assert cpxe8do[6] == False
        assert cpxe8do[7] == True
        mocked_base.read_reg_data.assert_called_with(cpxe8do.input_register)

    def test_write_channel_0_true(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.write_channel(0, True)
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_write_channel_1_false(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.write_channel(1, False)
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )

    def test_setitem_0_true(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do[0] = True
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_setitem_1_false(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do[1] = False
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )

    def test_set_channel_0(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.set_channel(0)
        mocked_base.write_reg_data.assert_called_with(
            0b10101111, cpxe8do.output_register
        )

    def test_clear_channel_1(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE8Do()])
        cpxe8do = cpx_e.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0b10101110])
        mocked_base.write_reg_data = Mock()
        cpxe8do.base = mocked_base

        cpxe8do.clear_channel(1)
        mocked_base.write_reg_data.assert_called_with(
            0b10101100, cpxe8do.output_register
        )
