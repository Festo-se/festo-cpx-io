"""Contains tests for cpx_e16di class"""

import pytest
from unittest.mock import Mock

from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di


class TestCpxE16Di:
    """Test cpx-e-16di"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxe16di = CpxE16Di()

        # Assert
        assert cpxe16di.base is None
        assert cpxe16di.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxe16di = CpxE16Di()
        mocked_base = Mock(next_input_register=0, modules=[])

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        cpxe16di.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxe16di.base == mocked_base
        assert cpxe16di.position == MODULE_POSITION

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.input_register = 0
        cpxe16di.base = Mock(read_reg_data=Mock(return_value=b"\xAA\xAA"))

        # Act
        status = cpxe16di.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_channel_0_to_15(self):
        """Test read channels"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.base = Mock(read_reg_data=Mock(return_value=b"\xAE\xCC"))

        # Act
        channel_values = [cpxe16di.read_channel(idx) for idx in range(16)]

        # Assert
        assert channel_values == [
            False,
            True,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            False,
            True,
            True,
            False,
            False,
            True,
            True,
        ]
        cpxe16di.base.read_reg_data.assert_called_with(cpxe16di.input_register)

    def test_getitem_0_to_15(self):
        """Test get item"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.base = Mock(read_reg_data=Mock(return_value=b"\xAE\xCC"))

        # Act
        channel_values = [cpxe16di[idx] for idx in range(16)]

        # Assert
        assert channel_values == [
            False,
            True,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            False,
            True,
            True,
            False,
            False,
            True,
            True,
        ]
        cpxe16di.base.read_reg_data.assert_called_with(cpxe16di.input_register)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(False, (4892, 0xAA)), (True, (4892, 0xAB))],
    )
    def test_configure_diagnostics(self, input_value, expected_value):
        """Test diagnostics"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.position = 1
        cpxe16di.base = Mock(read_function_number=Mock(return_value=0xAA))

        cpxe16di.configure_diagnostics(input_value)
        cpxe16di.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(False, (4893, 0xAA)), (True, (4893, 0xAB))],
    )
    def test_configure_power_reset(self, input_value, expected_value):
        """Test power reset"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.position = 1
        cpxe16di.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe16di.configure_power_reset(input_value)
        cpxe16di.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(0, (4893, 0x8A)), (3, (4893, 0xBA))],
    )
    def test_configure_debounce_time(self, input_value, expected_value):
        """Test debounce time"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.position = 1
        cpxe16di.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe16di.configure_debounce_time(input_value)

        # Assert
        cpxe16di.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_debounce_time_raise_error(self, input_value):
        """Test debounce time"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe16di.configure_debounce_time(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(0, (4893, 0x2A)), (3, (4893, 0xEA))],
    )
    def test_configure_signal_extension_time(self, input_value, expected_value):
        """Test debounce time"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.position = 1
        cpxe16di.base = Mock(read_function_number=Mock(return_value=0xAA))

        # Act
        cpxe16di.configure_signal_extension_time(input_value)
        cpxe16di.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_signal_extension_time_raise_error(self, input_value):
        """Test debounce time"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe16di.configure_signal_extension_time(input_value)

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxe16di = CpxE16Di()
        cpxe16di.position = 1

        # Act
        module_repr = repr(cpxe16di)

        # Assert
        assert module_repr == "cpxe16di (idx: 1, type: CpxE16Di)"
