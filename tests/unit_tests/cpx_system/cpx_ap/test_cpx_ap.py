"""Contains tests for CpxAp class"""
from unittest.mock import Mock, patch
import pytest

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp  # pylint: disable=E0611


class TestCpxAp:
    "Test CpxAp"

    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count", return_value=1)
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module",
        return_value=[CpxApEp()],
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_information",
        return_value={"Module Code": 8323, "Order Text": "CPX-AP-I-EP-M12"},
    )
    def test_constructor_one_module(
        self, mock_read_module_count, mock_add_module, mock_read_module_information
    ):
        "Test constructor"
        cpx_ap = CpxAp()

        mock_read_module_count.assert_called_once()
        mock_add_module.assert_called_once()
        mock_read_module_information.assert_called_once()
