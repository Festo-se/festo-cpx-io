"""Contains tests for CpxAp8Di class"""
from unittest.mock import Mock, patch
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_ap.apep import CpxApEp  # pylint: disable=E0611


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

        mock_read_module_count.return_value = 2
        mock_add_module.side_effect = [
            CpxApEp(),
            CpxAp8Di(),
        ]
        mock_read_module_information.return_value = (
            [
                {"Module Code": 8323, "Order Text": "CPX-AP-I-EP-M12"},
                {"Module Code": 8199, "Order Text": "CPX-AP-I-8DI-M8-3P"},
            ],
        )
        with CpxAp() as cpxap:
            yield cpxap

    def test_constructor(self, test_cpxap):
        """Test constructor"""

        assert len(test_cpxap.modules) == 2
        assert isinstance(test_cpxap.modules[0], CpxApEp)
        assert isinstance(test_cpxap.modules[1], CpxAp8Di)

    def test_read_channels(self, test_cpxap):
        """Test read channels"""
        cpxap4di = test_cpxap.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAA])
        cpxap4di.base = mocked_base

        assert cpxap4di.read_channels() == [
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
        ]

    def test_read_channel(self, test_cpxap):
        """Test read channel"""
        cpxap4di = test_cpxap.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAA])
        cpxap4di.base = mocked_base

        assert cpxap4di.read_channel(0) is False
        assert cpxap4di.read_channel(1) is True
        assert cpxap4di.read_channel(2) is False
        assert cpxap4di.read_channel(3) is True

        assert cpxap4di.read_channel(4) is False
        assert cpxap4di.read_channel(5) is True
        assert cpxap4di.read_channel(6) is False
        assert cpxap4di.read_channel(7) is True

    def test_get_item(self, test_cpxap):
        """Test get item"""
        cpxap4di = test_cpxap.modules[1]

        mocked_base = Mock()
        mocked_base.read_reg_data = Mock(return_value=[0xAA])
        cpxap4di.base = mocked_base

        assert cpxap4di[0] is False
        assert cpxap4di[1] is True
        assert cpxap4di[2] is False
        assert cpxap4di[3] is True

        assert cpxap4di[4] is False
        assert cpxap4di[5] is True
        assert cpxap4di[6] is False
        assert cpxap4di[7] is True

    def test_configure_debounce_time(self, test_cpxap):
        """Test get item"""
        cpxap4di = test_cpxap.modules[1]

        mocked_base = Mock()
        mocked_base.write_parameter = Mock()
        cpxap4di.base = mocked_base

        cpxap4di.position = 1  # this is not done by the patched functions

        cpxap4di.configure_debounce_time(0)
        mocked_base.write_parameter.assert_called_with(1, 20014, 0, 0)
        cpxap4di.configure_debounce_time(1)
        mocked_base.write_parameter.assert_called_with(1, 20014, 0, 1)
        cpxap4di.configure_debounce_time(2)
        mocked_base.write_parameter.assert_called_with(1, 20014, 0, 2)
        cpxap4di.configure_debounce_time(3)
        mocked_base.write_parameter.assert_called_with(1, 20014, 0, 3)

        with pytest.raises(ValueError):
            cpxap4di.configure_debounce_time(-1)
            cpxap4di.configure_debounce_time(4)
