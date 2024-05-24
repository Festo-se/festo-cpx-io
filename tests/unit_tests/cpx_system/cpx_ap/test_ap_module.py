"""Contains tests for ApModule class"""

from unittest.mock import Mock, call, patch
import pytest

from cpx_io.cpx_system.cpx_base import CpxRequestError
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import Channel


class TestApModule:
    "Test ApModule"

    @pytest.fixture(scope="function")
    def module_fixture(self):
        """module fixture"""
        apdd_information = ApModule.ApddInformation(
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

        channels = ([], [])
        parameters = []

        yield ApModule(
            apdd_information,
            channels,
            parameters,
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
        module.input_channels = ["x"] * 4

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
        module.input_channels = ["x"] * 4

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
        module.output_channels = input_value

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
        module.input_channels, module.output_channels = input_value

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
        module.parameter_dict = input_value

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
        assert module_fixture.output_register is None
        assert module_fixture.input_register is None

    def test_configure(self, module_fixture):
        """Test configure"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.INFRASTRUCTURE.value
        module.information = Mock(input_size=3, output_size=5)
        module.is_function_supported = Mock(return_value=True)
        mocked_base = Mock(next_output_register=0, next_input_register=0, modules=[])

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        module.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert module.position == MODULE_POSITION

    def test_configure_iolink(self, module_fixture):
        """Test configure"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = Mock(input_size=3, output_size=5)
        module.is_function_supported = Mock(return_value=True)
        mocked_base = Mock(next_output_register=0, next_input_register=0, modules=[])

        module.read_fieldbus_parameters = Mock()

        # Act
        MODULE_POSITION = 1  # pylint: disable=invalid-name
        module.configure(mocked_base, MODULE_POSITION)

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

        module.input_channels = [
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

        ret_data = b"\xFA\xFA"

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

        module.output_channels = [
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

        ret_data = b"\xFA\xFA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value[:input_value]

    def test_read_channels_correct_values_int16(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=8, output_size=0)

        module.input_channels = [
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
        ] * 4

        expected_value = [-17494, -8756, 4352, 13090]

        ret_data = b"\xAA\xBB\xCC\xDD\x00\x11\x22\x33"

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

        module.input_channels = [
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

        ret_data = b"\xAB\xCD\xEF\x00\x11\x22\x33\x44" * 4 + b"\x00\x00\x00\x00"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act

        channel_values = module.read_channels()

        # Assert
        assert channel_values == [b"\xAB\xCD\xEF\x00\x11\x22\x33\x44"] * 4

    def test_read_channels_unknown_type(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = CpxAp.ApInformation(input_size=8)

        module.input_channels = [
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

        ret_data = b"\xFA\xFA"

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

        module.input_channels = [
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
    def test_read_channel_correct_value_outputs_only(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()

        module.input_channels = [0, 1, 2, 4]  # dummy input channels
        module.output_channels = input_value

        module.read_channels = Mock(return_value=module.input_channels + expected_value)

        # Act
        channel_values = [
            module.read_channel(idx, outputs_only=True)
            for idx in range(len(input_value))
        ]

        # Assert
        assert channel_values == expected_value

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                True,
                [b"\xAB\xCD\xEF\x00\x11\x22\x33\x44"] * 4,
            ),
            (
                False,
                [b"\xAB\xCD\xEF\x00"] * 4,
            ),
        ],
    )
    def test_read_channel_correct_value_iolink_full_size_true(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.output_channels = ["x"] * 4  # will mock is_function_supported
        module.base = Mock()
        module.fieldbus_parameters = [{"Input data length": 4}] * 4

        ret_data = [b"\xAB\xCD\xEF\x00\x11\x22\x33\x44"] * 4

        module.read_channels = Mock(return_value=ret_data)

        # Act
        channel_values = [
            module.read_channel(idx, full_size=input_value)
            for idx in range(len(expected_value))
        ]

        # Assert
        assert all(c == e for (c, e) in zip(channel_values, expected_value))

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
        module.output_register = 0
        module.base = Mock()
        module.base.write_reg_data = Mock()

        module.output_channels = [
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
        module.base.write_reg_data.assert_called_with(b"\xFF", 0)

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
        module.output_register = 0
        module.base = Mock()

        module.output_channels = [
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
        module.output_register = 0
        module.base = Mock()

        module.output_channels = [
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
        ],
    )
    def test_write_channels_not_implemented_io_link(self, module_fixture, input_value):
        """Test write_channels"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(order_text="test module")
        module.input_channels = [1, 2, 3, 4]
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.write_channels([0] * input_value)

    def test_write_channel_bool(self, module_fixture):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.output_register = 0
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_channels = Mock(return_value=[False] * 4)

        module.output_channels = [
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

    @pytest.mark.parametrize("input_value", ["INT", "UNKNOWN"])
    def test_write_channel_unknown_type(self, module_fixture, input_value):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ApInformation(output_size=4)
        module.output_register = 0
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.read_channels = Mock(return_value=[False] * 4)

        module.output_channels = [
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
    def test_write_channel_iolink(self, module_fixture, input_value):
        """Test write_channel"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.output_channels = ["x"] * 4  # will mock is_function_supported
        module.output_register = 0
        module.information = CpxAp.ApInformation(output_size=32)
        module.base = Mock()
        module.base.write_reg_data = Mock()

        data = b"\xAB\xCD\xEF\x00"

        # Act
        module.write_channel(input_value, data)

        # Assert
        module.base.write_reg_data.assert_called_with(
            data, module.output_register + 4 * input_value
        )

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_get_item_correct_values(self, module_fixture, input_value):
        """Test get item"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.input_channels = []
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
        module.input_channels = []
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
        module.output_channels = [
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
    def test_clear_channel_correct_values(self, module_fixture, input_value):
        """Test clear channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.write_channel = Mock()
        module.output_channels = [
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
        module.clear_channel(input_value)

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
        module.read_channel = Mock(return_value=True)
        module.output_channels = [
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
        module.read_channel = Mock(return_value=False)
        module.output_channels = [
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
        module.output_channels = [
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
        module.output_channels = [
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
            module.clear_channel(input_value)

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_toggle_channel_wrong_output_type(self, module_fixture, input_value):
        """Test set channel"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.information = Mock(output_size=4)
        module.output_channels = [
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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

        # Act
        parameter_index_to_write = 0
        value_to_write = 1
        module.write_module_parameter(parameter_index_to_write, value_to_write)

        # Assert
        parameter = module.parameter_dict.get(0)

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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

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
        module.parameter_dict = {
            0: Parameter(0, {}, False, 0, "INT", 0, "test parameter", "test")
        }

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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

        # Act
        parameter_str_to_write = "test"
        value_to_write = 1
        module.write_module_parameter(parameter_str_to_write, value_to_write)

        # Assert
        parameter = module.parameter_dict.get(0)

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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }
        module._check_instances = Mock(return_value=[0, 1, 2, 3])

        # Act
        parameter_index_to_write = 0
        value_to_write = 1
        module.write_module_parameter(parameter_index_to_write, value_to_write)

        # Assert
        parameter = module.parameter_dict.get(0)

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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

        # Act
        parameter_index_to_read = 0
        module.read_module_parameter(parameter_index_to_read)

        # Assert
        parameter = module.parameter_dict.get(0)

        module.base.read_parameter.assert_called_with(module.position, parameter, 0)

    def test_read_module_parameter_not_available(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

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
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }

        # Act
        parameter_str_to_read = "test"
        module.read_module_parameter(parameter_str_to_read)

        # Assert
        parameter = module.parameter_dict.get(0)

        module.base.read_parameter.assert_called_with(module.position, parameter, 0)

    def test_read_module_parameter_instances(self, module_fixture):
        """Test read_module_parameter"""
        # Arrange
        module = module_fixture
        module.position = 9
        module.base = Mock()
        module.base.read_parameter = Mock()
        module.apdd_information.product_category = ProductCategory.DIGITAL.value
        module.parameter_dict = {
            0: Parameter(0, {}, True, 0, "INT", 0, "test parameter", "test")
        }
        module._check_instances = Mock(return_value=[0, 1, 2, 3])

        # Act
        parameter_index_to_read = 0
        module.read_module_parameter(parameter_index_to_read)

        # Assert
        parameter = module.parameter_dict.get(0)

        module.base.read_parameter.assert_has_calls(
            [
                call(module.position, parameter, 0),
                call(module.position, parameter, 1),
                call(module.position, parameter, 2),
                call(module.position, parameter, 3),
            ]
        )

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
        assert result == ApModule.SystemParameters(
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
        module.input_register = 0
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xCA\xFE")

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
        module.input_register = 0
        module.base = Mock()
        module.base.read_reg_data = Mock(return_value=b"\xCA\xFE")

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
        module.input_register = 0
        module.base = Mock()
        module.base.read_parameter = Mock(return_value=True)
        module.parameter_dict = {
            20074: 20074,
            20075: 20075,
            20076: 20076,
            20077: 20077,
            20078: 20078,
            20079: 20079,
            20108: 20108,
            20109: 20109,
        }

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
    def test_read_isdu(self, module_fixture, input_value):
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
        module.base.read_reg_data.assert_has_calls([call(34000, 1), call(34007, 119)])

        assert result == b"\x00\x00"

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
    def test_write_isdu(self, module_fixture, input_value):
        """Test write_isdu"""
        # Arrange
        module = module_fixture
        module.position = 0
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.base = Mock()
        module.base.write_reg_data = Mock()
        module.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = b"\xCA\xFE"
        channel = input_value
        index = 4
        subindex = 5

        module.write_isdu(data, channel, index, subindex)

        # Assert
        module.base.write_reg_data.assert_has_calls(
            [
                call(b"\x01\x00", 34002),  # MODULE_NO (position add 1)
                call((channel + 1).to_bytes(2, "little"), 34003),  # CHANNEL (add 1)
                call(b"\x04\x00", 34004),  # INDEX
                call(b"\x05\x00", 34005),  # SUBINDEX
                call(b"\x04\x00", 34006),  # LENGTH (bytes * 2)
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
        data = b"\xCA\xFE"
        channel = 0
        index = 4
        subindex = 5

        with pytest.raises(CpxRequestError):
            module.write_isdu(data, channel, index, subindex)
