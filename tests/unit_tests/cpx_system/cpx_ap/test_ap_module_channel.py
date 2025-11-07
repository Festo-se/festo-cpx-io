"""Contains tests for ApModule class"""

from unittest.mock import Mock, call, patch
from collections import namedtuple
import pytest

from cpx_io.cpx_system.cpx_base import CpxRequestError
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation
from cpx_io.cpx_system.cpx_ap.dataclasses.system_parameters import SystemParameters
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import Channel
from cpx_io.cpx_system.cpx_dataclasses import SystemEntryRegisters
from cpx_io.utils.helpers import div_ceil


def channel_fixture_bool(bit_offset, array_size=None, byte_swap=None):
    return Channel(
        array_size=array_size,
        bits=1 if array_size is None else array_size,
        bit_offset=bit_offset,
        byte_swap_needed=byte_swap,
        channel_id=0,
        data_type="BOOL",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int8(bit_offset, array_size=None, byte_swap=None):
    return Channel(
        array_size=array_size,
        bits=8 if array_size is None else array_size * 8,
        bit_offset=bit_offset,
        byte_swap_needed=byte_swap,
        channel_id=1,
        data_type="INT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int16(bit_offset, array_size=None, byte_swap=None):
    return Channel(
        array_size=array_size,
        bits=16 if array_size is None else array_size * 16,
        bit_offset=bit_offset,
        byte_swap_needed=byte_swap,
        channel_id=2,
        data_type="INT16",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint8(bit_offset, array_size=None, byte_swap=None):
    return Channel(
        array_size=array_size,
        bits=8 if array_size is None else array_size * 8,
        bit_offset=bit_offset,
        byte_swap_needed=byte_swap,
        channel_id=4,
        data_type="UINT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint16(bit_offset, array_size=None, byte_swap=None):
    return Channel(
        array_size=array_size,
        bits=16 if array_size is None else array_size * 16,
        bit_offset=bit_offset,
        byte_swap_needed=byte_swap,
        channel_id=5,
        data_type="UINT16",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


class TestApModule:
    "Test ApModule"

    @pytest.fixture(scope="function")
    def module_fixture(self):
        """module fixture"""
        apdd_information = ApddInformation(
            "Description",
            "Name",
            "Module Type",
            "Configurator Code",
            "Part Number",
            "Module Class",
            "Module Code",
            "Order Text",
            "Product Category",
            "Product Family",
        )

        channels = ([], [], [])
        parameters = []
        module_diagnosis = []

        yield ApModule(
            apdd_information,
            channels,
            parameters,
            module_diagnosis,
            variant_list=[],
            variant_switch_parameter=None,
        )

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (
                [channel_fixture_bool(i) for i in range(0, 59)],
                [True] * 8
                + [False] * 4
                + [True] * 4
                + [False] * 6
                + [True] * 2
                + [True, False] * 2
                + [False, True] * 2
                + [False, True, False, False]
                + [True, False, False, True]
                + [False, True, True, False]
                + [True, True, False, False]
                + [True] * 3
                + [False] * 3
                + [True, False]
                + [False] * 3,
            ),
            (
                [channel_fixture_int8(i * 8) for i in range(0, 8)],
                [-1, -16, -64, -91, -110, 54, 71, -56],
            ),
            (
                [channel_fixture_int16(i * 16) for i in range(0, 4)],
                [-16, -16219, -28106, 18376],
            ),
            (
                [channel_fixture_uint8(i * 8) for i in range(0, 8)],
                [255, 240, 192, 165, 146, 54, 71, 200],
            ),
            (
                [channel_fixture_uint16(i * 16, byte_swap=True) for i in range(0, 4)],
                [0xF0FF, 0xA5C0, 0x3692, 0xC847],
            ),
            (
                [channel_fixture_bool(i * 16, array_size=16) for i in range(0, 2)],
                [
                    [True] * 8 + [False] * 4 + [True] * 4,
                    [False] * 6 + [True] * 2 + [True, False] * 2 + [False, True] * 2,
                ],
            ),
            (
                [
                    channel_fixture_int8(0),
                    channel_fixture_int8(8),
                    channel_fixture_uint16(16, byte_swap=True),
                ]
                + [channel_fixture_bool(32 + i) for i in range(0, 4)]
                + [channel_fixture_uint8(40)],
                [-1, -16, 0xA5C0, False, True, False, False, 54],
            ),
            (
                [
                    channel_fixture_uint8(0, array_size=5, byte_swap=True),
                    channel_fixture_int8(40, array_size=3, byte_swap=False),
                ],
                [[255, 240, 192, 165, 146], [54, 71, -56]],
            ),
        ],
    )
    def test_read_output_channels(self, module_fixture, input_value, expected_output):
        """test read_output_channels interpretation"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.VTUX.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = input_value

        module.base = Mock()
        module.base.read_reg_data = Mock(
            return_value=b"\xff\xf0\xc0\xa5\x92\x36\x47\xc8"
        )

        # Act
        result = module.read_output_channels()

        # Assert
        assert result == expected_output

    @pytest.mark.parametrize(
        "channel_description, output",
        [
            (
                [channel_fixture_bool(i) for i in range(0, 64)],
                [True] * 8
                + [False] * 4
                + [True] * 4
                + [False] * 6
                + [True] * 2
                + [True, False] * 2
                + [False, True] * 2
                + [False, True, False, False]
                + [True, False, False, True]
                + [False, True, True, False]
                + [True, True, False, False]
                + [True] * 3
                + [False] * 3
                + [True, False]
                + [False] * 3
                + [True]
                + [False] * 2
                + [True] * 2,
            ),
            (
                [channel_fixture_int8(i * 8) for i in range(0, 8)],
                [-1, -16, -64, -91, -110, 54, 71, -56],
            ),
            (
                [channel_fixture_int16(i * 16) for i in range(0, 4)],
                [-16, -16219, -28106, 18376],
            ),
            (
                [channel_fixture_uint8(i * 8) for i in range(0, 8)],
                [255, 240, 192, 165, 146, 54, 71, 200],
            ),
            (
                [channel_fixture_uint16(i * 16, byte_swap=True) for i in range(0, 4)],
                [0xF0FF, 0xA5C0, 0x3692, 0xC847],
            ),
            (
                [channel_fixture_bool(i * 16, array_size=16) for i in range(0, 2)]
                + [channel_fixture_bool(32 + i) for i in range(0, 32)],
                [
                    [True] * 8 + [False] * 4 + [True] * 4,
                    [False] * 6 + [True] * 2 + [True, False] * 2 + [False, True] * 2,
                    False,
                    True,
                    False,
                    False,
                    True,
                    False,
                    False,
                    True,
                    False,
                    True,
                    True,
                    False,
                    True,
                    True,
                    False,
                    False,
                    True,
                    True,
                    True,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    False,
                    False,
                    True,
                    False,
                    False,
                    True,
                    True,
                ],
            ),
            (
                [
                    channel_fixture_int8(0),
                    channel_fixture_int8(8),
                    channel_fixture_uint16(16, byte_swap=True),
                ]
                + [channel_fixture_bool(32 + i) for i in range(8)]
                + [channel_fixture_uint8(40 + 8 * i) for i in range(3)],
                [
                    -1,
                    -16,
                    42432,
                    False,
                    True,
                    False,
                    False,
                    True,
                    False,
                    False,
                    True,
                    54,
                    71,
                    200,
                ],
            ),
            (
                [
                    channel_fixture_uint8(0, array_size=5, byte_swap=True),
                    channel_fixture_int8(40, array_size=3, byte_swap=False),
                ],
                [[255, 240, 192, 165, 146], [54, 71, -56]],
            ),
        ],
    )
    def test_write_output_channels(self, module_fixture, channel_description, output):
        """test read_output_channels interpretation"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.VTUX.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = channel_description
        if module.channels.outputs and len(module.channels.outputs) > 0:
            biggest_byte_offset_channel = max(
                module.channels.outputs, key=lambda x: x.bit_offset
            )
            module.output_byte_size = div_ceil(
                biggest_byte_offset_channel.bit_offset
                + biggest_byte_offset_channel.bits,
                8,
            )
        module.base = Mock()

        # Act
        module.write_channels(output)
        module.base.write_reg_data.assert_called_with(
            bytearray(b"\xff\xf0\xc0\xa5\x92\x36\x47\xc8"), None
        )
