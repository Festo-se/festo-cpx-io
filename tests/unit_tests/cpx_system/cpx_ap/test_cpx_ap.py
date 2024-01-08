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
    @patch.object(CpxAp, "add_module")
    def test_constructor_correct_type(
        self, mock_add_module, mock_read_module_information, mock_read_module_count
    ):
        "Test constructor"
        # Arrange
        mock_read_module_count.return_value = 6
        mock_read_module_information.return_value = [
            {"Module Code": 8323, "Order Text": "CPX-AP-I-EP-M12"},
            {"Module Code": 8199, "Order Text": "CPX-AP-I-8DI-M8-3P"},
            {"Module Code": 8197, "Order Text": "CPX-AP-I-4DI4DO-M12-5P"},
            {"Module Code": 8202, "Order Text": "CPX-AP-I-4AI-U-I-RTD-M12"},
            {"Module Code": 8201, "Order Text": "CPX-AP-I-4IOL-M12"},
            {"Module Code": 8198, "Order Text": "CPX-AP-I-4DI-M8-3P"},
        ]
        mock_add_module.side_effect = [
            CpxApEp(),
            CpxAp8Di(),
            CpxAp4Di4Do(),
            CpxAp4AiUI(),
            CpxAp4Iol(),
            CpxAp4Di(),
        ]

        # Act
        cpxap = CpxAp()

        # Assert
        assert isinstance(cpxap, CpxAp)
        assert len(cpxap.modules) == 6
        assert isinstance(cpxap.modules[0], CpxApEp)
        assert isinstance(cpxap.modules[1], CpxAp8Di)
        assert isinstance(cpxap.modules[2], CpxAp4Di4Do)
        assert isinstance(cpxap.modules[3], CpxAp4AiUI)
        assert isinstance(cpxap.modules[4], CpxAp4Iol)
        assert isinstance(cpxap.modules[5], CpxAp4Di)
