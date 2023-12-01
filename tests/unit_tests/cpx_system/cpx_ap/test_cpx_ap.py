"""Contains tests for CpxAp class"""
from unittest.mock import Mock, patch
import pytest

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol  # pylint: disable=E0611


class TestCpxAp:
    "Test CpxAp"

    @pytest.fixture
    def patched_functions(self):
        """Patch functions"""
        with patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count"
        ) as mock_read_module_count, patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module"
        ) as mock_add_module, patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_information"
        ) as mock_read_module_information:
            yield mock_read_module_count, mock_add_module, mock_read_module_information

    @pytest.fixture(scope="function")
    def test_cpxap(self, patched_functions):
        """Test fixture"""

        (
            mock_read_module_count,
            mock_add_module,
            mock_read_module_information,
        ) = patched_functions

        mock_read_module_count.return_value = 6
        mock_add_module.side_effect = [
            CpxApEp(),
            CpxAp8Di(),
            CpxAp4Di4Do(),
            CpxAp4AiUI(),
            CpxAp4Iol(),
            CpxAp4Di(),
        ]
        mock_read_module_information.return_value = (
            [
                {"Module Code": 8323, "Order Text": "CPX-AP-I-EP-M12"},
                {"Module Code": 8199, "Order Text": "CPX-AP-I-8DI-M8-3P"},
                {"Module Code": 8197, "Order Text": "CPX-AP-I-4DI4DO-M12-5P"},
                {"Module Code": 8202, "Order Text": "CPX-AP-I-4AI-U-I-RTD-M12"},
                {"Module Code": 8201, "Order Text": "CPX-AP-I-4IOL-M12"},
                {"Module Code": 8198, "Order Text": "CPX-AP-I-4DI-M8-3P"},
            ],
        )
        with CpxAp() as cpxap:
            yield cpxap

    def test_constructor(self, test_cpxap):
        "Test constructor"

        assert isinstance(test_cpxap, CpxAp)
        assert len(test_cpxap.modules) == 6
        assert isinstance(test_cpxap.modules[0], CpxApEp)
        assert isinstance(test_cpxap.modules[1], CpxAp8Di)
        assert isinstance(test_cpxap.modules[2], CpxAp4Di4Do)
        assert isinstance(test_cpxap.modules[3], CpxAp4AiUI)
        assert isinstance(test_cpxap.modules[4], CpxAp4Iol)
        assert isinstance(test_cpxap.modules[5], CpxAp4Di)
