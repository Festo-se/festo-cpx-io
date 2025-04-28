"""Contains tests for cpx_e4iol class"""

from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol, CpxRequestError
from cpx_io.cpx_system.cpx_e.cpx_e_enums import OperatingMode, AddressSpace
from cpx_io.cpx_system.cpx_dataclasses import SystemEntryRegisters


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
        [
            (2, 1, 1, 1),
            (8, 1, 4, 4),
            (AddressSpace.PORT_2E2A, 1, 1, 1),
            (AddressSpace.PORT_8E8A, 1, 4, 4),
        ],
    )
    def test_configure(
        self, address_space, module_position, expected_insize, expected_outsize
    ):
        """Test configure function"""
        # Arrange
        cpxe4iol = CpxE4Iol(address_space)
        mocked_base = Mock(next_input_register=0, next_output_register=0, modules=[])

        # Act
        cpxe4iol._configure(mocked_base, module_position)

        # Assert
        assert cpxe4iol.base == mocked_base
        assert cpxe4iol.position == module_position
        assert cpxe4iol.module_input_size == expected_insize
        assert cpxe4iol.module_output_size == expected_outsize

    def test_read_status(self):
        """Test read channels"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.system_entry_registers = SystemEntryRegisters(inputs=0)
        cpxe4iol.base = Mock(read_reg_data=Mock(return_value=b"\xaa\xaa"))

        # Act
        status = cpxe4iol.read_status()

        # Assert
        assert status == [False, True] * 8

    def test_read_2byte_channel_0_to_3(self):
        """Test read channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.base = Mock(read_reg_data=Mock(return_value=b"\xa0\xa1"))
        cpxe4iol.system_entry_registers.inputs = 0
        channel_size = 1  # in registers

        # Act
        channel_values = [cpxe4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [b"\xa0\xa1"] * 4
        cpxe4iol.base.read_reg_data.assert_has_calls(
            [
                call(channel_size * 0, length=1),
                call(channel_size * 1, length=1),
                call(channel_size * 2, length=1),
                call(channel_size * 3, length=1),
            ]
        )

    def test_read_8byte_channel_0_to_3(self):
        """Test read channel"""
        # Arrange
        cpxe4iol = CpxE4Iol(8)
        cpxe4iol.base = Mock(
            read_reg_data=Mock(return_value=b"\xa1\x10\xa1\x11\xa1\x13\xa1\x14")
        )
        cpxe4iol.system_entry_registers.inputs = 0
        channel_size = 4  # in registers

        # Act
        channel_values = [cpxe4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [b"\xa1\x10\xa1\x11\xa1\x13\xa1\x14"] * 4
        cpxe4iol.base.read_reg_data.assert_has_calls(
            [
                call(channel_size * 0, length=4),
                call(channel_size * 1, length=4),
                call(channel_size * 2, length=4),
                call(channel_size * 3, length=4),
            ]
        )

    def test_read_2bytes_from_8byte_channel(self):
        """Test read channel"""
        # Arrange
        cpxe4iol = CpxE4Iol(8)
        cpxe4iol.base = Mock(
            read_reg_data=Mock(return_value=b"\xa1\x10\xa1\x11\xa1\x13\xa1\x14")
        )
        cpxe4iol.system_entry_registers.inputs = 0

        # Act
        channel_value = cpxe4iol.read_channel(0, bytelength=2)

        # Assert
        assert channel_value == b"\xa1\x10"

        cpxe4iol.base.read_reg_data.assert_called_with(0, length=4)

    def test_read_2bytes_from_8byte_channels(self):
        """Test read channels"""
        # Arrange
        cpxe4iol = CpxE4Iol(8)
        cpxe4iol.base = Mock(
            read_reg_data=Mock(
                return_value=b"\xa1\x10\xa1\x11\xa1\x13\xa1\x14"
                b"\xa2\x10\xa1\x11\xa1\x13\xa1\x14"
                b"\xa3\x10\xa1\x11\xa1\x13\xa1\x14"
                b"\xa4\x10\xa1\x11\xa1\x13\xa1\x14"
            )
        )
        cpxe4iol.system_entry_registers.inputs = 0

        # Act
        channel_values = cpxe4iol.read_channels(bytelength=2)

        # Assert
        assert channel_values == [b"\xa1\x10", b"\xa2\x10", b"\xa3\x10", b"\xa4\x10"]

        cpxe4iol.base.read_reg_data.assert_called_with(
            cpxe4iol.system_entry_registers.inputs, length=16
        )

    def test_getitem_0_to_3(self):
        """Test get item"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.base = Mock(read_reg_data=Mock(return_value=b"\x00\xab"))
        cpxe4iol.system_entry_registers.inputs = 0
        channel_size = 1  # size in registers

        # Act
        channel_values = [cpxe4iol[idx] for idx in range(4)]

        # Assert
        assert channel_values == [b"\x00\xab"] * 4

        cpxe4iol.base.read_reg_data.assert_has_calls(
            [
                call(channel_size * 0, length=1),
                call(channel_size * 1, length=1),
                call(channel_size * 2, length=1),
                call(channel_size * 3, length=1),
            ]
        )

    @pytest.mark.parametrize(
        "module_output_size, input_value, expected_value",
        [
            (1, (0, b"\x12\xab"), (b"\x12\xab", 1000)),
            (1, (1, b"\x34\xcd"), (b"\x34\xcd", 1001)),
            (2, (0, b"\x12\xab\x34\xcd"), (b"\x12\xab\x34\xcd", 1000)),
            (2, (1, b"\x12\xab\x34\xcd"), (b"\x12\xab\x34\xcd", 1002)),
        ],
    )
    def test_write_channel(self, module_output_size, input_value, expected_value):
        """test write channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.system_entry_registers = SystemEntryRegisters(outputs=1000)
        cpxe4iol.base = Mock(write_reg_data=Mock())
        cpxe4iol.module_output_size = module_output_size

        # Act
        cpxe4iol.write_channel(*input_value)

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(*expected_value)

    def test_setter_channel_0(self):
        """Test setter channel"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.system_entry_registers = SystemEntryRegisters(outputs=0)
        cpxe4iol.base = Mock(write_reg_data=Mock())

        # Act
        cpxe4iol[0] = b"\xfe\x00"

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(
            b"\xfe\x00", cpxe4iol.system_entry_registers.outputs
        )

    def test_write_channels_2byte(self):
        """Test write channels"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.system_entry_registers = SystemEntryRegisters(outputs=1000)
        cpxe4iol.base = Mock(write_reg_data=Mock())
        cpxe4iol.module_output_size = 1

        # Act
        cpxe4iol.write_channels([b"\x12\xab", b"\x34\xcd", b"\x56\xef", b"\x78\x00"])

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(
            b"\x12\xab\x34\xcd\x56\xef\x78\x00", cpxe4iol.system_entry_registers.outputs
        )

    def test_write_channels_4byte(self):
        """Test write channels"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.system_entry_registers = SystemEntryRegisters(outputs=1000)
        cpxe4iol.base = Mock(write_reg_data=Mock())
        cpxe4iol.module_output_size = 2

        # Act
        cpxe4iol.write_channels(
            [
                b"\x12\xab\x01\x02",
                b"\x34\xcd\x03\x04",
                b"\x56\xef\x05\x06",
                b"\x78\x00\x07\x08",
            ]
        )

        # Assert
        cpxe4iol.base.write_reg_data.assert_called_with(
            b"\x12\xab\x01\x02\x34\xcd\x03\x04\x56\xef\x05\x06\x78\x00\x07\x08",
            cpxe4iol.system_entry_registers.outputs,
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
            (True, (4892 + 1, 0xAA)),
            (False, (4892 + 1, 0xA8)),
        ],
    )
    def test_configure_behaviour_after_sco(self, input_value, expected_value):
        """Test configure_behaviour_after_sco"""
        # Arrange
        cpxe4iol = CpxE4Iol()
        cpxe4iol.position = 1
        cpxe4iol.base = Mock(
            read_function_number=Mock(return_value=0xAA), write_reg_data=Mock()
        )

        # Act
        cpxe4iol.configure_behaviour_after_sco(input_value)

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
            (
                (OperatingMode.IO_LINK, None),
                [
                    call(4892 + 11, 0xAB),
                    call(4892 + 15, 0xAB),
                    call(4892 + 19, 0xAB),
                    call(4892 + 23, 0xAB),
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

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_read_isdu_different_channels(self, input_value):
        """Test read_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data_with_single_cmds = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        channel = input_value
        index = 4
        subindex = 5

        result = module.read_isdu(channel, index, subindex)

        # Assert
        module.base.write_reg_data_with_single_cmds.assert_has_calls(
            [
                call(b"\x01\x00", 61),  # MODULE_NO
                call((channel).to_bytes(2, "little"), 62),  # CHANNEL
                call(b"\x04\x00", 63),  # INDEX
                call(b"\x05\x00", 64),  # SUBINDEX
                call(b"\x00\x00", 65),  # LENGTH zero when reading
                call(b"\x32\x00", 60),  # COMMAND (read 50)
            ]
        )
        module.base.read_reg_data.assert_has_calls(
            [
                call(60, 1),
                call(65),
                call(66, 0),
            ]
        )

        assert (
            result == b""
        )  # will cut to the actual_length which is returned with 0 in this test

    def test_read_isdu_no_response(self):
        """Test read_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x01\x00")

        # Act & Assert
        channel = 0
        index = 4
        subindex = 5

        with pytest.raises(CpxRequestError):
            module.read_isdu(channel, index, subindex)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_write_isdu_different_channels(self, input_value):
        """Test write_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data_with_single_cmds = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = b"\xca\xfe"
        channel = input_value
        index = 4  # random
        subindex = 5  # random

        module.write_isdu(data, channel, index, subindex)

        # Assert
        module.base.write_reg_data_with_single_cmds.assert_has_calls(
            [
                call(b"\x01\x00", 61),  # MODULE_NO
                call((channel).to_bytes(2, "little"), 62),  # CHANNEL
                call(b"\x04\x00", 63),  # INDEX
                call(b"\x05\x00", 64),  # SUBINDEX
                call(b"\x02\x00", 65),  # LENGTH (bytes)
                call(data, 66),  # DATA
                call(b"\x33\x00", 60),  # COMMAND 51
            ]
        )

    @pytest.mark.parametrize(
        "input_value",
        [
            b"\x01",
            b"\x01\x02",
            b"\x01\x02\x03",
            b"\x01\x02\x03\x04",
        ],
    )
    def test_write_isdu_different_lengths(self, input_value):
        """Test write_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data_with_single_cmds = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = input_value
        channel = 0  # random
        index = 4  # random
        subindex = 5  # random

        module.write_isdu(data, channel, index, subindex)
        length = len(data)

        # Assert
        module.base.write_reg_data_with_single_cmds.assert_has_calls(
            [
                call(b"\x01\x00", 61),  # MODULE_NO
                call((channel).to_bytes(2, "little"), 62),  # CHANNEL
                call(b"\x04\x00", 63),  # INDEX
                call(b"\x05\x00", 64),  # SUBINDEX
                call(length.to_bytes(2, "little"), 65),  # LENGTH
                call(data, 66),  # DATA
                call(b"\x33\x00", 60),  # COMMAND 51
            ]
        )

    @pytest.mark.parametrize(
        "input_value, length, expected_output",
        [
            ("str", 0, ""),
            ("int8", 1, 0),
            ("int16", 2, 0),
            ("int32", 4, 0),
            ("uint8", 1, 0),
            ("uint16", 2, 0),
            ("uint32", 4, 0),
            ("raw", 4, b"\x00\x00\x00\x00"),
            ("bool", 1, False),
            ("float32", 4, 0.0),
        ],
    )
    def test_read_isdu_different_datatypes(self, input_value, length, expected_output):
        """Test read_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data = Mock()
        length_bytes = length.to_bytes(2, "little")
        module.base.read_reg_data = Mock(
            side_effect=[b"\x00\x00", length_bytes, b"\x00\x00\x00\x00"]
        )

        # Act
        ret = module.read_isdu(0, 0, data_type=input_value)

        # Assert
        assert ret == expected_output

    @pytest.mark.parametrize(
        "input_value, length, data_type, expected_output",
        [
            ("abc", 3, "str", b"abc"),  # string
            (1, 1, "uint8", b"\x01"),  # uint8
            (0xCAFE, 2, "uint16", b"\xca\xfe"),  # uint16
            (0xBEBAFECA, 4, "uint32", b"\xbe\xba\xfe\xca"),  # uint32
            (-1, 1, "int8", b"\xff"),  # sint8
            (-1925, 2, "int16", b"\xf8\x7b"),  # sint16
            (-999999, 4, "int32", b"\xff\xf0\xbd\xc1"),  # 3byte sint32
            (-99999999, 4, "int32", b"\xfa\x0a\x1f\x01"),  # sint32
            (b"\xca\xfe", 2, "raw", b"\xca\xfe"),  # bytes = raw
            (True, 1, "bool", b"\x01"),  # bool true
            (False, 1, "bool", b"\x00"),  # bool false
            (0.0, 4, "float32", b"\x00\x00\x00\x00"),  # float 0
            (-1.23456, 4, "float32", b"\xbf\x9e\x06\x10"),  # negative float
        ],
    )
    def test_write_isdu_different_datatypes(
        self, input_value, length, data_type, expected_output
    ):
        """Test read_isdu"""
        # Arrange
        module = CpxE4Iol()
        module.position = 1
        module.base = Mock()
        module.base.write_reg_data_with_single_cmds = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        module.write_isdu(input_value, 0, 0, data_type=data_type)

        # Assert
        module.base.write_reg_data_with_single_cmds.assert_has_calls(
            [
                call(b"\x01\x00", 61),  # MODULE_NO
                call(b"\x00\x00", 62),  # CHANNEL
                call(b"\x00\x00", 63),  # INDEX
                call(b"\x00\x00", 64),  # SUBINDEX
                call(length.to_bytes(2, "little"), 65),  # LENGTH
                call(expected_output, 66),  # DATA
                call(b"\x33\x00", 60),  # COMMAND
            ]
        )
