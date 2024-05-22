"""Contains tests for ApModule build"""

from collections import namedtuple
from unittest.mock import patch
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.builder.ap_module_builder import build_ap_module


class TestBuildApModule:
    "Test build_ap_module"

    @patch(
        "cpx_io.cpx_system.cpx_ap.builder.ap_module_builder.build_parameter_list",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.builder.ap_module_builder.build_channel_list",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.builder.ap_module_builder.build_apdd_information",
        spec=True,
    )
    def test_build_ap_module(
        self,
        mock_build_apdd_information,
        mock_build_channel_list,
        mock_build_parameter_list,
    ):
        # Arrange
        ApddInformation = namedtuple("ApddInformation", "uid name")
        apdd_information = ApddInformation(uid="ApddModuleId", name="ApddModuleName")
        input_channels = [1, 2, 3]
        output_channels = [4, 5, 6]
        Parameter = namedtuple("Parameter", "parameter_id name")
        parameter_list = [Parameter(i, f"Parameter{i}") for i in range(5)]

        mock_build_apdd_information.return_value = apdd_information
        mock_build_channel_list.side_effect = [input_channels, output_channels]
        mock_build_parameter_list.return_value = parameter_list

        # Act
        ap_module = build_ap_module(None, None)

        # Assert
        assert isinstance(ap_module, ApModule)

        assert ap_module.apdd_information == apdd_information
        assert ap_module.name == apdd_information.name
        assert ap_module.input_channels == input_channels
        assert ap_module.output_channels == output_channels
        assert len(ap_module.parameter_dict) == len(parameter_list)
