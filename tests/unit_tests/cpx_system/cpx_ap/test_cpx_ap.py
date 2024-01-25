"""Contains tests for CpxAp class"""
from unittest.mock import patch

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol


class TestCpxAp:
    "Test CpxAp methods"

    @patch.object(CpxAp, "read_module_count")
    @patch.object(CpxAp, "read_module_information")
    # @patch.object(CpxAp, "add_module")
    def test_constructor_correct_type(
        self, mock_read_module_information, mock_read_module_count
    ):
        "Test constructor"
        # Arrange
        mock_read_module_count.return_value = 7

        module_code_list = [8323, 8199, 8197, 8202, 8201, 8198, 8198]
        module_information_list = [
            CpxAp.ModuleInformation(
                module_code=module_code, output_size=0, input_size=0
            )
            for module_code in module_code_list
        ]
        mock_read_module_information.side_effect = module_information_list

        # Act
        cpxap = CpxAp()

        # Assert
        assert isinstance(cpxap, CpxAp)
        assert len(cpxap.modules) == 7
        assert isinstance(cpxap.modules[0], CpxApEp)
        assert isinstance(cpxap.modules[1], CpxAp8Di)
        assert isinstance(cpxap.modules[2], CpxAp4Di4Do)
        assert isinstance(cpxap.modules[3], CpxAp4AiUI)
        assert isinstance(cpxap.modules[4], CpxAp4Iol)
        assert isinstance(cpxap.modules[5], CpxAp4Di)
        assert isinstance(cpxap.modules[6], CpxAp4Di)
        assert isinstance(cpxap.cpxapep, CpxApEp)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap8di, CpxAp8Di)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap4di4do, CpxAp4Di4Do)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap4aiui, CpxAp4AiUI)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap4iol, CpxAp4Iol)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap4di, CpxAp4Di)  # pylint: disable="no-member"
        assert isinstance(cpxap.cpxap4di_1, CpxAp4Di)  # pylint: disable="no-member"

    @patch.object(CpxAp, "read_module_count")
    @patch.object(CpxAp, "read_module_information")
    # @patch.object(CpxAp, "add_module")
    def test_rename_module_reflected_in_base(
        self, mock_read_module_information, mock_read_module_count
    ):
        "Test constructor"
        # Arrange
        mock_read_module_count.return_value = 7

        module_code_list = [8323, 8199, 8197, 8202, 8201, 8198, 8198]
        module_information_list = [
            CpxAp.ModuleInformation(
                module_code=module_code, output_size=0, input_size=0
            )
            for module_code in module_code_list
        ]
        mock_read_module_information.side_effect = module_information_list
        cpxap = CpxAp()

        # Act
        cpxap.cpxap8di.name = "my8di"  # pylint: disable="no-member"

        # Assert
        assert isinstance(cpxap.my8di, CpxAp8Di)  # pylint: disable="no-member"
