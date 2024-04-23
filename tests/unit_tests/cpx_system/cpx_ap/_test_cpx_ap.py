"""Contains tests for CpxAp class"""

from unittest.mock import patch, Mock
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
import cpx_io.cpx_system.cpx_ap.ap_modbus_registers as reg


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
            b"\x64\x00\x00\x00", reg.TIMEOUT.register_address
        )
        mock_read_reg_data.assert_called_once()

        assert isinstance(cpxap, CpxAp)
        assert len(cpxap.modules) == 7
        assert all(isinstance(m, ApModule) for m in cpxap.modules)

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
        cpxap.cpx_ap_i_8di_m8_3p.name = "my8di"  # pylint: disable="no-member"

        # Assert
        assert isinstance(cpxap.my8di, ApModule)  # pylint: disable="no-member"

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
