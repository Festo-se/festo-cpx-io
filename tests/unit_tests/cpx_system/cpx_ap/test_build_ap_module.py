"""Contains tests for ApModule build"""

from collections import namedtuple
from unittest.mock import patch
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.builder.ap_module_builder import build_ap_module
from cpx_io.cpx_system.cpx_ap.builder.apdd_information_builder import Variant
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import Channel


class TestBuildApModule:
    "Test build_ap_module"

    @patch(
        "cpx_io.cpx_system.cpx_ap.builder.ap_module_builder.build_diagnosis_list",
        spec=True,
    )
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
    @patch(
        "cpx_io.cpx_system.cpx_ap.builder.ap_module_builder.build_actual_variant",
        spec=True,
    )
    def test_build_ap_module(
        self,
        mock_build_actual_variant,
        mock_build_apdd_information,
        mock_build_channel_list,
        mock_build_parameter_list,
        mock_build_diagnosis_list,
    ):
        # Arrange
        ApddInformation = namedtuple("ApddInformation", "uid name")
        apdd_information = ApddInformation(uid="ApddModuleId", name="ApddModuleName")
        inputs = [1, 2, 3]
        outputs = [
            Channel(
                array_size=None,
                bits=1,
                bit_offset=0,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
            Channel(
                array_size=None,
                bits=1,
                bit_offset=1,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
            Channel(
                array_size=None,
                bits=1,
                bit_offset=2,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
        ]
        inouts = [
            Channel(
                array_size=None,
                bits=1,
                bit_offset=3,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
            Channel(
                array_size=None,
                bits=1,
                bit_offset=4,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
            Channel(
                array_size=None,
                bits=1,
                bit_offset=5,
                byte_swap_needed=False,
                channel_id=0,
                data_type="BOOL",
                description="",
                direction="out",
                name="Output %d",
                parameter_group_ids=None,
                profile_list=[3],
            ),
        ]
        Parameter = namedtuple("Parameter", "parameter_id name")
        parameter_list = [Parameter(i, f"Parameter{i}") for i in range(5)]
        ModuleDiagnosis = namedtuple("Diagnosis", "diagnosis_id name")
        diagnosis_list = [ModuleDiagnosis(hex(i), f"Diagnosis{i}") for i in range(1, 7)]
        actual_variant = Variant(
            channel_group_ids=[1, 2, 3],
            description="Description",
            name="Name",
            parameter_group_ids=[0],
            profile=[0],
            variant_identification={},
        )

        mock_build_actual_variant.return_value = actual_variant
        mock_build_apdd_information.return_value = apdd_information
        mock_build_channel_list.side_effect = [
            inputs,
            outputs,
            inouts,
        ]
        mock_build_parameter_list.return_value = parameter_list
        mock_build_diagnosis_list.return_value = diagnosis_list

        # Act
        ap_module = build_ap_module(None, None)

        # Assert
        assert isinstance(ap_module, ApModule)

        assert ap_module.apdd_information == apdd_information
        assert ap_module.name == apdd_information.name
        assert ap_module.channels.inputs == inputs + inouts
        assert ap_module.channels.outputs == outputs + inouts
        assert ap_module.channels.inouts == inouts
        assert len(ap_module.module_dicts.parameters) == len(parameter_list)
        assert len(ap_module.module_dicts.diagnosis) == len(diagnosis_list)
