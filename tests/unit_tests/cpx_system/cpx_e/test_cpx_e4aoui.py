"""Contains tests for cpx_e4aoui class"""

from unittest.mock import Mock
import pytest
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.cpx_e_enums import ChannelRange
from cpx_io.cpx_system.cpx_dataclasses import StartRegisters


class TestCpxE4AoUI:
    """Test cpx-e-4aoui"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxe4aoui = CpxE4AoUI()

        # Assert
        assert cpxe4aoui.base is None
        assert cpxe4aoui.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        mocked_base = Mock(next_input_register=0, next_output_register=0, modules=[])

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        cpxe4aoui.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe4aoui.base == mocked_base
        assert cpxe4aoui.position == MODULE_POSITION

    def test_read_status(self):
        """Test read status"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(inputs=0)
        cpxe4aoui.base = Mock(read_reg_data=Mock(return_value=b"\xAA\xAA"))

        # Act
        status = cpxe4aoui.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_channel_0_to_3(self):
        """Test read channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.base = Mock(
            read_reg_data=Mock(return_value=b"\x00\x00\xE8\x03\xD0\x07\xB8\x0B")
        )

        # Act
        channel_values = [cpxe4aoui.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aoui.base.read_reg_data.assert_called_with(
            cpxe4aoui.start_registers.inputs, length=4
        )

    def test_getitem_0_to_3(self):
        """Test get item"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.base = Mock(
            read_reg_data=Mock(return_value=b"\x00\x00\xE8\x03\xD0\x07\xB8\x0B")
        )

        # Act
        channel_values = [cpxe4aoui[idx] for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aoui.base.read_reg_data.assert_called_with(
            cpxe4aoui.start_registers.inputs, length=4
        )

    @pytest.mark.parametrize(
        "output_register, input_value, expected_value",
        [
            (0, (0, 1000), (b"\xE8\x03", 0)),
            (0, (1, 2000), (b"\xD0\x07", 1)),
            (1, (0, 1000), (b"\xE8\x03", 1)),
            (1, (1, 2000), (b"\xD0\x07", 2)),
        ],
    )
    def test_write_channel(self, output_register, input_value, expected_value):
        """test write channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=output_register)
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui.write_channel(*input_value)

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(*expected_value)

    def test_write_channels(self):
        """test write channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui.write_channels([0, 1, 2, 3])

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(
            b"\x00\x00\x01\x00\x02\x00\x03\x00", cpxe4aoui.start_registers.outputs
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_read_channel_out_of_range(self, input_value):
        """test read channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.read_channel(input_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_write_channel_out_of_range(self, input_value):
        """test write channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.write_channel(input_value, 0)

    @pytest.mark.parametrize("input_value", [[0], [0, 1], [0, 1, 2], [0, 1, 2, 3, 4]])
    def test_write_channels_wrong_length(self, input_value):
        """test write channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aoui.write_channels(input_value)

    def test_write_channels_negative(self):
        """test write channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui.write_channels([0, -1, -2, -3])

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(
            b"\x00\x00\xff\xff\xfe\xff\xfd\xff", cpxe4aoui.start_registers.outputs
        )

    def test_set_channel_0(self):
        """Test set channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.start_registers = StartRegisters(outputs=0)
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui[0] = 1000

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(
            b"\xE8\x03", cpxe4aoui.start_registers.outputs
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((None, None, None), (4892, 0xAA)),
            ((False, None, None), (4892, 0xA8)),
            ((None, None, False), (4892, 0x2A)),
            ((None, True, None), (4892, 0xAE)),
            ((False, True, False), (4892, 0x2C)),
        ],
    )
    def test_configure_diagnostics(self, input_value, expected_value):
        """Test diagnostics"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_diagnostics(*input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4893, 0xAA)),
            (False, (4893, 0xA8)),
        ],
    )
    def test_configure_power_reset(self, input_value, expected_value):
        """Test power reset"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_power_reset(input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4893, 0xAA)),
            (False, (4893, 0xA2)),
        ],
    )
    def test_configure_behaviour_overload(self, input_value, expected_value):
        """Test behaviour overload"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_behaviour_overload(input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

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
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_data_format(input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4898, 0xAA)),
            (False, (4898, 0x8A)),
        ],
    )
    def test_configure_actuator_supply(self, input_value, expected_value):
        """Test actuator supply"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_actuator_supply(input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 7, 0xAE)),
            ((0, False), (4892 + 7, 0xAA)),
            ((1, True), (4892 + 8, 0xAE)),
            ((1, False), (4892 + 8, 0xAA)),
            ((2, True), (4892 + 9, 0xAE)),
            ((2, False), (4892 + 9, 0xAA)),
            ((3, True), (4892 + 10, 0xAE)),
            ((3, False), (4892 + 10, 0xAA)),
        ],
    )
    def test_configure_channel_diagnostics_wire_break(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_wire_break"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_channel_diagnostics_wire_break(*input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            (4, False),
            (-1, False),
        ],
    )
    def test_configure_channel_diagnostics_wire_break_wrong_channel(self, input_value):
        """Test configure_channel_diagnostics_wire_break"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.configure_channel_diagnostics_wire_break(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 7, 0xBA)),
            ((0, False), (4892 + 7, 0xAA)),
            ((1, True), (4892 + 8, 0xBA)),
            ((1, False), (4892 + 8, 0xAA)),
            ((2, True), (4892 + 9, 0xBA)),
            ((2, False), (4892 + 9, 0xAA)),
            ((3, True), (4892 + 10, 0xBA)),
            ((3, False), (4892 + 10, 0xAA)),
        ],
    )
    def test_configure_channel_diagnostics_overload_short_circuit(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_overload_short_circuit"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_channel_diagnostics_overload_short_circuit(*input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            (4, False),
            (-1, False),
        ],
    )
    def test_configure_channel_diagnostics_overload_short_circuit_wrong_channel(
        self, input_value
    ):
        """Test configure_channel_diagnostics_overload_short_circuit"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.configure_channel_diagnostics_overload_short_circuit(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, True), (4892 + 7, 0xAA)),
            ((0, False), (4892 + 7, 0x2A)),
            ((1, True), (4892 + 8, 0xAA)),
            ((1, False), (4892 + 8, 0x2A)),
            ((2, True), (4892 + 9, 0xAA)),
            ((2, False), (4892 + 9, 0x2A)),
            ((3, True), (4892 + 10, 0xAA)),
            ((3, False), (4892 + 10, 0x2A)),
        ],
    )
    def test_configure_channel_diagnostics_parameter_error(
        self, input_value, expected_value
    ):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_channel_diagnostics_parameter_error(*input_value)

        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            (4, False),
            (-1, False),
        ],
    )
    def test_configure_channel_diagnostics_parameter_error_wrong_channel(
        self, input_value
    ):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.configure_channel_diagnostics_parameter_error(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, ChannelRange.U_10V), (4892 + 11, 0xA1)),
            ((1, ChannelRange.U_4_20MA), (4892 + 11, 0x6A)),
            ((2, ChannelRange.U_1_5V), (4892 + 12, 0xA4)),
            ((3, ChannelRange.B_20MA), (4892 + 12, 0x7A)),
        ],
    )
    def test_configure_channel_range(self, input_value, expected_value):
        """Test channel range"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe4aoui.configure_channel_range(*input_value)  # 0001
        # Assert
        cpxe4aoui.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            (4, 8),
            (-1, 0),
        ],
    )
    def test_configure_channel_range_raise_error_wrong_channel(self, input_value):
        """Test channel range"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(IndexError):
            cpxe4aoui.configure_channel_range(*input_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            (0, -1),
            (1, 50000),
        ],
    )
    def test_configure_channel_range_raise_error_wrong_input(self, input_value):
        """Test channel range"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aoui.configure_channel_range(*input_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1

        # Act
        module_repr = repr(cpxe4aoui)

        # Assert
        assert module_repr == "cpxe4aoui (idx: 1, type: CpxE4AoUI)"
