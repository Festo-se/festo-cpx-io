"""Contains tests for CpxAp class"""

from unittest.mock import Mock, call, patch
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


class TestCpxAp:
    "Test CpxAp"

    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.build_ap_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.generate_system_information_file",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir",
        spec=True,
    )
    def test_default_constructor(
        self,
        mock_os_listdir,
        mock_generate_system_information_file,
        mock_build_ap_module,
        mock_add_module,
        mock__grab_apdd,
        mock_read_apdd_information,
        mock_read_module_count,
        mock_create_docu_path,
        mock_create_apdd_path,
        mock_set_timeout,
    ):
        """Test default constructor"""
        # Arrange
        mock_create_apdd_path.return_value = "apdd_path"
        mock_create_docu_path.return_value = "docu_path"
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="test", fw_version="0.0.1"
        )
        mock__grab_apdd.return_value = {}
        mock_build_ap_module.return_value = None
        mock_os_listdir.return_value = [""]

        # Act
        cpx_ap = CpxAp()

        # Assert
        assert cpx_ap.next_output_register is None
        assert cpx_ap.next_input_register is None
        mock_set_timeout.assert_called_once()
        assert cpx_ap.apdd_path == "apdd_path"
        assert cpx_ap.docu_path == "docu_path"
        mock_read_apdd_information.assert_called_once()
        mock__grab_apdd.assert_called_once()
        mock_build_ap_module.assert_called_once()
        mock_add_module.assert_called_once()
        mock_generate_system_information_file.assert_called_once()

    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.build_ap_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.generate_system_information_file",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir",
        spec=True,
    )
    def test_constructor_with_paths(
        self,
        mock_os_listdir,
        mock_generate_system_information_file,
        mock_build_ap_module,
        mock_add_module,
        mock__grab_apdd,
        mock_read_apdd_information,
        mock_read_module_count,
        mock_create_docu_path,
        mock_create_apdd_path,
        mock_set_timeout,
    ):
        """Test constructor"""
        # Arrange
        mock_create_apdd_path.return_value = "apdd_path"
        mock_create_docu_path.return_value = "docu_path"
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="test", fw_version="0.0.1"
        )
        mock__grab_apdd.return_value = {}
        mock_build_ap_module.return_value = None
        mock_os_listdir.return_value = [""]

        # Act
        cpx_ap = CpxAp(apdd_path="myApddPath", docu_path="myDocuPath")

        # Assert
        assert cpx_ap.next_output_register is None
        assert cpx_ap.next_input_register is None
        mock_set_timeout.assert_called_once()
        assert cpx_ap.apdd_path == "myApddPath"
        assert cpx_ap.docu_path == "myDocuPath"
        mock_read_apdd_information.assert_called_once()
        mock__grab_apdd.assert_called_once()
        mock_build_ap_module.assert_called_once()
        mock_add_module.assert_called_once()
        mock_generate_system_information_file.assert_called_once()

    @pytest.fixture(scope="function")
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.build_ap_module",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.generate_system_information_file",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir",
        spec=True,
    )
    def ap_fixture(
        self,
        mock_os_listdir,
        mock_generate_system_information_file,
        mock_build_ap_module,
        mock_add_module,
        mock__grab_apdd,
        mock_read_apdd_information,
        mock_read_module_count,
        mock_create_docu_path,
        mock_create_apdd_path,
        mock_set_timeout,
    ):
        """AP fixture"""
        mock_create_apdd_path.return_value = "apdd_path"
        mock_create_docu_path.return_value = "docu_path"
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="test", fw_version="0.0.1"
        )
        mock__grab_apdd.return_value = {}
        mock_build_ap_module.return_value = None
        mock_os_listdir.return_value = [""]

        yield CpxAp()

    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.isdir", spec=True)
    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir", spec=True)
    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join", spec=True)
    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.isfile", spec=True)
    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.remove", spec=True)
    def test_delete_apdds(
        self, mock_remove, mock_isfile, mock_join, mock_listdir, mock_isdir, ap_fixture
    ):
        # Arrange
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1", "file2"]
        mock_join.return_value = ["path/file1", "path/file2"]
        mock_isfile.return_value = True

        # Act
        ap_fixture.delete_apdds()

        # Assert
        mock_remove.assert_has_calls([call("path/file1"), call("path/file2")])

    @patch("cpx_io.cpx_system.cpx_ap.platformdirs.user_data_dir", spec=True)
    def test_create_apdd_path(self, ap_fixture, mock_user_data_dir):
        # Arrange

        # Act

        pass  # Assert

    def test_create_docu_path(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_getter_modules(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_getter_apdd_path(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_getter_docu_path(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_set_timeout(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_add_module(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_read_module_count(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_read_apdd_information(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_read_diagnostics_status(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_write_parameter(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert

    def test_(self, ap_fixture):
        # Arrange

        # Act

        pass  # Assert
