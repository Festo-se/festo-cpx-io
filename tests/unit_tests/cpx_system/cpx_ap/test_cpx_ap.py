"""Contains tests for CpxAp class"""

from unittest.mock import Mock, call, patch
import pytest

from pymodbus.client import ModbusTcpClient
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation
from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter


class TestCpxAp:
    "Test CpxAp"

    @patch("pymodbus.client.ModbusTcpClient.__new__", spec=True)
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
        spec=CpxAp.create_apdd_path,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
        spec=CpxAp.create_docu_path,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=CpxAp.read_module_count,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=CpxAp.read_apdd_information,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=CpxAp._grab_apdd,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._add_module",
        spec=CpxAp._add_module,
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
        spec=CpxAp.connected,
    )
    @patch("cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.perform_io", spec=True)
    def test_default_constructor(
        self,
        mock_perform_io,
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
        mock_modbus_tcp_client,
    ):
        """Test default constructor"""
        # Debugging: Check if mocks are callable
        for mock in [
            mock_create_apdd_path,
            mock_create_docu_path,
            mock_read_module_count,
            mock_read_apdd_information,
            mock__grab_apdd,
            mock_build_ap_module,
            mock_add_module,
            mock_generate_system_information_file,
            mock_os_listdir,
            mock_connected,
            mock_perform_io,
        ]:
            print(f"{mock} is callable: {callable(mock)}")
        # Arrange
        mock_set_timeout.return_value = None
        mock_create_apdd_path.return_value = "apdd_path"
        mock_create_docu_path.return_value = "docu_path"
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="CPX-AP-I-EP-M12", fw_version="0.0.1"
        )
        mock__grab_apdd.return_value = {}
        mock_add_module.return_value = ["Dummy"]
        mock_build_ap_module.return_value = None
        mock_generate_system_information_file.return_value = None
        mock_os_listdir.return_value = [""]
        mock_connected.return_value = True
        mock_modbus_tcp_client.return_value = Mock()
        mock_perform_io.return_value = Mock()
        # Act
        cpx_ap = CpxAp(ip_address="0.0.0.0")

        # Assert
        assert cpx_ap.next_output_register is None
        assert cpx_ap.next_input_register is None

        assert cpx_ap.global_diagnosis_register == 11000
        assert cpx_ap.next_diagnosis_register == 11006

        assert not mock_set_timeout.called

        assert cpx_ap.apdd_path == "apdd_path"
        assert cpx_ap.docu_path == "docu_path"

        mock_add_module.assert_called_once()
        mock_generate_system_information_file.assert_called_once()

    @patch("pymodbus.client.ModbusTcpClient.__new__", spec=True)
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=True,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=CpxAp.read_module_count,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=CpxAp.read_apdd_information,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=CpxAp._grab_apdd,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._add_module",
        spec=CpxAp._add_module,
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
        spec=CpxAp.connected,
    )
    def test_constructor_with_given_timeout(
        self,
        mock_connected,
        mock_os_listdir,
        mock_generate_system_information_file,
        mock_build_ap_module,
        mock_add_module,
        mock__grab_apdd,
        mock_read_apdd_information,
        mock_read_module_count,
        mock_set_timeout,
        mock_modbus_tcp_client,
    ):
        """Test constructor with timeout"""
        # Debugging: Check if mocks are callable
        for mock in [
            mock_read_module_count,
            mock_read_apdd_information,
            mock__grab_apdd,
            mock_build_ap_module,
            mock_add_module,
            mock_generate_system_information_file,
            mock_os_listdir,
            mock_connected,
        ]:
            print(f"{mock} is callable: {callable(mock)}")
        # Arrange
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="CPX-AP-I-EP-M12", fw_version="0.0.1"
        )
        mock_set_timeout.return_value = None
        mock_connected.return_value = True
        mock_modbus_tcp_client.return_value = Mock()

        # Act
        cpx_ap = CpxAp(ip_address="0.0.0.0", timeout=0.1, cycle_time=None)

        # Assert
        mock_set_timeout.assert_called_once

    @patch("pymodbus.client.ModbusTcpClient.__new__", spec=True)
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout",
        spec=CpxAp.set_timeout,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
        spec=CpxAp.create_apdd_path,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
        spec=CpxAp.create_docu_path,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
        spec=CpxAp.read_module_count,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
        spec=CpxAp.read_apdd_information,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
        spec=CpxAp._grab_apdd,
    )
    @patch(
        "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._add_module",
        spec=CpxAp._add_module,
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
        spec=CpxAp.connected,
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
        mock_modbus_tcp_client,
    ):
        """Test constructor"""
        # Arrange
        mock_set_timeout.return_value = None
        mock_create_apdd_path.return_value = "apdd_path"
        mock_create_docu_path.return_value = "docu_path"
        mock_read_module_count.return_value = 1
        mock_read_apdd_information.return_value = CpxAp.ApInformation(
            order_text="CPX-AP-I-EP-M12", fw_version="0.0.1"
        )
        mock__grab_apdd.return_value = {}
        mock_add_module.return_value = ["Dummy"]
        mock_build_ap_module.return_value = None
        mock_generate_system_information_file.return_value = None
        mock_os_listdir.return_value = [""]
        mock_connected.return_value = True
        mock_modbus_tcp_client.return_value = Mock()

        # Act
        cpx_ap = CpxAp(
            apdd_path="myApddPath",
            docu_path="myDocuPath",
            ip_address="0.0.0.0",
            cycle_time=None,
        )

        # Assert
        assert cpx_ap.next_output_register is None
        assert cpx_ap.next_input_register is None
        assert not mock_set_timeout.called
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
            spec=CpxAp.connected,
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
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._add_module",
            spec=CpxAp._add_module,
        )
        mock__grab_apdd = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp._grab_apdd",
            spec=CpxAp._grab_apdd,
            return_value={},
        )
        mock_read_apdd_information = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_apdd_information",
            spec=CpxAp.read_apdd_information,
            return_value=CpxAp.ApInformation(
                order_text="CPX-AP-I-EP-M12", fw_version="0.0.1"
            ),
        )
        mock_read_module_count = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.read_module_count",
            spec=CpxAp.read_module_count,
            return_value=1,
        )
        mock_create_docu_path = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_docu_path",
            spec=CpxAp.create_docu_path,
            return_value="mock_docu_path",
        )
        mock_create_apdd_path = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.create_apdd_path",
            spec=CpxAp.create_apdd_path,
            return_value="mock_apdd_path",
        )
        mock_set_timeout = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.CpxAp.set_timeout", spec=CpxAp.set_timeout
        )
        mock_modbus_tcp_client = mocker.patch(
            "pymodbus.client.ModbusTcpClient.__new__", spec=True, return_value=Mock()
        )
        yield CpxAp(ip_address="0.0.0.0", cycle_time=None)

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
            side_effect=lambda *args: "/".join(args),
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
        mock_remove.assert_has_calls(
            [call("mock_apdd_path/file1"), call("mock_apdd_path/file2")]
        )

    def test_create_apdd_path(self, ap_fixture, mocker):
        # Arrange

        # need to stop the mock of create_apdd_path from the fixture
        mocker.stopall()
        mock_user_data_dir = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.platformdirs.user_data_dir",
            return_value="/dummy_user/festo",
        )
        mock_join = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join",
            side_effect=lambda *args: "/".join(args),
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
        mock_user_data_dir = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.platformdirs.user_data_dir",
            return_value="/dummy_user/festo",
        )
        mock_join = mocker.patch(
            "cpx_io.cpx_system.cpx_ap.cpx_ap.os.path.join",
            side_effect=lambda *args: "/".join(args),
        )
        mock_makedirs = mocker.patch("cpx_io.cpx_system.cpx_ap.cpx_ap.os.makedirs")

        # Act
        ret = ap_fixture.create_docu_path()

        # Assert
        assert ret == "/dummy_user/festo/docu"

    def test_getter_modules(self, ap_fixture):
        # Arrange
        mocked_list = [
            ApModule(
                ApddInformation(
                    description="description",
                    name="name",
                    module_type="module_type",
                    configurator_code="configurator_code",
                    part_number="part_number",
                    module_class="module_class",
                    module_code="module_code",
                    order_text="order_text",
                    product_category="product_category",
                    product_family="product_family",
                ),
                ([], [], []),
                [],
                [],
            )
        ]

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
            (200, b"\xc8\x00\x00\x00"),
            (10000, b"\x10\x27\x00\x00"),
            (4294967295, b"\xff\xff\xff\xff"),
        ],
    )
    def test_set_timeout_accepted_values(
        self, ap_fixture, mocker, input_value, expected_output
    ):
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

    @pytest.mark.parametrize(
        "input_value", [10, 20, 30, 40, 50, 60, 61, 70, 80, 81, 82, 83, 84, 85]
    )
    def test_add_module_io_module(self, ap_fixture, mocker, input_value):
        # Arrange
        # stop mocking the add_module function
        mocker.stopall()

        apdd_information = ApddInformation(
            description="description",
            name="CPX-AP-I-EP-M12",
            module_type="module_type",
            configurator_code="configurator_code",
            part_number="part_number",
            module_class=input_value,
            module_code="module_code",
            order_text="order_text",
            product_category="product_category",
            product_family="product_family",
        )

        module = ApModule(apdd_information, [(), (), ()], [], [])
        module._configure = Mock()

        ap_fixture.update_module_names = Mock()

        # Act
        ret = ap_fixture._add_module(module, apdd_information)

        # Assert
        assert ret == module
        assert module.name == "CPX-AP-I-EP-M12"

    def test_add_module_bus_module(self, ap_fixture, mocker):
        # Arrange
        # stop mocking the add_module function
        mocker.stopall()

        apdd_information = ApddInformation(
            description="description",
            name="name",
            module_type="module_type",
            configurator_code="configurator_code",
            part_number="part_number",
            module_class=100,
            module_code="module_code",
            order_text="order_text",
            product_category="product_category",
            product_family="product_family",
        )

        module = ApModule(apdd_information, [(), (), ()], [], [])
        module._configure = Mock()

        ap_fixture.update_module_names = Mock()

        # Act
        ret = ap_fixture._add_module(module, apdd_information)

        # Assert
        assert ret == module
        assert ap_fixture.next_output_register == 0
        assert ap_fixture.next_input_register == 5000

    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (b"\x00\x00\x00\x00", 0),
            (b"\x01\x00\x00\x00", 1),
            (b"\x00\x01\x00\x00", 256),
            (b"\xff\xff\xff\xff", 4294967295),
        ],
    )
    def test_read_module_count(self, ap_fixture, mocker, input_value, expected_output):
        # Arrange
        # stop mocking the add_module function
        mocker.stopall()
        ap_fixture.read_reg_data = Mock(return_value=input_value)

        # Act
        ret = ap_fixture.read_module_count()

        # Assert
        ap_fixture.read_reg_data.assert_called_with(12000, 1)
        assert ret == expected_output

    def test_read_apdd_information(self, ap_fixture, mocker):
        # Arrange
        # stop mocking the read_apdd_information function
        mocker.stopall()
        ap_fixture.read_reg_data = Mock(return_value=b"\x34\x35\x36\x37\x38\x39")

        # Act
        ret = ap_fixture.read_apdd_information(0)

        # Assert
        assert isinstance(ret, CpxAp.ApInformation)

    def test_read_diagnostics_status(self, ap_fixture):
        # Arrange
        ap_fixture.read_parameter = Mock(return_value=[0, 1, 2])

        # Act
        ret = ap_fixture.read_diagnostic_status()

        # Assert
        assert all(isinstance(r, CpxAp.Diagnostics) for r in ret)

    def test_read_global_diagnosis_state(self, ap_fixture):
        # Arrange
        ap_fixture.read_reg_data = Mock(return_value=b"\xaa\xaa\xaa\xaa")

        # Act
        ret = ap_fixture.read_global_diagnosis_state()

        # Assert
        ap_fixture.read_reg_data.assert_called_with(11000, length=2)

        assert ret == {
            "Device available": False,
            "Current": True,
            "Voltage": False,
            "Temperature": True,
            "reserved": False,
            "Movement": True,
            "Configuration / Parameters": False,
            "Monitoring": True,
            "Communication": False,
            "Safety": True,
            "Internal Hardware": False,
            "Software": True,
            "Maintenance": False,
            "Misc": True,
            "reserved(14)": False,
            "reserved(15)": True,
            "External Device": False,
            "Security": True,
            "Encoder": False,
        }

    def test_read_active_diagnosis_count(self, ap_fixture):
        # Arrange
        ap_fixture.read_reg_data = Mock(return_value=b"\x01\x00\x00\x00")
        # Act
        ret = ap_fixture.read_active_diagnosis_count()
        # Assert
        ap_fixture.read_reg_data.assert_called_with(11002)
        assert ret == 1

    def test_read_latest_diagnosis_index(self, ap_fixture):
        # Arrange
        ap_fixture.read_reg_data = Mock(return_value=b"\x01\x00\x00\x00")
        # Act
        ret = ap_fixture.read_latest_diagnosis_index()
        # Assert
        ap_fixture.read_reg_data.assert_called_with(11003)
        assert ret == 0

    def test_read_latest_diagnosis_code(self, ap_fixture):
        # Arrange
        ap_fixture.read_reg_data = Mock(return_value=b"\x01\x00\x00\x00")
        # Act
        ret = ap_fixture.read_latest_diagnosis_code()
        # Assert
        ap_fixture.read_reg_data.assert_called_with(11004, length=2)
        assert ret == 1

    def test_write_parameter_no_instance(self, ap_fixture):
        # Arrange
        position = 12
        parameter = Parameter(
            parameter_id=1,
            parameter_instances={},
            is_writable=True,
            array_size=0,
            data_type="UINT8",
            default_value=0,
            description="description",
            name="name",
        )
        data = 2

        ap_fixture._write_parameter_raw = Mock()

        # Act
        ap_fixture.write_parameter(position, parameter, data)

        # Assert
        ap_fixture._write_parameter_raw.assert_called_with(
            position, parameter.parameter_id, 0, b"\x02"
        )

    def test_write_parameter_with_instance(self, ap_fixture):
        # Arrange
        position = 12
        parameter = Parameter(
            parameter_id=1,
            parameter_instances={},
            is_writable=True,
            array_size=0,
            data_type="UINT8",
            default_value=0,
            description="description",
            name="name",
        )
        data = 2
        instance = 13

        ap_fixture._write_parameter_raw = Mock()

        # Act
        ap_fixture.write_parameter(position, parameter, data, instance)

        # Assert
        ap_fixture._write_parameter_raw.assert_called_with(
            position, parameter.parameter_id, instance, b"\x02"
        )

    def test_read_parameter_no_instance(self, ap_fixture):
        # Arrange
        position = 12
        parameter = Parameter(
            parameter_id=1,
            parameter_instances={},
            is_writable=True,
            array_size=0,
            data_type="UINT8",
            default_value=0,
            description="description",
            name="name",
        )

        ap_fixture._read_parameter_raw = Mock(return_value=b"\x02")

        # Act
        ret = ap_fixture.read_parameter(position, parameter)

        # Assert
        ap_fixture._read_parameter_raw.assert_called_with(
            position, parameter.parameter_id, 0
        )

        assert ret == 2

    def test_read_parameter_with_instance(self, ap_fixture):
        # Arrange
        position = 12
        parameter = Parameter(
            parameter_id=1,
            parameter_instances={},
            is_writable=True,
            array_size=0,
            data_type="UINT8",
            default_value=0,
            description="description",
            name="name",
        )
        instance = 13

        ap_fixture._read_parameter_raw = Mock(return_value=b"\x02")

        # Act
        ret = ap_fixture.read_parameter(position, parameter, instance)

        # Assert
        ap_fixture._read_parameter_raw.assert_called_with(
            position, parameter.parameter_id, instance
        )

        assert ret == 2

    def test_name(self, ap_fixture):
        """Test name access"""
        # Arrange
        # Act
        ap_fixture._modules = [
            ApModule(
                ApddInformation(
                    description="description",
                    name="name1",
                    module_type="module_type",
                    configurator_code="configurator_code",
                    part_number="part_number",
                    module_class="module_class",
                    module_code="module_code",
                    order_text="order_text",
                    product_category="product_category",
                    product_family="product_family",
                ),
                ([], [], []),
                [],
                [],
            ),
            ApModule(
                ApddInformation(
                    description="description",
                    name="name2",
                    module_type="module_type",
                    configurator_code="configurator_code",
                    part_number="part_number",
                    module_class="module_class",
                    module_code="module_code",
                    order_text="order_text",
                    product_category="product_category",
                    product_family="product_family",
                ),
                ([], [], []),
                [],
                [],
            ),
            ApModule(
                ApddInformation(
                    description="description",
                    name="name3",
                    module_type="module_type",
                    configurator_code="configurator_code",
                    part_number="part_number",
                    module_class="module_class",
                    module_code="module_code",
                    order_text="order_text",
                    product_category="product_category",
                    product_family="product_family",
                ),
                ([], [], []),
                [],
                [],
            ),
        ]

        # Assert
        assert ap_fixture.modules[0].name == "name1"
        assert ap_fixture.modules[1].name == "name2"
        assert ap_fixture.modules[2].name == "name3"
