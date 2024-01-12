"""Contains tests for cpx_e4iol class"""
import pytest
from unittest.mock import Mock, call

from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol


class TestCpxE4Iol:
    """Test cpx-e-4iol"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxe4iol = CpxE4Iol()
        # Assert
        assert cpxe4iol.base is None
        assert cpxe4iol.position is None

    def test_constructor_raise_error(self):
        """Test initialize function"""
        # Arrange

        # Act & Assert
        with pytest.raises(ValueError):
            CpxE4Iol(3)

    @pytest.mark.parametrize(
        "address_space, module_position, expected_insize, expected_outsize",
        [(2, 1, 1, 1), (8, 1, 4, 4)],
    )
    def test_configure(
        self, address_space, module_position, expected_insize, expected_outsize
    ):
        # Arrange
        cpxe4iol = CpxE4Iol(address_space)
        mocked_base = Mock(next_input_register=0, next_output_register=0, modules=[])

        # Act
        cpxe4iol.configure(mocked_base, module_position)

        # Assert
        assert cpxe4iol.base == mocked_base
        assert cpxe4iol.position == module_position
        assert cpxe4iol.module_input_size == expected_insize
        assert cpxe4iol.module_output_size == expected_outsize

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.input_register = 0
        cpxe4iol.base = Mock(read_reg_data=Mock(return_value=[0xAAAA]))

        # Act
        status = cpxe4iol.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_2byte_channel_0_to_3(self):
        """Test read channels"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.base = Mock(
            read_reg_data=Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        )

        # Act
        channel_values = [cpxe4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [[0xAB00], [0xCD00], [0xEF00], [0x1200]]
        cpxe4iol.base.read_reg_data.assert_called_with(
            cpxe4iol.input_register, length=4
        )

    def test_read_8byte_channel_0_to_3(self):
        """Test read channels"""
        # Arrange
        cpxe4iol = CpxE4Iol(8)
        cpxe4iol.base = Mock(
            read_reg_data=Mock(
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
        )

        # Act
        channel_values = [cpxe4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [
            [0x10A1, 0x11A1, 0x13A1, 0x14A1],
            [0x10B1, 0x11B1, 0x13B1, 0x14B1],
            [0x10C1, 0x11C1, 0x13C1, 0x14C1],
            [0x10D1, 0x11D1, 0x13D1, 0x14D1],
        ]
        cpxe4iol.base.read_reg_data.assert_called_with(
            cpxe4iol.input_register, length=16
        )

    def test_getitem_0_to_3(self):
        """Test get item"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.base = Mock(
            read_reg_data=Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        )

        # Act
        channel_values = [cpxe4iol[idx] for idx in range(4)]

        # Assert
        assert channel_values == [[0xAB00], [0xCD00], [0xEF00], [0x1200]]
        cpxe4iol.base.read_reg_data.assert_called_with(
            cpxe4iol.input_register, length=4
        )

    def test_read_outputs_0_to_3(self):
        """Test read outputs"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.input_register = 0
        cpxe4iol.base = Mock(
            read_reg_data=Mock(return_value=[0x00AB, 0x00CD, 0x00EF, 0x0012])
        )

        # Act
        channel_values = [cpxe4iol.read_output_channel(idx) for idx in range(4)]

        # Exercise
        assert channel_values == [[0xAB00], [0xCD00], [0xEF00], [0x1200]]
        cpxe4iol.base.read_reg_data.assert_called_with(
            cpxe4iol.input_register + 4, length=4
        )

    @pytest.mark.parametrize(
        "output_register, input_value, expected_value",
        [
            (0, (0, [0xAB]), ([0xAB00], 0)),
            (0, (1, [0xCD]), ([0xCD00], 1)),
            (1, (0, [0xAB]), ([0xAB00], 1)),
            (1, (1, [0xCD]), ([0xCD00], 2)),
        ],
    )
    def test_write_channel(self, output_register, input_value, expected_value):
        """test write channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.output_register = output_register
        cpxe4iol.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4iol.write_channel(*input_value)

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(*expected_value)

    def test_set_channel_0(self):
        """Test set channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.output_register = 0
        cpxe4iol.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4iol[0] = [0xFE]

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(
            [0xFE00], cpxe4iol.output_register
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4892, 0xAE)),
            (False, (4892, 0xAA)),
        ],
    )
    def test_configure_monitoring_uload(self, input_value, expected_value):
        """Test configure_monitoring_uload"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_monitoring_uload(input_value)

        # Assert
        cpxe4iol.base.read_function_number.assert_called_with(expected_value[0])
        cpxe4iol.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4892 + 1, 0xAB)),
            (False, (4892 + 1, 0xAA)),
        ],
    )
    def test_configure_behaviour_after_scl(self, input_value, expected_value):
        """Test configure_behaviour_after_scl"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_behaviour_after_scl(input_value)

        # Assert
        cpxe4iol.base.read_function_number.assert_called_with(expected_value[0])
        cpxe4iol.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (True, (4892 + 6, 0xAB)),
            (False, (4892 + 6, 0xAA)),
        ],
    )
    def test_configure_ps_supply(self, input_value, expected_value):
        """Test configure_ps_supply"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_ps_supply(input_value)

        # Assert
        cpxe4iol.base.read_function_number.assert_called_with(expected_value[0])
        cpxe4iol.base.write_function_number.assert_called_with(*expected_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                ((10, 20), None),
                [
                    call(4892 + 8, 10),
                    call(4892 + 9, 20),
                    call(4892 + 12, 10),
                    call(4892 + 13, 20),
                    call(4892 + 16, 10),
                    call(4892 + 17, 20),
                    call(4892 + 20, 10),
                    call(4892 + 21, 20),
                ],
            ),
            (
                ((10, 20), 0),
                [
                    call(4892 + 8, 10),
                    call(4892 + 9, 20),
                ],
            ),
            (
                ((10, 20), [1, 2]),
                [
                    call(4892 + 12, 10),
                    call(4892 + 13, 20),
                    call(4892 + 16, 10),
                    call(4892 + 17, 20),
                ],
            ),
        ],
    )
    def test_configure_cycle_time(self, input_value, expected_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(write_function_number=Mock())

        # Act
        cpxe4iol.configure_cycle_time(*input_value)

        # Assert
        cpxe4iol.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            (True, -1),
            (True, 4),
        ],
    )
    def test_configure_cycle_time_raise_error(self, input_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4iol.configure_cycle_time(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                (True, None),
                [
                    call(4892 + 10, 0xAB),
                    call(4892 + 14, 0xAB),
                    call(4892 + 18, 0xAB),
                    call(4892 + 22, 0xAB),
                ],
            ),
            (
                (False, None),
                [
                    call(4892 + 10, 0xAA),
                    call(4892 + 14, 0xAA),
                    call(4892 + 18, 0xAA),
                    call(4892 + 22, 0xAA),
                ],
            ),
            (
                (True, 0),
                [
                    call(4892 + 10, 0xAB),
                ],
            ),
            (
                (False, 0),
                [
                    call(4892 + 10, 0xAA),
                ],
            ),
            (
                (True, [1, 2]),
                [
                    call(4892 + 14, 0xAB),
                    call(4892 + 18, 0xAB),
                ],
            ),
            (
                (False, [1, 2]),
                [
                    call(4892 + 14, 0xAA),
                    call(4892 + 18, 0xAA),
                ],
            ),
        ],
    )
    def test_configure_pl_supply(self, input_value, expected_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_pl_supply(*input_value)

        # Assert
        cpxe4iol.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            (True, -1),
            (True, 4),
        ],
    )
    def test_configure_pl_supply_raise_error(self, input_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4iol.configure_pl_supply(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                (3, None),
                [
                    call(4892 + 11, 0xAB),
                    call(4892 + 15, 0xAB),
                    call(4892 + 19, 0xAB),
                    call(4892 + 23, 0xAB),
                ],
            ),
            (
                (3, 0),
                [
                    call(4892 + 11, 0xAB),
                ],
            ),
            (
                (3, [1, 2]),
                [
                    call(4892 + 15, 0xAB),
                    call(4892 + 19, 0xAB),
                ],
            ),
        ],
    )
    def test_configure_operating_mode(self, input_value, expected_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_operating_mode(*input_value)
        # Assert
        cpxe4iol.base.write_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            (4, 0),
            (-1, 0),
            (0, [-1]),
            (0, [4]),
            (0, -1),
            (0, 4),
        ],
    )
    def test_configure_operating_mode_raise_error(self, input_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4iol.configure_operating_mode(*input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                (None),
                [
                    call(4892 + 24),
                    call(4892 + 27),
                    call(4892 + 30),
                    call(4892 + 33),
                ],
            ),
            (
                (0),
                [
                    call(4892 + 24),
                ],
            ),
            (
                ([1, 2]),
                [
                    call(4892 + 27),
                    call(4892 + 30),
                ],
            ),
        ],
    )
    def test_read_line_state(self, input_value, expected_value):
        """Test read_line_state per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(read_function_number=Mock(return_value=0xAD))

        # Act
        state = cpxe4iol.read_line_state(input_value)

        # Assert
        assert (
            state == ["OPERATE"] * len(expected_value)
            if len(expected_value) > 1
            else "OPERATE"
        )
        cpxe4iol.base.read_function_number.assert_has_calls(
            expected_value, any_order=False
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            ([4]),
            ([-1]),
            (4),
            (-1),
        ],
    )
    def test_read_line_state_raise_error(self, input_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4iol.read_line_state(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                (None),
                [("0xb", "0xb")] * 4,
            ),
            (
                (0),
                ("0xb", "0xb"),
            ),
            (
                ([1, 2]),
                [("0xb", "0xb")] * 2,
            ),
        ],
    )
    def test_read_device_error(self, input_value, expected_value):
        """Test read_device_error per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(read_function_number=Mock(return_value=0xAB))

        # Act
        state = cpxe4iol.read_device_error(input_value)

        # Assert
        assert state == expected_value
        cpxe4iol.base.read_function_number.assert_has_calls(
            [
                call(4892 + 25),
                call(4892 + 26),
                call(4892 + 28),
                call(4892 + 29),
                call(4892 + 31),
                call(4892 + 32),
                call(4892 + 34),
                call(4892 + 35),
            ],
            any_order=False,
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            ([4]),
            ([-1]),
            (4),
            (-1),
        ],
    )
    def test_read_device_error_raise_error(self, input_value):
        """Test configure_cycle_time per channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock()

        # Act & Assert
        with pytest.raises(ValueError):
            cpxe4iol.read_device_error(input_value)
