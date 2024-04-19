"""Contains tests for ApModule class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
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

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (
                [
                    Channel(
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

    def test_read_channel_correct_values(self, module_fixture):
        """Test read channel"""
        # Arrange
        module = module_fixture
        module.information = CpxAp.ModuleInformation(input_size=4)

        module.input_channels = [
            Channel(
                bits=1,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="in",
                name="Input %d",
                profile_list=[3],
            )
        ] * 4

        ret_data = b"\xAA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [module.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
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

        module = ApModule(
            module_information,
            input_channels,
            output_channels,
            parameters,
        )

        ret_data = b"\xAA"

        module.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [module[idx] for idx in range(4)]

        # Assert
        assert channel_values == [False, True, False, True]

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
