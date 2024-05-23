"""Contains tests for ApModule class"""

import inspect
from unittest.mock import Mock, call
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
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
        module.information = CpxAp.ApInformation(input_size=8)

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

    def test_read_channels_correct_values_int16(self, module_fixture):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.ANALOG.value
        module.information = CpxAp.ApInformation(input_size=8)

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

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                [
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
                ]
                * 40,
                [b"\xAB\xCD\xEF\x00\x11\x22\x33\x44"] * 4,
            ),
        ],
    )
    def test_read_channels_correct_values_BYTES(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.apdd_information.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ApInformation(input_size=36)

        module.input_channels = input_value

        ret_data = b"\xAB\xCD\xEF\x00\x11\x22\x33\x44" * 4

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

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
                        direction="in",
                        name="Input %d",
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
    def test_read_channel_correct_value_IOLink_full_size_True(
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

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_get_item_correct_values(self, module_fixture, input_value):
        """Test get item"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.input_channels = []
        module.read_channel = Mock()

        # Act
        module[input_value]

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
