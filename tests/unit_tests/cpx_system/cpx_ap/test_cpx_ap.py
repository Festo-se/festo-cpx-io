"""Contains tests for CpxAp class"""

from unittest.mock import patch, Mock
import pytest

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap, ParameterMapItem


class TestCpxAp:
    "Test CpxAp methods"

    @patch.object(CpxAp, "read_module_count")
    @patch.object(CpxAp, "read_module_information")
    @patch.object(CpxAp, "write_reg_data")
    @patch.object(CpxAp, "read_reg_data")
    @patch.object(CpxAp, "read_parameter")
    # @patch.object(CpxAp, "add_module")
    def test_constructor_correct_type(
        self,
        mock_read_parameter,
        mock_read_reg_data,
        mock_write_reg_data,
        mock_read_module_information,
        mock_read_module_count,
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
        mock_read_reg_data.side_effect = [b"\x64\x00\x00\x00"]
        mock_read_parameter.return_value = 0

        # Act
        cpxap = CpxAp()

        # Assert
        mock_write_reg_data.assert_called_with(
            b"\x64\x00\x00\x00", cpx_ap_registers.TIMEOUT.register_address
        )
        mock_read_reg_data.assert_called_once()

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
    @patch.object(CpxAp, "write_reg_data")
    @patch.object(CpxAp, "read_reg_data")
    # @patch.object(CpxAp, "add_module")
    def test_rename_module_reflected_in_base(
        self,
        mock_read_reg_data,
        mock_write_reg_data,
        mock_read_module_information,
        mock_read_module_count,
    ):
        "Test constructor"
        # Arrange
        mock_read_module_count.return_value = 2

        module_code_list = [8323, 8199]
        module_information_list = [
            CpxAp.ModuleInformation(
                module_code=module_code, output_size=0, input_size=0
            )
            for module_code in module_code_list
        ]
        mock_read_module_information.side_effect = module_information_list
        mock_read_reg_data.return_value = b"\x64\x00\x00\x00"

        cpxap = CpxAp()

        # Act
        cpxap.cpxap8di.name = "my8di"  # pylint: disable="no-member"

        # Assert
        assert isinstance(cpxap.my8di, CpxAp8Di)  # pylint: disable="no-member"

    @patch.object(CpxAp, "read_module_count")
    @patch.object(CpxAp, "read_module_information")
    @patch.object(CpxAp, "write_reg_data")
    @patch.object(CpxAp, "read_reg_data")
    # @patch.object(CpxAp, "add_module")
    def test_constructor_inknown_module(
        self,
        mock_read_reg_data,
        mock_write_reg_data,
        mock_read_module_information,
        mock_read_module_count,
    ):
        "Test constructor"
        # Arrange
        mock_read_module_count.return_value = 7

        module_code_list = [0]
        module_information_list = [
            CpxAp.ModuleInformation(
                module_code=module_code, output_size=0, input_size=0
            )
            for module_code in module_code_list
        ]
        mock_read_module_information.side_effect = module_information_list
        mock_read_reg_data.return_value = b"\x64\x00\x00\x00"

        # Act & Assert
        with pytest.raises(NotImplementedError):
            cpxap = CpxAp()

    @pytest.fixture(scope="function")
    @patch.object(CpxAp, "read_module_count")
    @patch.object(CpxAp, "read_module_information")
    @patch.object(CpxAp, "write_reg_data")
    @patch.object(CpxAp, "read_reg_data")
    @patch.object(CpxAp, "read_parameter")
    def test_cpxap(
        self,
        mock_read_parameter,
        mock_read_reg_data,
        mock_write_reg_data,
        mock_read_module_information,
        mock_read_module_count,
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
        mock_read_reg_data.side_effect = [b"\x64\x00\x00\x00"]
        mock_read_parameter.return_value = 0

        with CpxAp() as cpxap:
            return cpxap

    def test_read_diagnostic_status(self, test_cpxap):
        """Test read_diagnostic_status"""
        # Arrange
        ret = [0xAA] * 5
        test_cpxap.read_parameter = Mock(return_value=ret)
        test_cpxap.read_module_count = Mock(return_value=4)

        ap_diagnosis_parameter = ParameterMapItem(
            ParameterNameMap()["ApDiagnosisStatus"].parameter_id,
            name="ApDiagnosisStatus",
            data_type="UINT8",
            size=5,
        )
        expected = CpxAp.Diagnostics.from_int(0xAA)

        # Act
        diagnostics = test_cpxap.read_diagnostic_status()

        # Assert
        test_cpxap.read_parameter.assert_called_with(0, ap_diagnosis_parameter)
        assert all(isinstance(d, CpxAp.Diagnostics) for d in diagnostics)
        assert diagnostics == [expected] * 5
        assert len(diagnostics) == 5
