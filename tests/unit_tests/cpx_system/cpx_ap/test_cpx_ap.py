"""Contains tests for CpxAp class"""

from unittest.mock import Mock, call, patch
import pytest

from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation

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
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.connected",
        spec=True,
    )
    def test_default_constructor(
        self,
        mock_connected,
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
        mock_add_module.return_value = ["Dummy"]
        mock_generate_system_information_file.return_value = None
        mock_os_listdir.return_value = [""]
        mock_connected.return_value = True

        # Act
        cpx_ap = CpxAp()

        # Assert
        assert cpx_ap.next_output_register is None
        assert cpx_ap.next_input_register is None

        assert cpx_ap.global_diagnosis_register == 11000
        assert cpx_ap.next_diagnosis_register == 11006

        mock_set_timeout.assert_called_once()

        assert cpx_ap.apdd_path == "apdd_path"
        assert cpx_ap.docu_path == "docu_path"

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
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.connected",
        spec=True,
    )
    def test_constructor_with_paths(
        self,
        mock_connected,
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
        mock_connected.return_value = True

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
    def ap_fixture(self, mocker):
        """AP fixture"""
        mock_connected = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.connected",
            spec=True,
            return_value=True,
        )
        mock_os_listdir = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir", spec=True, return_value=[""]
        )
        mock_generate_system_information_file = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.generate_system_information_file",
            spec=True,
        )
        mock_build_ap_module = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.build_ap_module",
            spec=True,
            return_value=None,
        )
        mock_add_module = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.add_module",
            spec=True,
        )
        mock__grab_apdd = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
            spec=True,
            return_value={},
        )
        mock_read_apdd_information = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
            spec=True,
            return_value=CpxAp.ApInformation(order_text="test", fw_version="0.0.1"),
        )
        mock_read_module_count = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
            spec=True,
            return_value=1,
        )
        mock_create_docu_path = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
            spec=True,
            return_value="mock_docu_path",
        )
        mock_create_apdd_path = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
            spec=True,
            return_value="mock_apdd_path",
        )
        mock_set_timeout = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout", spec=True
        )

        yield CpxAp()

    def test_connected(self, ap_fixture):
        # Arrange
        ap_fixture.client = Mock()
        ap_fixture.client.connected = Mock()

        # Act
        ap_fixture.connected()

        # Assert
        # is called twice. once for fixture and once for Act
        assert ap_fixture.connected.call_count == 2

    def test_delete_apdds(self, ap_fixture, mocker):
        # Arrange
        mock_remove = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.remove",
        )
        mock_isfile = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.isfile",
            return_value=True,
        )
        mock_join = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join",
            side_effect = lambda *args: "/".join(args)
        )
        mock_listdir = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.listdir",
            return_value=["file1", "file2"],
        )
        mock_isdir = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.isdir",
            return_value=True,
        )

        # Act
        ap_fixture.delete_apdds()

        # Assert
        mock_remove.assert_has_calls([call("mock_apdd_path/file1"), call("mock_apdd_path/file2")])

    def test_create_apdd_path(self, ap_fixture, mocker):
        # Arrange

        # need to stop the mock of create_apdd_path from the fixture
        mocker.stopall()
        mock_user_data_dir = mocker.patch("cpx_io.cpx_system.cpx_ap.cpx_ap.platformdirs.user_data_dir", return_value="/dummy_user/festo")
        mock_join = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join",
            side_effect = lambda *args: "/".join(args)
        )
        mock_makedirs = mocker.patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.makedirs")

        # Act
        ret = ap_fixture.create_apdd_path()

        # Assert
        assert ret == "/dummy_user/festo/apdds"


    def test_create_docu_path(self, ap_fixture, mocker):
        # Arrange

        # need to stop the mock of create_apdd_path from the fixture
        mocker.stopall()
        mock_user_data_dir = mocker.patch("cpx_io.cpx_system.cpx_ap.cpx_ap.platformdirs.user_data_dir", return_value="/dummy_user/festo")
        mock_join = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join",
            side_effect = lambda *args: "/".join(args)
        )
        mock_makedirs = mocker.patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.makedirs")

        # Act
        ret = ap_fixture.create_docu_path()

        # Assert
        assert ret == "/dummy_user/festo/docu"

    def test_getter_modules(self, ap_fixture):
        # Arrange
        mocked_list = [ApModule(ApddInformation(
            description= "description",
            name= "name",
            module_type= "module_type",
            configurator_code= "configurator_code",
            part_number= "part_number",
            module_class= "module_class",
            module_code= "module_code",
            order_text= "order_text",
            product_category= "product_category",
            product_family= "product_family"),([],[],[]),[],[])]
        
        ap_fixture._modules = mocked_list

        # Act & Assert
        assert ap_fixture.modules == mocked_list

    def test_getter_apdd_path(self, ap_fixture):
        # Arrange

        # Act & Assert
        assert ap_fixture.apdd_path == ap_fixture._apdd_path

    def test_getter_docu_path(self, ap_fixture):
        # Arrange

        # Act & Assert
        assert ap_fixture.docu_path == ap_fixture._docu_path

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (0, b"\x00\x00\x00\x00"),
            (1, b"\x64\x00\x00\x00"),
            (99, b"\x64\x00\x00\x00"),
            (100, b"\x64\x00\x00\x00"),
            (200, b"\xC8\x00\x00\x00"),
            (10000, b"\x10\x27\x00\x00"),
            (4294967295, b"\xFF\xFF\xFF\xFF"),
        ],
    )
    def test_set_timeout_accepted_values(self, ap_fixture, mocker, input_value, expected_output):
        # Arrange
        # stop mocking the timeout function
        mocker.stopall()
        ap_fixture.write_reg_data = Mock()
        ap_fixture.read_reg_data = Mock(return_value=expected_output)

        # Act
        ap_fixture.set_timeout(input_value)

        # Assert
        ap_fixture.write_reg_data.assert_called_with(expected_output, 14000)

    def test_set_timeout_too_big(self, ap_fixture, mocker):
        # Arrange
        # stop mocking the timeout function
        mocker.stopall()
        ap_fixture.write_reg_data = Mock()

        # Act & Assert
        with pytest.raises(OverflowError):
            ap_fixture.set_timeout(4294967296)

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
