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
            ("read_channels", True),
            ("not_known", False),
        ],
    )
    def test_is_function_supported_mapping(
        self, module_fixture, input_value, expected_output
    ):
        """Test is_function_supported"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.inputs = ["x"] * 4

        # Act & Assert
        assert module.is_function_supported(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ("read_channels", True),
            ("write_channels", False),
        ],
    )
    def test_is_function_supported_category(
        self, module_fixture, input_value, expected_output
    ):
        """Test is_function_supported"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.inputs = ["x"] * 4

        # Act & Assert
        assert module.is_function_supported(input_value) == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (["x"], True),
            (["x"] * 4, True),
            ([], False),
        ],
    )
    def test_is_function_supported_outputs(
        self, module_fixture, input_value, expected_output
    ):
        """Test is_function_supported"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.outputs = input_value

        # Act & Assert
        assert module.is_function_supported("write_channels") == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ((["x"], ["x"]), True),
            ((["x"], []), True),
            (([], ["x"]), True),
            (([], []), False),
        ],
    )
    def test_is_function_supported_inoutputs(
        self, module_fixture, input_value, expected_output
    ):
        """Test is_function_supported"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.inputs, module.channels.outputs = input_value

        assert module.is_function_supported("read_channels") == expected_output

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            ({"x": 0}, True),
            ({}, False),
        ],
    )
    def test_is_function_supported_parameters(
        self, module_fixture, input_value, expected_output
    ):
        """Test is_function_supported"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(parameters=input_value)

        # Act & Assert
        assert module.is_function_supported("read_module_parameter") == expected_output

    def test_constructor_correct_type(self, module_fixture):
        """Test constructor"""
        # Arrange
        # Act
        # Assert
        assert isinstance(module_fixture, ApModule)
        assert module_fixture.base is None
        assert module_fixture.position is None
        assert module_fixture.information is None
        assert module_fixture.system_entry_registers.outputs is None
        assert module_fixture.system_entry_registers.inputs is None

    def test_configure(self, module_fixture):
        """Test configure"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INFRASTRUCTURE.value
        module.information = Mock(input_size=3, output_size=5)
        module.is_function_supported = Mock(return_value=True)
        mocked_base = Mock(
            next_output_register=0,
            next_input_register=0,
            next_diagnosis_register=0,
            modules=[],
        )

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        module._configure(mocked_base, MODULE_POSITION)

        # Assert
        assert module.position == MODULE_POSITION

    def test_configure_iolink(self, module_fixture):
        """Test configure"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = Mock(input_size=3, output_size=5)
        module.is_function_supported = Mock(return_value=True)
        mocked_base = Mock(
            next_output_register=0,
            next_input_register=0,
            next_diagnosis_register=0,
            modules=[],
        )

        module.read_fieldbus_parameters = Mock()

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        module._configure(mocked_base, MODULE_POSITION)

        # Assert
        assert module.position == MODULE_POSITION
        module.read_fieldbus_parameters.assert_called_once_with()

    def test_repr_correct_string(self, module_fixture):
        """Test repr"""
        # Arrange
        module = module_fixture
        module.name = "code"
        module.position = 1

        # Act
        module_repr = repr(module)

        # Assert
        assert module_repr == "code (idx: 1, type: Module Type)"

    @pytest.mark.parametrize("input_value", [4, 8, 16])
    def test_read_channels_correct_values_bool(self, module_fixture, input_value):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(input_size=8, output_size=0)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * input_value

        expected_value = [
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
        ]

        ret_data = b"\xfa\xfa"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value[:input_value]

    @pytest.mark.parametrize("input_value", [4, 8, 16])
    def test_read_channels_outputs(self, module_fixture, input_value):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(input_size=0, output_size=8)

        module.channels.outputs = [
            Channel(
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
        ] * input_value

        expected_value = [
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
        ]

        ret_data = b"\xfa\xfa"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value[:input_value]

    def test_read_channels_correct_values_int8(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=2, output_size=2)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=8,
                byte_swap_needed=None,
                channel_id=1,
                data_type="INT8",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=8,
                byte_swap_needed=None,
                channel_id=2,
                data_type="INT8",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2

        expected_value = [
            -128,
            127,
            -128,
            127,
        ]
        # it will call read_reg_data twice. Once for input_channels and for output_channels
        # Both times will return 0x8074 for 2 channels each

        ret_data = b"\x80\x7f"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

    def test_read_channels_correct_values_uint8(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=2, output_size=2)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=8,
                byte_swap_needed=None,
                channel_id=1,
                data_type="UINT8",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=8,
                byte_swap_needed=None,
                channel_id=2,
                data_type="UINT8",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2

        expected_value = [
            0xCA,
            0xFE,
            0xCA,
            0xFE,
        ]
        # it will call read_reg_data twice. Once for input_channels and for output_channels
        # Both times will return 0xCAFE for 2 channels each
        ret_data = b"\xca\xfe"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

    def test_read_channels_correct_values_int16(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=8, output_size=8)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=16,
                byte_swap_needed=True,
                channel_id=0,
                data_type="INT16",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=16,
                byte_swap_needed=True,
                channel_id=0,
                data_type="INT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2

        expected_value = [
            -17494,
            4352,
            -17494,
            4352,
        ]

        ret_data = b"\xaa\xbb\x00\x11"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

    def test_read_channels_correct_values_uint16(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=8, output_size=8)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=16,
                byte_swap_needed=True,
                channel_id=0,
                data_type="UINT16",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=16,
                byte_swap_needed=True,
                channel_id=0,
                data_type="UINT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=[1],
                profile_list=[3],
            )
        ] * 2

        expected_value = [
            0xBBAA,
            0x1100,
            0xBBAA,
            0x1100,
        ]

        ret_data = b"\xaa\xbb\x00\x11"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

    def test_read_channels_correct_values_io_link(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(input_size=36, output_size=32)
        module.fieldbus_parameters = [{"Input data length": 2}] * 4

        module.channels.inouts = [
            Channel(
                array_size=2,
                bits=16,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4

        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts

        ret_data = b"\xab\xcd" * ((36 + 32) // 2)  # in+out in registers

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act

        channel_values = module.read_channels()

        # Assert
        assert channel_values == [b"\xab\xcd"] * 4

    def test_read_channels_io_link_different_device_lengths(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(input_size=36, output_size=32)
        module.fieldbus_parameters = [
            {"Input data length": 0},
            {"Input data length": 2},
            {"Input data length": 3},
            {"Input data length": 4},
        ]

        module.channels.inouts = [
            Channel(
                array_size=4,
                bits=32,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4

        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts

        ret_data = b"\xab\xcd" * ((36 + 32) // 2)  # in+out in registers

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act

        channel_values = module.read_channels()

        # Assert
        assert channel_values == [
            None,
            b"\xab\xcd",
            b"\xab\xcd\xab",
            b"\xab\xcd\xab\xcd",
        ]

    def test_read_channels_unknown_type(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(input_size=8)

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UNKNOWN",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        ret_data = b"\xfa\xfa"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act & Assert
        with pytest.raises(TypeError):
            module.read_channels()

    @pytest.mark.parametrize("input_value", [4, 8])
    def test_read_channel_correct_value(self, module_fixture, input_value):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()

        module.channels.inputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * input_value

        module.read_channel = Mock()

        # Act
        for idx in range(input_value):
            module.read_channel(idx)

        # Assert
        expected_calls = [call(i) for i in range(input_value)]
        module.read_channel.assert_has_calls(expected_calls)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                [
                    Channel(
                        array_size=None,
                        bits=1,
                        byte_swap_needed=None,
                        channel_id=0,
                        data_type="BOOL",
                        description="",
                        direction="in",
                        name="Input %d",
                        parameter_group_ids=None,
                        profile_list=[3],
                    )
                ]
                * 4,
                [
                    False,
                    True,
                    False,
                    True,
                ],
            ),
            (
                [
                    Channel(
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
                ]
                * 8,
                [
                    False,
                    True,
                    False,
                    True,
                    True,
                    True,
                    True,
                    True,
                ],
            ),
        ],
    )
    def test_read_output_channel_correct_value(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()

        module.channels.inputs = [0, 1, 2, 4]  # dummy input channels
        module.channels.outputs = input_value

        module.read_output_channels = Mock(return_value=expected_value)

        # Act
        channel_values = [
            module.read_output_channel(idx) for idx in range(len(input_value))
        ]

        # Assert
        assert channel_values == expected_value

    def test_read_channel_correct_value_iolink(self, module_fixture):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=8,
                byte_swap_needed=None,
                channel_id=0,
                data_type="",
                description="",
                direction="out",
                name="",
                parameter_group_ids=None,
                profile_list=[],
            )
        ] * 4

        module.base = Mock()
        module.fieldbus_parameters = [{"Input data length": 4}] * 4

        ret_data = [b"\xab\xcd\xef\x00\x11\x22\x33\x44"] * 4

        module.read_channels = Mock(return_value=ret_data)

        # Act
        channel_values = [module.read_channel(idx) for idx in range(4)]

        # Assert
        assert all(c == b"\xab\xcd\xef\x00\x11\x22\x33\x44" for c in channel_values)

    def test_read_channels_not_implemented(self, module_fixture):
        """Test read_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.information = CpxAp.ApInformation(order_text="test module")
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.read_channels()

    @pytest.mark.parametrize(
        "input_value",
        [
            0,
            1,
            2,
            3,
        ],
    )
    def test_read_channel_not_implemented(self, module_fixture, input_value):
        """Test read_channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.information = CpxAp.ApInformation(order_text="test module")
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.read_channel(input_value)

    def test_write_channels_bool(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=8)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()
        module.base.write_reg_data = Mock()

        module.channels.outputs = [
            Channel(
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
        ] * 8

        # Act
        module.write_channels([True] * 8)

        # Assert
        module.base.write_reg_data.assert_called_with(b"\xff", 0)

    def test_write_channels_int8(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers.outputs = 0
        module.base = Mock()
        module.write_channel = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT8",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act
        module.write_channels([1, -2])

        # Assert
        module.base.write_reg_data.assert_called_with(bytearray(b"\x01\xfe"), 0)

    def test_write_channels_uint8(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers.outputs = 0
        module.base = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act
        module.write_channels([1, 2])

        # Assert
        module.base.write_reg_data.assert_called_with(bytearray(b"\x01\x02"), 0)

    def test_write_channels_uint8_negative_value(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act and assert
        with pytest.raises(ValueError):
            module.write_channels([-1, 2])

        # Act with mixed valid and invalid values
        with pytest.raises(ValueError):
            module.write_channels([300, -2])

    def test_write_channels_int16(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act
        module.write_channels([1, -2])

        # Assert
        module.base.write_reg_data.assert_called_with(bytearray(b"\x01\x00\xfe\xff"), 0)

    def test_write_channels_uint16(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act
        module.write_channels([1, 2])

        # Assert
        module.base.write_reg_data.assert_called_with(b"\x01\x00\x02\x00", 0)

    def test_write_channels_uint16_negative_value(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=2)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()
        module.write_channel = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 2

        # Act and assert
        with pytest.raises(OverflowError):
            module.write_channels([-1, 2])

    @pytest.mark.parametrize(
        "input_value",
        ["INT", "UNKNOWN"],
    )
    def test_write_channels_wrong_type(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=8)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type=input_value,
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 8

        # Act & Assert
        with pytest.raises(TypeError):
            module.write_channels([True] * 8)

    @pytest.mark.parametrize(
        "input_value",
        [7, 9],
    )
    def test_write_channels_wrong_length(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(output_size=8)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.base = Mock()

        module.channels.outputs = [
            Channel(
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
        ] * 8

        # Act & Assert
        with pytest.raises(ValueError):
            module.write_channels([True] * input_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            0,
            1,
            2,
            3,
        ],
    )
    def test_write_channels_not_implemented(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.information = CpxAp.ApInformation(order_text="test module")
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.write_channels([0] * input_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            0,
            1,
            2,
            3,
            5,
        ],
    )
    def test_write_channels_lengtherror_io_link(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(order_text="test module")
        module.channels.inouts = [
            Channel(
                array_size=2,
                bits=8,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4
        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts
        # Act & Assert
        with pytest.raises(ValueError):
            module.write_channels([b"\x00\x00"] * input_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            b"\x00",
            b"\x00\x00",
            b"\x00\x00\x00",
            b"\x00\x00\x00\x00\x00",
        ],
    )
    def test_write_channels_bytelength_error_io_link(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(order_text="test module")
        module.channels.inouts = [
            Channel(
                array_size=4,
                bits=16,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4
        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts
        # Act & Assert
        with pytest.raises(ValueError):
            module.write_channels([input_value] * 4)

    @pytest.mark.parametrize(
        "input_value",
        [
            1,
            "1",
            True,
        ],
    )
    def test_write_channels_typeerror_io_link(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(order_text="test module")
        module.channels.outputs = [1, 2, 3, 4]
        module.channels.inputs = [1, 2, 3, 4]
        module.channels.inouts = [1, 2, 3, 4]
        # Act & Assert
        with pytest.raises(TypeError):
            module.write_channels([input_value] * 4)

    def test_write_channels_io_link(self, module_fixture):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock(write_reg_data=Mock())
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(order_text="test module")
        module.channels.inouts = [
            Channel(
                array_size=8,
                bits=32,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4
        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts
        # Act
        module.write_channels([b"\x00\x01\x02\x03\x04\x05\x06\x07"] * 4)

        # Assert
        module.base.write_reg_data.assert_called_with(
            b"\x00\x01\x02\x03\x04\x05\x06\x07\x00\x01\x02\x03\x04\x05\x06\x07"
            b"\x00\x01\x02\x03\x04\x05\x06\x07\x00\x01\x02\x03\x04\x05\x06\x07",
            0,
        )

    def test_write_channel_bool(self, module_fixture):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_output_channels = Mock(return_value=[False] * 4)

        module.channels.outputs = [
            Channel(
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
        ] * 4

        # Act
        module.write_channel(1, True)

        # Assert
        module.base.write_reg_data.assert_called_with(b"\x02", 0)

    def test_write_channel_int16(self, module_fixture):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_channels = Mock(return_value=[False] * 4)

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.write_channel(1, -1)

        # Assert
        module.base.write_reg_data.assert_called_with(b"\xff\xff", 1)

    def test_write_channel_uint16(self, module_fixture):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_channels = Mock(return_value=[False] * 4)

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT16",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.write_channel(1, 1)

        # Assert
        module.base.write_reg_data.assert_called_with(b"\x01\x00", 1)

    @pytest.mark.parametrize("input_value", ["INT", "UNKNOWN"])
    def test_write_channel_unknown_type(self, module_fixture, input_value):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_channels = Mock(return_value=[False] * 4)

        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type=input_value,
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act & Assert
        with pytest.raises(TypeError):
            module.write_channel(1, True)

    @pytest.mark.parametrize(
        "input_value",
        [
            0,
            1,
            2,
            3,
        ],
    )
    def test_write_channel_not_implemented(self, module_fixture, input_value):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.information = CpxAp.ApInformation(order_text="test module")
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.write_channel(input_value, input_value)

    @pytest.mark.parametrize(
        "input_value",
        [
            0,
            1,
            2,
            3,
        ],
    )
    def test_write_channel_iolink_2bytes(self, module_fixture, input_value):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.information = CpxAp.ApInformation(input_size=34, output_size=32)
        module.base = Mock()
        module.base.write_reg_data = Mock()

        module.channels.inouts = [
            Channel(
                array_size=2,
                bits=16,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4

        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts

        data = b"\xab\xcd"

        # Act
        module.write_channel(input_value, data)

        # Assert
        module.base.write_reg_data.assert_called_with(
            data, module.system_entry_registers.outputs + input_value
        )

    @pytest.mark.parametrize(
        "input_value, expected_register",
        [
            (0, 0),
            (1, 2),
            (2, 4),
            (3, 6),
        ],
    )
    def test_write_channel_iolink_4bytes(
        self, module_fixture, input_value, expected_register
    ):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.system_entry_registers = SystemEntryRegisters(outputs=0)
        module.information = CpxAp.ApInformation(input_size=34, output_size=32)
        module.base = Mock()
        module.base.write_reg_data = Mock()

        module.channels.inouts = [
            Channel(
                array_size=4,
                bits=32,
                byte_swap_needed=None,
                channel_id=0,
                data_type="UINT8",
                description="",
                direction="in",
                name="Port %d",
                parameter_group_ids=[1, 2],
                profile_list=[50],
            )
        ] * 4

        module.channels.inputs = module.channels.inouts
        module.channels.outputs = module.channels.inouts

        data = b"\x01\x02\xab\xcd"

        # Act
        module.write_channel(input_value, data)

        # Assert
        module.base.write_reg_data.assert_called_with(
            b"\x01\x02\xab\xcd", expected_register
        )

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_get_item_correct_values(self, module_fixture, input_value):
        """Test get item"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.channels.inputs = []
        module.read_channel = Mock()

        # Act
        _ = module[input_value]

        # Assert
        module.read_channel.assert_called_with(input_value)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_set_item_correct_values(self, module_fixture, input_value):
        """Test set item"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.channels.inputs = []
        module.write_channel = Mock()

        # Act
        module[input_value] = input_value

        # Assert
        module.write_channel.assert_called_with(input_value, input_value)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_set_channel_correct_values(self, module_fixture, input_value):
        """Test set channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.write_channel = Mock()
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.set_channel(input_value)

        # Assert
        module.write_channel.assert_called_with(input_value, True)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_reset_channel_correct_values(self, module_fixture, input_value):
        """Test reset channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.write_channel = Mock()
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.reset_channel(input_value)

        # Assert
        module.write_channel.assert_called_with(input_value, False)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_toggle_true_channel_correct_values(self, module_fixture, input_value):
        """Test toggle channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.write_channel = Mock()
        module.read_output_channel = Mock(return_value=True)
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.toggle_channel(input_value)

        # Assert
        module.write_channel.assert_called_with(input_value, False)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_toggle_false_channel_correct_values(self, module_fixture, input_value):
        """Test toggle channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.write_channel = Mock()
        module.read_output_channel = Mock(return_value=False)
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act
        module.toggle_channel(input_value)

        # Assert
        module.write_channel.assert_called_with(input_value, True)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_set_channel_wrong_output_type(self, module_fixture, input_value):
        """Test set channel"""
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act & Assert
        with pytest.raises(TypeError):
            module.set_channel(input_value)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_clear_channel_wrong_output_type(self, module_fixture, input_value):
        """Test set channel"""
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act & Assert
        with pytest.raises(TypeError):
            module.reset_channel(input_value)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_toggle_channel_wrong_output_type(self, module_fixture, input_value):
        """Test set channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = Mock(output_size=4)
        module.channels.outputs = [
            Channel(
                array_size=None,
                bits=1,
                byte_swap_needed=None,
                channel_id=0,
                data_type="INT",
                description="",
                direction="in",
                name="Input %d",
                parameter_group_ids=None,
                profile_list=[3],
            )
        ] * 4

        # Act & Assert
        with pytest.raises(TypeError):
            module.toggle_channel(input_value)

    def test_write_module_parameter_int(self, module_fixture):
        """Test write_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.write_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act
        parameter_index_to_write = 0
        value_to_write = 1
        module.write_module_parameter(parameter_index_to_write, value_to_write)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.write_parameter.assert_called_with(
            module.position, parameter, value_to_write, 0
        )

    def test_write_module_parameter_not_available(self, module_fixture):
        """Test write_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.write_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act & Assert
        parameter_index_to_write = 1
        value_to_write = 1
        with pytest.raises(NotImplementedError):
            module.write_module_parameter(parameter_index_to_write, value_to_write)

    def test_write_module_parameter_not_writable(self, module_fixture):
        """Test write_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.write_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, False, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act & Assert
        parameter_index_to_write = 0
        value_to_write = 1
        with pytest.raises(AttributeError):
            module.write_module_parameter(parameter_index_to_write, value_to_write)

    def test_write_module_parameter_str(self, module_fixture):
        """Test write_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.write_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act
        parameter_str_to_write = "test"
        value_to_write = 1
        module.write_module_parameter(parameter_str_to_write, value_to_write)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.write_parameter.assert_called_with(
            module.position, parameter, value_to_write, 0
        )

    def test_write_module_parameter_instances(self, module_fixture):
        """Test write_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.write_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )
        module._check_instances = Mock(return_value=[0, 1, 2, 3])

        # Act
        parameter_index_to_write = 0
        value_to_write = 1
        module.write_module_parameter(parameter_index_to_write, value_to_write)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.write_parameter.assert_has_calls(
            [
                call(module.position, parameter, value_to_write, 0),
                call(module.position, parameter, value_to_write, 1),
                call(module.position, parameter, value_to_write, 2),
                call(module.position, parameter, value_to_write, 3),
            ]
        )

    def test_read_module_parameter_int(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act
        parameter_index_to_read = 0
        module.read_module_parameter(parameter_index_to_read)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.read_parameter.assert_called_with(module.position, parameter, 0)

    def test_read_module_parameter_not_available(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act & Assert
        parameter_index_to_read = 1
        with pytest.raises(NotImplementedError):
            module.read_module_parameter(parameter_index_to_read)

    def test_read_module_parameter_str(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )

        # Act
        parameter_str_to_read = "test"
        module.read_module_parameter(parameter_str_to_read)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.read_parameter.assert_called_with(module.position, parameter, 0)

    def test_read_module_parameter_instances(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
            }
        )
        module._check_instances = Mock(return_value=[0, 1, 2, 3])

        # Act
        parameter_index_to_read = 0
        module.read_module_parameter(parameter_index_to_read)

        # Assert
        parameter = module.module_dicts.parameters.get(0)

        module.base.read_parameter.assert_has_calls(
            [
                call(module.position, parameter, 0),
                call(module.position, parameter, 1),
                call(module.position, parameter, 2),
                call(module.position, parameter, 3),
            ]
        )

    def test_read_diagnosis_code(self, module_fixture):
        """Test read_diagnosis_code"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INTERFACE.value
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xca\xfe\xba\xbe")
        module.system_entry_registers.diagnosis = 1
        ModuleDicts = namedtuple("ModuleDicts", ["diagnosis"])
        module.module_dicts = ModuleDicts(diagnosis={"x": 0, "y": 1})

        # Act
        result = module.read_diagnosis_code()

        # Assert
        module.base.read_reg_data.assert_called_with(5, length=2)
        assert result == 0xBEBAFECA

    def test_read_diagnosis_code_not_supported(self, module_fixture):
        """Test read_diagnosis_code"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INTERFACE.value
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xca\xfe\xba\xbe")
        module.system_entry_registers.diagnosis = 1

        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.read_diagnosis_code()

    def test_read_diagnosis_information(self, module_fixture):
        """Test read_diagnosis_information"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INTERFACE.value
        module.base = Mock()
        module.read_diagnosis_code = Mock(return_value=0)
        ModuleDicts = namedtuple("ModuleDicts", ["diagnosis"])
        module.module_dicts = ModuleDicts(diagnosis={0: "test0", 1: "test1"})

        # Act
        result = module.read_diagnosis_information()

        # Assert
        module.read_diagnosis_code.assert_called_with()
        assert result == "test0"

    def test_read_diagnosis_information_not_supported(self, module_fixture):
        """Test read_diagnosis_information"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INTERFACE.value
        module.base = Mock()

        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.read_diagnosis_information()

    @patch(
        "cpx_io.cpx_system.cpx_ap.ap_module.convert_uint32_to_octett",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.ap_module.convert_to_mac_string",
        spec=True,
    )
    def test_read_system_parameters(
        self,
        mock_convert_to_mac_string,
        mock_convert_uint32_to_octett,
        module_fixture,
    ):
        """Test read_system_parameters"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INTERFACE.value
        module.base = Mock()
        module.base.read_parameter = Mock(return_value=1)
        mock_convert_uint32_to_octett.return_value = "1.1.1.1"
        mock_convert_to_mac_string.return_value = "1:1:1:1:1:1"

        # Act
        result = module.read_system_parameters()

        # Assert
        assert result == SystemParameters(
            dhcp_enable=True,
            ip_address="1.1.1.1",
            subnet_mask="1.1.1.1",
            gateway_address="1.1.1.1",
            active_ip_address="1.1.1.1",
            active_subnet_mask="1.1.1.1",
            active_gateway_address="1.1.1.1",
            mac_address="1:1:1:1:1:1",
            setup_monitoring_load_supply=1,
        )

    def test_read_pqi_channel_no_index(self, module_fixture):
        """Test read_pqi"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.system_entry_registers.inputs = 0
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xca\xfe")

        # Act
        result = module.read_pqi()

        # Assert
        assert result == [
            {
                "Port Qualifier": "input data is valid",
                "Device Error": "there is at least one error or warning on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is invalid",
                "Device Error": "there are no errors or warnings on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is valid",
                "Device Error": "there is at least one error or warning on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is invalid",
                "Device Error": "there are no errors or warnings on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
        ]

    def test_read_pqi_channel_indexes(self, module_fixture):
        """Test read_pqi"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.system_entry_registers.inputs = 0
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xca\xfe")

        # Act
        results = [module.read_pqi(idx) for idx in range(4)]

        # Assert
        assert results == [
            {
                "Port Qualifier": "input data is valid",
                "Device Error": "there is at least one error or warning on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is invalid",
                "Device Error": "there are no errors or warnings on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is valid",
                "Device Error": "there is at least one error or warning on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
            {
                "Port Qualifier": "input data is invalid",
                "Device Error": "there are no errors or warnings on the device or port",
                "DevCOM": "device is not connected or not yet in operation",
            },
        ]

    def test_read_fieldbus_parameters(self, module_fixture):
        """Test read_fieldbus_parameters"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.system_entry_registers.inputs = 0
        module.base = Mock()
        module.base.read_parameter = Mock(return_value=True)
        ModuleDicts = namedtuple("ModuleDicts", ["parameters"])
        module.module_dicts = ModuleDicts(
            parameters={
                20074: 20074,
                20075: 20075,
                20076: 20076,
                20077: 20077,
                20078: 20078,
                20079: 20079,
                20108: 20108,
                20109: 20109,
            }
        )

        # Act
        result = module.read_fieldbus_parameters()

        # Assert
        assert result == [
            {
                "Port status information": "DEACTIVATED",
                "Revision ID": True,
                "Transmission rate": "COM1",
                "Actual cycle time [in 100 us]": True,
                "Actual vendor ID": True,
                "Actual device ID": True,
                "Input data length": True,
                "Output data length": True,
            },
            {
                "Port status information": "DEACTIVATED",
                "Revision ID": True,
                "Transmission rate": "COM1",
                "Actual cycle time [in 100 us]": True,
                "Actual vendor ID": True,
                "Actual device ID": True,
                "Input data length": True,
                "Output data length": True,
            },
            {
                "Port status information": "DEACTIVATED",
                "Revision ID": True,
                "Transmission rate": "COM1",
                "Actual cycle time [in 100 us]": True,
                "Actual vendor ID": True,
                "Actual device ID": True,
                "Input data length": True,
                "Output data length": True,
            },
            {
                "Port status information": "DEACTIVATED",
                "Revision ID": True,
                "Transmission rate": "COM1",
                "Actual cycle time [in 100 us]": True,
                "Actual vendor ID": True,
                "Actual device ID": True,
                "Input data length": True,
                "Output data length": True,
            },
        ]

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_read_isdu_different_channels(self, module_fixture, input_value):
        """Test read_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        channel = input_value
        index = 4
        subindex = 5

        result = module.read_isdu(channel, index, subindex)

        # Assert
        module.base.write_reg_data.assert_has_calls(
            [
                call(b"\x01\x00", 34002),  # MODULE_NO (position add 1)
                call((channel + 1).to_bytes(2, "little"), 34003),  # CHANNEL (add 1)
                call(b"\x04\x00", 34004),  # INDEX
                call(b"\x05\x00", 34005),  # SUBINDEX
                call(b"\x00\x00", 34006),  # LENGTH zero when reading
                call(b"\x64\x00", 34001),  # COMMAND (read 100)
            ]
        )
        module.base.read_reg_data.assert_has_calls(
            [
                call(34000, 1),
                call(34006),
                call(34007, 0),
            ]
        )

        assert (
            result == b""
        )  # will cut to the actual_length which is returned with 0 in this test

    def test_read_isdu_no_response(self, module_fixture):
        """Test read_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
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
    def test_write_isdu_different_channels(self, module_fixture, input_value):
        """Test write_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = b"\xca\xfe"
        channel = input_value
        index = 4  # random
        subindex = 5  # random

        module.write_isdu(data, channel, index, subindex)

        # Assert
        module.base.write_reg_data.assert_has_calls(
            [
                call(b"\x01\x00", 34002),  # MODULE_NO (position add 1)
                call((channel + 1).to_bytes(2, "little"), 34003),  # CHANNEL (add 1)
                call(b"\x04\x00", 34004),  # INDEX
                call(b"\x05\x00", 34005),  # SUBINDEX
                call(b"\x02\x00", 34006),  # LENGTH (bytes)
                call(data, 34007),  # DATA
                call(b"\x65\x00", 34001),  # COMMAND (read 101)
            ]
        )
        module.base.read_reg_data.assert_has_calls([call(34000, 1)])

    @pytest.mark.parametrize(
        "input_value",
        [
            b"\x01",
            b"\x01\x02",
            b"\x01\x02\x03",
            b"\x01\x02\x03\x04",
        ],
    )
    def test_write_isdu_different_lengths(self, module_fixture, input_value):
        """Test write_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = input_value
        channel = 0  # random
        index = 4  # random
        subindex = 5  # random

        module.write_isdu(data, channel, index, subindex)
        length = len(data)

        # Assert
        module.base.write_reg_data.assert_has_calls(
            [
                call(b"\x01\x00", 34002),  # MODULE_NO (position add 1)
                call((channel + 1).to_bytes(2, "little"), 34003),  # CHANNEL (add 1)
                call(b"\x04\x00", 34004),  # INDEX
                call(b"\x05\x00", 34005),  # SUBINDEX
                call(length.to_bytes(2, "little"), 34006),  # LENGTH
                call(data, 34007),  # DATA
                call(b"\x65\x00", 34001),  # COMMAND (read 101)
            ]
        )
        module.base.read_reg_data.assert_has_calls([call(34000, 1)])

    def test_write_isdu_no_response(self, module_fixture):
        """Test write_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x01\x00")

        # Act & Assert
        data = b"\xca\xfe"
        channel = 0
        index = 4
        subindex = 5

        with pytest.raises(CpxRequestError):
            module.write_isdu(data, channel, index, subindex)

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [("str", ""), ("int", 0), ("raw", b""), ("bool", False)],
    )
    def test_read_isdu_different_datatypes(
        self, module_fixture, input_value, expected_output
    ):
        """Test read_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        ret = module.read_isdu(0, 0, data_type=input_value)

        # Assert
        assert ret == expected_output

    @pytest.mark.parametrize(
        "input_value,, length, expected_output",
        [
            ("str", 3, b"str"),  # string
            (1, 1, b"\x01"),  # int8
            (0xCAFE, 2, b"\xca\xfe"),  # int16
            (0xCAFEBABE, 4, b"\xca\xfe\xba\xbe"),  # int32
            (-1, 1, b"\xff\xff"),  # sint8
            (-1925, 2, b"\xf8\x7b"),  # sint16
            (-999999, 3, b"\xff\xf0\xbd\xc1"),  # 3byte sint32
            (-99999999, 4, b"\xfa\x0a\x1f\x01"),  # sint32
            (b"\xca\xfe", 2, b"\xca\xfe"),  # bytes = raw
            (True, 1, b"\x01"),  # bool true
            (False, 1, b"\x00"),  # bool false
            (0.0, 4, b"\x00\x00\x00\x00"),  # float 0
            (-1.23456, 4, b"\xbf\x9e\x06\x10"),  # negative float
        ],
    )
    def test_write_isdu_different_datatypes(
        self, module_fixture, input_value, length, expected_output
    ):
        """Test read_isdu"""
        # Remark
        # This test is has different byteorders from CPX-AP write_isdu because
        # there are no dedicated "write with byteswap" commands for CPX-E. We
        # need to send different byteorders for different types

        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        module.write_isdu(input_value, 0, 0)

        command = 101

        # Assert
        module.base.write_reg_data.assert_has_calls(
            [
                call(b"\x01\x00", 34002),  # MODULE_NO (position add 1)
                call((1).to_bytes(2, "little"), 34003),  # CHANNEL (add 1)
                call(b"\x00\x00", 34004),  # INDEX
                call(b"\x00\x00", 34005),  # SUBINDEX
                call(length.to_bytes(2, "little"), 34006),  # LENGTH
                call(expected_output, 34007),  # DATA
                call(command.to_bytes(2, "little"), 34001),  # COMMAND
            ]
        )
        module.base.read_reg_data.assert_has_calls([call(34000, 1)])
