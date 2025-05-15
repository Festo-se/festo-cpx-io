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


class TestApModule:
    "Test ApModule"

    def channel_fixture_bool(self):
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

    def channel_fixture_int8(self):
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

    def channel_fixture_int16(self):
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

    def channel_fixture_int32(self):
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

    def channel_fixture_uint8(self):
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

    def channel_fixture_uint16(self):
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

    def channel_fixture_uint32(self):
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

    def channel_fixture_int8_array(self):
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

    def channel_fixture_uint8_array(self):
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

    def channel_fixture_int16_array(self):
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

    def channel_fixture_uint16_array(self):
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

    @pytest.mark.parametrize("input_value", [8, 16, 32])
    def test_generate_decode_string_list_only_bools(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_bool(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">?"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_int8(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_int8(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">b"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_int16(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_int16(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">h"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_int32(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_int32(),
        ] * input_value

        # Act & Assert
        with pytest.raises(TypeError):
            module._generate_decode_string_list(module.channels.outputs)

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_uint8(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_uint8(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">B"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_uint16(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_uint16(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">H"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_only_uint32(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_uint32(),
        ] * input_value

        # Act & Assert
        with pytest.raises(TypeError):
            module._generate_decode_string_list(module.channels.outputs)

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_int8_array(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_int8_array(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">bb"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_int16_array(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_int16_array(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">hh"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_uint8_array(self, module_fixture, input_value):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_uint8_array(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">BB"] * input_value

    @pytest.mark.parametrize("input_value", [1, 2, 3, 4, 5])
    def test_generate_decode_string_list_uint16_array(
        self, module_fixture, input_value
    ):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_uint16_array(),
        ] * input_value

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [">HH"] * input_value

    def test_generate_decode_string_list_mixed(self, module_fixture):
        """Test decode string list"""
        # Arrange
        module = module_fixture

        module.channels.outputs = [
            self.channel_fixture_bool(),
            self.channel_fixture_bool(),
            self.channel_fixture_int8(),
            self.channel_fixture_int16(),
            self.channel_fixture_uint8(),
            self.channel_fixture_uint16(),
            self.channel_fixture_int8_array(),
            self.channel_fixture_int16_array(),
            self.channel_fixture_uint8_array(),
            self.channel_fixture_uint16_array(),
        ]

        # Act
        result = module._generate_decode_string_list(module.channels.outputs)

        # Assert
        assert result == [
            ">?",
            ">?",
            ">b",
            ">h",
            ">B",
            ">H",
            ">bb",
            ">hh",
            ">BB",
            ">HH",
        ]
