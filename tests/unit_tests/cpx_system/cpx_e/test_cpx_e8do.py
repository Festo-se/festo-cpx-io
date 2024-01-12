"""Contains tests for cpx_e8do class"""
import pytest
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do


class TestCpxE8Do:
    """Test cpx-e-8do"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxe8do = CpxE8Do()

        # Assert
        assert cpxe8do.base is None
        assert cpxe8do.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxe8do = CpxE8Do()
        mocked_base = Mock(next_input_register=0, next_output_register=0, modules=[])

        # Act
        MODULE_POSITION = 1
        cpxe8do.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe8do.base == mocked_base
        assert cpxe8do.position == MODULE_POSITION

    def test_read_status(self):
        """Test read status"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.input_register = 0
        cpxe8do.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

        # Act
        status = cpxe8do.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_channel_0_to_7(self):
        """Test read channels"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.input_register = 0
        cpxe8do.base = Mock(read_reg_data=Mock(return_value=[0b10101110]))

        # Act
        channel_values = [cpxe8do.read_channel(idx) for idx in range(8)]

        assert channel_values == [False, True, True, True, False, True, False, True]
        cpxe8do.base.read_reg_data.assert_called_with(cpxe8do.input_register)

    def test_getitem_0_to_7(self):
        """Test get item"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.input_register = 0
        cpxe8do.base = Mock(read_reg_data=Mock(return_value=[0b10101110]))

        # Act
        channel_values = [cpxe8do[idx] for idx in range(8)]

        # Assert
        assert channel_values == [False, True, True, True, False, True, False, True]
        cpxe8do.base.read_reg_data.assert_called_with(cpxe8do.input_register)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                [
                    True,
                    False,
                    True,
                    True,
                    True,
                    False,
                    True,
                    False,
                ],
                (0b01011101, 0),
            ),
        ],
    )
    def test_write_channels(self, input_value, expected_value):
        """test write channel true"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = 0
        cpxe8do.base = Mock(write_reg_data=Mock())

        # Act
        cpxe8do.write_channels(input_value)

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            [],
            [1],
            [1, 2, 3],
        ],
    )
    def test_write_channels_raise_error(self, input_value):
        """test write channel true"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = 0
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe8do.write_channels(input_value)

    @pytest.mark.parametrize(
        "output_register, input_value, expected_value",
        [
            (0, (0, True), (0b10101111, 0)),
            (0, (1, False), (0b10101100, 0)),
            (1, (0, True), (0b10101111, 1)),
            (1, (1, False), (0b10101100, 1)),
        ],
    )
    def test_write_channel(self, output_register, input_value, expected_value):
        """test write channel true"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = output_register
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act
        cpxe8do.write_channel(*input_value)

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "output_register, input_value, expected_value",
        [
            (0, (0, True), (0b10101111, 0)),
            (0, (1, False), (0b10101100, 0)),
            (1, (0, True), (0b10101111, 1)),
            (1, (1, False), (0b10101100, 1)),
        ],
    )
    def test_setitem(self, output_register, input_value, expected_value):
        """Test set item true"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = output_register
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act
        cpxe8do[input_value[0]] = input_value[True]

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(*expected_value)

    def test_set_channel(self):
        """Test set channel"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = 0
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act
        cpxe8do.set_channel(0)

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(0b10101111, 0)

    def test_clear_channel(self):
        """Test clear channel"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = 0
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act
        cpxe8do.clear_channel(1)

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(0b10101100, 0)

    def test_toggle_channel(self):
        """Test toggle channel"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.output_register = 0
        cpxe8do.base = Mock(
            read_reg_data=Mock(return_value=[0b10101110]), write_reg_data=Mock()
        )

        # Act
        cpxe8do.toggle_channel(2)

        # Assert
        cpxe8do.base.write_reg_data.assert_called_with(
            0b10101010, cpxe8do.output_register
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            ((None, None), (4892, 0xAA)),
            ((False, None), (4892, 0xA8)),
            ((None, True), (4892, 0xAE)),
            ((False, True), (4892, 0xAC)),
        ],
    )
    def test_configure_diagnostics(self, input_value, expected_value):
        """Test diagnostics"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.position = 1
        cpxe8do.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe8do.configure_diagnostics(*input_value)

        # Assert
        cpxe8do.base.write_function_number.assert_called_with(*expected_value)

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
        cpxe8do = CpxE8Do()
        cpxe8do.position = 1
        cpxe8do.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_function_number=Mock()
        )

        # Act
        cpxe8do.configure_power_reset(input_value)

        # Assert
        cpxe8do.base.write_function_number.assert_called_with(*expected_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxe8do = CpxE8Do()
        cpxe8do.position = 1

        # Act
        module_repr = repr(cpxe8do)

        # Assert
        assert module_repr == "cpxe8do (idx: 1, type: CpxE8Do)"
