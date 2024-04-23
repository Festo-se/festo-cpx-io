"""Contains tests for ApModule class"""

import inspect
from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_module_builder import Channel


class TestApModule:
    "Test ApModule"

    @pytest.fixture(scope="function")
    def module_fixture(self):
        """module fixture"""
        module_information = {
            "Description": "Description",
            "Name": "Name",
            "Module Type": "Module Type",
            "Configurator Code": "Configurator Code",
            "Part Number": "Part Number",
            "Module Class": "Module Class",
            "Module Code": "Module Code",
            "Order Text": "Order Text",
            "Product Category": "Product Category",
            "Product Family": "Product Family",
        }

        input_channels = []
        output_channels = []
        parameters = []

        yield ApModule(
            module_information,
            input_channels,
            output_channels,
            parameters,
        )

    def test_constructor_correct_type(self, module_fixture):
        """Test constructor"""
        # Arrange

        # Assert
        assert isinstance(module_fixture, ApModule)

    def test_supported_functions(self, module_fixture):
        """Test function support"""
        module = module_fixture
        coded_attributes = [
            attr for attr in dir(module) if callable(getattr(module, attr))
        ]
        # it is a coded function if it does not start with underscore and is not of type class
        coded_functions = [
            attr
            for attr in coded_attributes
            if not attr.startswith("_") and not inspect.isclass(getattr(module, attr))
        ]
        assert all(f in module.PRODUCT_CATEGORY_MAPPING.keys() for f in coded_functions)

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
                [False, True, False, True],
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
                [False, True, False, True, True, True, True, True],
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
                * 16,
                [
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
                ],
            ),
        ],
    )
    def test_read_channels_correct_values_BOOL(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ModuleInformation(input_size=8)

        module.input_channels = input_value

        ret_data = b"\xFA\xFA"

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
                ]
                * 4,
                [-17494, -8756, 4352, 13090],
            ),
        ],
    )
    def test_read_channels_correct_values_INT16(
        self, module_fixture, input_value, expected_value
    ):
        """Test read channels"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ModuleInformation(input_size=8)

        module.input_channels = input_value

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
        module.information = CpxAp.ModuleInformation(input_size=36)
        module.product_category = ProductCategory.IO_LINK.value

        module.input_channels = input_value

        ret_data = b"\xAB\xCD\xEF\x00\x11\x22\x33\x44" * 4

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = module.read_channels()

        # Assert
        assert channel_values == expected_value

    @pytest.mark.parametrize(
        "input_value",
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
            ),
        ],
    )
    def test_read_channel_correct_value(self, module_fixture, input_value):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.product_category = ProductCategory.DIGITAL.value
        module.base = Mock()

        module.input_channels = input_value
        module.read_channel = Mock()

        # Act
        for idx in range(len(input_value)):
            module.read_channel(idx)

            # Assert
            module.read_channels.assert_called_with(idx)

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
        module.product_category = ProductCategory.DIGITAL.value
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
        module.product_category = ProductCategory.IO_LINK.value
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
        module.information = CpxAp.ModuleInformation(order_text="test module")
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
        module.information = CpxAp.ModuleInformation(order_text="test module")
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
        module.information = CpxAp.ModuleInformation(order_text="test module")
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
        module.information = CpxAp.ModuleInformation(order_text="test module")
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
        module.product_category = ProductCategory.IO_LINK.value
        module.information = CpxAp.ModuleInformation(order_text="test module")
        module.input_channels = [1, 2, 3, 4]
        # Act & Assert
        with pytest.raises(NotImplementedError):
            module.write_channels([0] * input_value)

    def test_get_item_correct_values(self, module_fixture):
        """Test get item"""
        # Arrange
        module = module_fixture
        module.base = Mock()
        module.input_channels = []
        # Act
        # module

        # Assert
        # assert channel_values == [False, True, False, True]

    # @pytest.mark.parametrize(
    #     "input_value, expected_value",
    #     [
    #         (0, 0),
    #         (1, 1),
    #         (2, 2),
    #         (3, 3),
    #         (DebounceTime.T_100US, 0),
    #         (DebounceTime.T_3MS, 1),
    #         (DebounceTime.T_10MS, 2),
    #         (DebounceTime.T_20MS, 3),
    #     ],
    # )
    # def test_configure_debounce_time_successful_configuration(
    #     self, input_value, expected_value
    # ):
    #     """Test configure_debounce_time and expect success"""
    #     # Arrange
    #     MODULE_POSITION = 1  # pylint: disable=invalid-name

    #     module = ApModule(
    #         module_information,
    #         input_channels,
    #         output_channels,
    #         parameters,
    #     )
    #     module.position = MODULE_POSITION

    #     module.base = Mock(write_parameter=Mock())

    #     # Act
    #     module.configure_debounce_time(input_value)

    #     # Assert
    #     module.base.write_parameter.assert_called_with(
    #         MODULE_POSITION,
    #         ParameterNameMap()["InputDebounceTime"],
    #         expected_value,
    #     )

    # @pytest.mark.parametrize("input_value", [-1, 4])
    # def test_configure_debounce_time_raise_error(self, input_value):
    #     """Test configure_debounce_time and expect error"""
    #     # Arrange
    #     MODULE_POSITION = 1  # pylint: disable=invalid-name

    #     module = ApModule(
    #         module_information,
    #         input_channels,
    #         output_channels,
    #         parameters,
    #     )
    #     module.position = MODULE_POSITION

    #     module.base = Mock(write_parameter=Mock())

    #     # Act & Assert
    #     with pytest.raises(ValueError):
    #         module.configure_debounce_time(input_value)
