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


def channel_fixture_bool():
    return Channel(
        array_size=None,
        bits=1,
        byte_swap_needed=None,
        channel_id=0,
        data_type="BOOL",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int8():
    return Channel(
        array_size=None,
        bits=8,
        byte_swap_needed=None,
        channel_id=1,
        data_type="INT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int16():
    return Channel(
        array_size=None,
        bits=16,
        byte_swap_needed=None,
        channel_id=2,
        data_type="INT16",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int32():
    return Channel(
        array_size=None,
        bits=32,
        byte_swap_needed=None,
        channel_id=3,
        data_type="INT32",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint8():
    return Channel(
        array_size=None,
        bits=8,
        byte_swap_needed=None,
        channel_id=4,
        data_type="UINT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint16():
    return Channel(
        array_size=None,
        bits=16,
        byte_swap_needed=None,
        channel_id=5,
        data_type="UINT16",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint32():
    return Channel(
        array_size=None,
        bits=32,
        byte_swap_needed=None,
        channel_id=6,
        data_type="UINT32",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int8_array():
    return Channel(
        array_size=2,
        bits=8,
        byte_swap_needed=None,
        channel_id=7,
        data_type="INT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint8_array():
    return Channel(
        array_size=2,
        bits=8,
        byte_swap_needed=None,
        channel_id=8,
        data_type="UINT8",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_int16_array():
    return Channel(
        array_size=2,
        bits=16,
        byte_swap_needed=None,
        channel_id=9,
        data_type="INT16",
        description="",
        direction="out",
        name="Output %d",
        parameter_group_ids=None,
        profile_list=[3],
    )


def channel_fixture_uint16_array():
    return Channel(
        array_size=2,
        bits=16,
        byte_swap_needed=None,
        channel_id=10,
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
        )

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (
                ([channel_fixture_int8()] * 8, [">b"] * 8),
                [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],
            ),
            (
                ([channel_fixture_int16()] * 4, [">h"] * 4),
                [0x0102, 0x0304, 0x0506, 0x0708],
            ),
            (
                ([channel_fixture_uint8()] * 8, [">B"] * 8),
                [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],
            ),
            (
                ([channel_fixture_uint16()] * 4, [">H"] * 4),
                [0x0102, 0x0304, 0x0506, 0x0708],
            ),
        ],
    )
    def test_read_output_channels_interpretation_same_types(
        self, module_fixture, input_value, expected_output
    ):
        """test read_output_channels interpretation"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.VTUX.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = input_value[0]
        module._generate_decode_string_list = Mock(return_value=input_value[1])

        module.base = Mock()
        module.base.read_reg_data = Mock(
            return_value=b"\x01\x02\x03\x04\x05\x06\x07\x08"
        )

        # Act
        result = module.read_output_channels()

        # Assert
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (
                (
                    [
                        channel_fixture_int8(),
                        channel_fixture_uint8(),
                        channel_fixture_int16(),
                        channel_fixture_uint16(),
                        channel_fixture_int8_array(),
                    ],
                    [">b", ">B", ">h", ">H", ">bb"],
                ),
                [0x01, 0x02, 0x0304, 0x0506, (0x07, 0x08)],
            ),
            (
                (
                    [
                        channel_fixture_int8(),
                        channel_fixture_int8(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_int16(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_int8_array(),
                    ],
                    [
                        ">b",
                        ">b",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">h",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">?",
                        ">bb",
                    ],
                ),
                [
                    0x01,
                    0x02,
                    True,
                    True,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    0x0405,
                    False,
                    True,
                    True,
                    False,
                    False,
                    False,
                    False,
                    False,
                    (0x07, 0x08),
                ],
            ),
        ],
    )
    def test_read_output_channels_interpretation_mixed_types_8bytes(
        self, module_fixture, input_value, expected_output
    ):
        """test read_output_channels interpretation"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.VTUX.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = input_value[0]
        module._generate_decode_string_list = Mock(return_value=input_value[1])

        module.base = Mock()
        module.base.read_reg_data = Mock(
            return_value=b"\x01\x02\x03\x04\x05\x06\x07\x08"
        )

        # Act
        result = module.read_output_channels()

        # Assert
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (
                (
                    [
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                        channel_fixture_bool(),
                    ],
                    [
                        ">b",
                        ">b",
                        ">b",
                        ">b",
                    ],
                ),
                [True, False, False, False],
            ),
        ],
    )
    def test_read_output_channels_interpretation_mixed_types_2byte(
        self, module_fixture, input_value, expected_output
    ):
        """test read_output_channels interpretation"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.VTUX.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = input_value[0]
        module._generate_decode_string_list = Mock(return_value=input_value[1])

        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x01\x02")

        # Act
        result = module.read_output_channels()

        # Assert
        assert result == expected_output
