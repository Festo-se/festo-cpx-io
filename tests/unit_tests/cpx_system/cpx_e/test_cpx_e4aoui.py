"""Contains tests for cpx_e4aoui class"""
import pytest
from unittest.mock import Mock
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI


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
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        mocked_base = Mock(next_input_register=0, next_output_register=0)

        # Act
        MODULE_POSITION = 1
        cpxe4aoui.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe4aoui.base == mocked_base
        assert cpxe4aoui.position == MODULE_POSITION

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.input_register = 0
        cpxe4aoui.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

        # Act
        status = cpxe4aoui.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_channel_0_to_3(self):
        """Test read channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.base = Mock(read_reg_data=Mock(return_value=[0, 1000, 2000, 3000]))

        # Act
        channel_values = [cpxe4aoui.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aoui.base.read_reg_data.assert_called_with(
            cpxe4aoui.input_register, length=4
        )

    def test_getitem_0_to_3(self):
        """Test get item"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.base = Mock(read_reg_data=Mock(return_value=[0, 1000, 2000, 3000]))

        # Act
        channel_values = [cpxe4aoui[idx] for idx in range(4)]

        # Assert
        assert channel_values == [0, 1000, 2000, 3000]
        cpxe4aoui.base.read_reg_data.assert_called_with(
            cpxe4aoui.input_register, length=4
        )

    @pytest.mark.parametrize(
        "output_register, input_value, expected_value",
        [
            (0, (0, 1000), (1000, 0)),
            (0, (1, 2000), (2000, 1)),
            (1, (0, 1000), (1000, 1)),
            (1, (1, 2000), (2000, 2)),
        ],
    )
    def test_write_channel(self, output_register, input_value, expected_value):
        """test write channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.output_register = output_register
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui.write_channel(*input_value)

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(*expected_value)

    def test_write_channels(self):
        """test write channels"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.output_register = 0
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui.write_channels([0, 1, 2, 3])

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(
            [0, 1, 2, 3], cpxe4aoui.output_register, length=4
        )

    def test_set_channel_0(self):
        """Test set channel"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.output_register = 0
        cpxe4aoui.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4aoui[0] = 1000

        # Assert
        cpxe4aoui.base.write_reg_data.assert_called_with(
            1000, cpxe4aoui.output_register
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
    def test_configure_channel_diagnostics_wire_break_raise_error(self, input_value):
        """Test configure_channel_diagnostics_wire_break"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
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
    def test_configure_channel_diagnostics_overload_short_circuit_raise_error(
        self, input_value
    ):
        """Test configure_channel_diagnostics_overload_short_circuit"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
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
    def test_configure_channel_diagnostics_parameter_error_raise_error(
        self, input_value
    ):
        """Test configure_channel_diagnostics_parameter_error"""
        # Arrange
        cpxe4aoui = CpxE4AoUI()
        cpxe4aoui.position = 1
        cpxe4aoui.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4aoui.configure_channel_diagnostics_parameter_error(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((0, "0-10V"), (4892 + 11, 0xA1)),
            ((1, "4-20mA"), (4892 + 11, 0x6A)),
            ((2, "1-5V"), (4892 + 12, 0xA4)),
            ((3, "-20-+20mA"), (4892 + 12, 0x7A)),
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
            (0, "not_implemented"),
            (4, "0-10V"),
        ],
    )
    def test_configure_channel_range_raise_error(self, input_value):
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
