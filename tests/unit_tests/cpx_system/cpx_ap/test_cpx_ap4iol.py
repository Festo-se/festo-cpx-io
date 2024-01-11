"""Contains tests for CpxAp4Iol class"""
from unittest.mock import Mock, call, patch
import pytest

from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.utils.boollist import boollist_to_int


class TestCpxAp4Iol:
    "Test CpxAp4Iol"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxap4iol = CpxAp4Iol()

        # Assert
        assert isinstance(cpxap4iol, CpxAp4Iol)

    @patch.object(
        CpxApModule,
        "read_ap_parameter",
        return_value=CpxApModule.ApParameters(
            fieldbus_serial_number=0,
            product_key="pk",
            firmware_version="fw",
            module_code="mc",
            temp_asic="ta",
            logic_voltage="lv",
            load_voltage="ld",
            hw_version="hw",
        ),
    )
    def test_read_ap_parameter(self, mock_read_ap_parameter):
        """Test read_ap_parameter"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(read_parameter=Mock(return_value=[8201, 0]))

        # Act
        PARAMETER_ID_VARIANT = 20090  # pylint: disable=invalid-name
        PARAMETER_ID_VOLTAGE = 20097  # pylint: disable=invalid-name
        params = cpxap4iol.read_ap_parameter()

        # Assert
        mock_read_ap_parameter.assert_called_once()
        cpxap4iol.base.read_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID_VARIANT, 0),
                call(MODULE_POSITION, PARAMETER_ID_VOLTAGE, 0),
            ],
            any_order=True,
        )
        assert params.io_link_variant == "CPX-AP-I-4IOL-M12 variant 8"
        assert params.operating_supply is False

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.information = CpxAp.ModuleInformation(
            module_code=0,
            module_class=1,
            communication_profiles=0,
            input_size=20,
            input_channels=0,
            output_size=0,
            output_channels=0,
            hw_version=0,
            fw_version=0,
            serial_number=0,
            product_key=0,
            order_text=0,
        )
        v0, v1, v2, v3, v4, v5, v6, v7 = 0, 1, 2, 3, 4, 5, 6, 7
        cpxap4iol.base = Mock(
            read_reg_data=Mock(return_value=[v0, v1, v2, v3, v4, v5, v6, v7])
        )

        # Act
        channel_values = cpxap4iol.read_channels()

        # Assert
        # values are in byteorder: little
        assert channel_values == [
            [
                int.from_bytes(v0.to_bytes(2, byteorder="little"), byteorder="big"),
                int.from_bytes(v1.to_bytes(2, byteorder="little"), byteorder="big"),
            ],
            [
                int.from_bytes(v2.to_bytes(2, byteorder="little"), byteorder="big"),
                int.from_bytes(v3.to_bytes(2, byteorder="little"), byteorder="big"),
            ],
            [
                int.from_bytes(v4.to_bytes(2, byteorder="little"), byteorder="big"),
                int.from_bytes(v5.to_bytes(2, byteorder="little"), byteorder="big"),
            ],
            [
                int.from_bytes(v6.to_bytes(2, byteorder="little"), byteorder="big"),
                int.from_bytes(v7.to_bytes(2, byteorder="little"), byteorder="big"),
            ],
        ]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.read_channel = Mock(return_value=[[0xDEAD], [0xBEEF]])
        # Act
        channel_values = [cpxap4iol[idx] for idx in range(4)]

        # Assert
        assert channel_values == [[[0xDEAD], [0xBEEF]]] * 4

    def test_read_channel_correct_value(self):
        """Test read_channel"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.read_channels = Mock(
            return_value=[
                [[0xDEAD], [0xBEEF]],
                [[0xDEAF], [0xCAFE]],
                [[0xABCD], [0x1234]],
                [[0xDEED], [0xBEEB]],
            ]
        )
        # Act
        channel_values = [cpxap4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [
            [[0xDEAD], [0xBEEF]],
            [[0xDEAF], [0xCAFE]],
            [[0xABCD], [0x1234]],
            [[0xDEED], [0xBEEB]],
        ]

    @pytest.mark.parametrize("channel_number", [0, 1, 2, 3])
    def test_write_channel_correct_values(self, channel_number):
        """Test write channel"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock(write_reg_data=Mock())
        cpxap4iol.information = CpxAp.ModuleInformation(
            module_code=0,
            module_class=1,
            communication_profiles=0,
            input_size=0,
            input_channels=0,
            output_size=16,  # makes module_output size=8, channel_size=2
            output_channels=0,
            hw_version=0,
            fw_version=0,
            serial_number=0,
            product_key=0,
            order_text=0,
        )
        cpxap4iol.output_register = 0

        data = [
            int.from_bytes(x.to_bytes(2, byteorder="little"), byteorder="big")
            for x in range(8)
        ]

        # Act
        cpxap4iol.write_channel(channel_number, list(range(8)))

        # Assert
        cpxap4iol.base.write_reg_data.assert_called_with(
            data, cpxap4iol.output_register + 2 * channel_number
        )

    def test_set_item(self):
        """Test set item"""
        # Arange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.write_channel = Mock()

        # Act
        cpxap4iol[0] = [0, 1, 2, 3]
        cpxap4iol[1] = [1, 1, 2, 3]
        cpxap4iol[2] = [2, 1, 2, 3]
        cpxap4iol[3] = [3, 1, 2, 3]

        # Assert
        cpxap4iol.write_channel.assert_has_calls(
            [
                call(0, [0, 1, 2, 3]),
                call(1, [1, 1, 2, 3]),
                call(2, [2, 1, 2, 3]),
                call(3, [3, 1, 2, 3]),
            ]
        )

    @pytest.mark.parametrize("channel_number", [0, 1, 2, 3])
    def test_read_pqi_one_channel(self, channel_number):
        """Test read_pqi"""
        # Arange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock(read_reg_data=Mock(return_value=[0xCACA]))
        cpxap4iol.input_register = 0
        expected = {
            "Port Qualifier": "input data is valid",
            "Device Error": "there is at least one error or warning on the device or port",
            "DevCOM": "device is not connected or not yet in operation",
        }

        # Act & Assert
        assert cpxap4iol.read_pqi(channel_number) == expected

    def test_read_pqi_all_channels(self):
        """Test read_pqi"""
        # Arange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock(read_reg_data=Mock(return_value=[0xCACA]))
        cpxap4iol.input_register = 0
        expected = {
            "Port Qualifier": "input data is valid",
            "Device Error": "there is at least one error or warning on the device or port",
            "DevCOM": "device is not connected or not yet in operation",
        }

        # Act
        pqi = cpxap4iol.read_pqi()

        # Assert
        assert all(p == expected for p in pqi)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (1, 1), (2, 2)])
    def test_configure_monitoring_load_supply(self, input_value, expected_value):
        """Test configure_monitoring_load_supply and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20022  # pylint: disable=invalid-name
        cpxap4iol.configure_monitoring_load_supply(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4iol.configure_monitoring_load_supply(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value", [(0, 0), (16, 16), (183, 183)]
    )
    def test_configure_target_cycle_time_all_channels(
        self, input_value, expected_value
    ):
        """Test configure_target_cycle_time and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20049  # pylint: disable=invalid-name
        cpxap4iol.configure_target_cycle_time(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 1, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 2, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 3, expected_value),
            ]
        )

    @pytest.mark.parametrize(
        "input_value, expected_value", [(0, 0), (16, 16), (183, 183)]
    )
    def test_configure_target_cycle_time_one_channel(self, input_value, expected_value):
        """Test configure_target_cycle_time and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20049  # pylint: disable=invalid-name
        cpxap4iol.configure_target_cycle_time(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 1])
    def test_configure_target_cycle_time_raise_error(self, input_value):
        """Test configure_target_cycle_time and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4iol.configure_target_cycle_time(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value", [(False, False), (True, True)]
    )
    def test_configure_device_lost_diagnostics_all_channels(
        self, input_value, expected_value
    ):
        """Test configure_device_lost_diagnostics and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20050  # pylint: disable=invalid-name
        cpxap4iol.configure_device_lost_diagnostics(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 1, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 2, expected_value),
                call(MODULE_POSITION, PARAMETER_ID, 3, expected_value),
            ]
        )

    @pytest.mark.parametrize(
        "input_value, expected_value", [(False, False), (True, True)]
    )
    def test_configure_device_lost_diagnostics_one_channel(
        self, input_value, expected_value
    ):
        """Test configure_device_lost_diagnostics and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20050  # pylint: disable=invalid-name
        cpxap4iol.configure_device_lost_diagnostics(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    @pytest.mark.parametrize(
        "input_value, expected_value", [(0, 0), (1, 1), (2, 2), (3, 3), (97, 97)]
    )
    def test_configure_port_mode_single_channel(self, input_value, expected_value):
        """Test configure_port_mode and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20071  # pylint: disable=invalid-name
        cpxap4iol.configure_port_mode(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    def test_configure_port_mode_more_channels(self):
        """Test configure_port_mode and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20071  # pylint: disable=invalid-name
        cpxap4iol.configure_port_mode(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 1, 0),
                call(MODULE_POSITION, PARAMETER_ID, 2, 0),
                call(MODULE_POSITION, PARAMETER_ID, 3, 0),
            ]
        )

    def test_configure_port_mode_all_channels(self):
        """Test configure_port_mode and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20071  # pylint: disable=invalid-name
        cpxap4iol.configure_port_mode(97)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, 97),
                call(MODULE_POSITION, PARAMETER_ID, 1, 97),
                call(MODULE_POSITION, PARAMETER_ID, 2, 97),
                call(MODULE_POSITION, PARAMETER_ID, 3, 97),
            ]
        )

    @pytest.mark.parametrize("input_value", [-1, 4])
    def test_configure_port_mode_raise_error(self, input_value):
        """Test configure_port_mode and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4iol.configure_port_mode(input_value, 0)

    @pytest.mark.parametrize(
        "input_value, expected_value", [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    )
    def test_configure_review_and_backup_single_channel(
        self, input_value, expected_value
    ):
        """Test configure_review_and_backup and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20072  # pylint: disable=invalid-name
        cpxap4iol.configure_review_and_backup(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    def test_configure_review_and_backup_more_channels(self):
        """Test configure_review_and_backup and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20072  # pylint: disable=invalid-name
        cpxap4iol.configure_review_and_backup(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 1, 0),
                call(MODULE_POSITION, PARAMETER_ID, 2, 0),
                call(MODULE_POSITION, PARAMETER_ID, 3, 0),
            ]
        )

    def test_configure_review_and_backup_all_channels(self):
        """Test configure_review_and_backup and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20072  # pylint: disable=invalid-name
        cpxap4iol.configure_review_and_backup(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, 4),
                call(MODULE_POSITION, PARAMETER_ID, 1, 4),
                call(MODULE_POSITION, PARAMETER_ID, 2, 4),
                call(MODULE_POSITION, PARAMETER_ID, 3, 4),
            ]
        )

    @pytest.mark.parametrize("input_value", [-1, 5])
    def test_configure_review_and_backup_raise_error(self, input_value):
        """Test configure_review_and_backup and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxap4iol.configure_review_and_backup(input_value, 0)

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (10, 10)])
    def test_configure_target_vendor_id_single_channel(
        self, input_value, expected_value
    ):
        """Test configure_target_vendor_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20073  # pylint: disable=invalid-name
        cpxap4iol.configure_target_vendor_id(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    def test_configure_target_vendor_id_more_channels(self):
        """Test configure_target_vendor_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20073  # pylint: disable=invalid-name
        cpxap4iol.configure_target_vendor_id(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 1, 0),
                call(MODULE_POSITION, PARAMETER_ID, 2, 0),
                call(MODULE_POSITION, PARAMETER_ID, 3, 0),
            ]
        )

    def test_configure_target_vendor_id_all_channels(self):
        """Test configure_target_vendor_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20073  # pylint: disable=invalid-name
        cpxap4iol.configure_target_vendor_id(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, 4),
                call(MODULE_POSITION, PARAMETER_ID, 1, 4),
                call(MODULE_POSITION, PARAMETER_ID, 2, 4),
                call(MODULE_POSITION, PARAMETER_ID, 3, 4),
            ]
        )

    @pytest.mark.parametrize("input_value, expected_value", [(0, 0), (10, 10)])
    def test_configure_setpoint_device_id_single_channel(
        self, input_value, expected_value
    ):
        """Test configure_setpoint_device_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20080  # pylint: disable=invalid-name
        cpxap4iol.configure_setpoint_device_id(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, PARAMETER_ID, 0, expected_value
        )

    def testconfigure_setpoint_device_id_more_channels(self):
        """Test configure_setpoint_device_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20080  # pylint: disable=invalid-name
        cpxap4iol.configure_setpoint_device_id(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 1, 0),
                call(MODULE_POSITION, PARAMETER_ID, 2, 0),
                call(MODULE_POSITION, PARAMETER_ID, 3, 0),
            ]
        )

    def test_configure_setpoint_device_id_all_channels(self):
        """Test configure_setpoint_device_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        PARAMETER_ID = 20080  # pylint: disable=invalid-name
        cpxap4iol.configure_setpoint_device_id(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, PARAMETER_ID, 0, 4),
                call(MODULE_POSITION, PARAMETER_ID, 1, 4),
                call(MODULE_POSITION, PARAMETER_ID, 2, 4),
                call(MODULE_POSITION, PARAMETER_ID, 3, 4),
            ]
        )

    def test_read_fieldbus_parameters_all_channels(self):
        """Test read_fieldbus_parameters"""
        # Arange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock(read_parameter=Mock())
        cpxap4iol.base.read_parameter.side_effect = [
            [0xCAFE],
            [0xCAFE],
            [0xCA02],
            [0xCAFE],
            [0xCAFE],
            [0xDEAD, 0xBEEF],
            [0xDEAD],
            [0xBEEF],
        ] * 4
        cpxap4iol.input_register = 0
        expected = {
            "Port status information": "PORT_POWER_OFF",
            "Revision ID": 0xFE,
            "Transmission rate": "COM2",
            "Actual cycle time [in 100 us]": 0xCAFE,
            "Actual vendor ID": 0xCAFE,
            "Actual device ID": 0xBEEFDEAD,
            "Input data length": 0xAD,
            "Output data length": 0xEF,
        }

        # Act
        params = cpxap4iol.read_fieldbus_parameters()

        # Assert
        assert all(p == expected for p in params)

    @pytest.mark.parametrize("input_value", [0, 1, 10])
    def test_read_isdu(self, input_value):
        """Test read_isdu"""
        # Arange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        ISDU_STATUS = (34000, 1)  # pylint: disable=invalid-name
        ISDU_COMMAND = (34001, 1)  # pylint: disable=invalid-name
        ISDU_MODULE_NO = (34002, 1)  # pylint: disable=invalid-name
        ISDU_CHANNEL = (34003, 1)  # pylint: disable=invalid-name
        ISDU_INDEX = (34004, 1)  # pylint: disable=invalid-name
        ISDU_SUBINDEX = (34005, 1)  # pylint: disable=invalid-name
        ISDU_LENGTH = (34006, 1)  # pylint: disable=invalid-name
        ISDU_DATA = (34007, 119)  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_reg_data=Mock())
        cpxap4iol.base.read_reg_data = Mock(return_value=[0])

        # Act
        isdu = cpxap4iol.read_isdu(input_value, input_value, input_value)

        # Assert
        cpxap4iol.base.write_reg_data.assert_has_calls(
            [
                call(MODULE_POSITION + 1, *ISDU_MODULE_NO),
                call(input_value + 1, *ISDU_CHANNEL),
                call(input_value, *ISDU_INDEX),
                call(input_value, *ISDU_SUBINDEX),
                call(0, *ISDU_LENGTH),
                call(100, *ISDU_COMMAND),
            ]
        )
        cpxap4iol.base.read_reg_data.assert_has_calls(
            [
                call(*ISDU_STATUS),
                call(*ISDU_DATA),
            ]
        )
        assert isdu == [0]

    @pytest.mark.parametrize("input_value", [0, 1, 10])
    def test_write_isdu(self, input_value):
        """Test write_isdu"""
        # Arange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        ISDU_STATUS = (34000, 1)  # pylint: disable=invalid-name
        ISDU_COMMAND = (34001, 1)  # pylint: disable=invalid-name
        ISDU_MODULE_NO = (34002, 1)  # pylint: disable=invalid-name
        ISDU_CHANNEL = (34003, 1)  # pylint: disable=invalid-name
        ISDU_INDEX = (34004, 1)  # pylint: disable=invalid-name
        ISDU_SUBINDEX = (34005, 1)  # pylint: disable=invalid-name
        ISDU_LENGTH = (34006, 1)  # pylint: disable=invalid-name
        ISDU_DATA = (34007, 119)  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_reg_data=Mock())
        cpxap4iol.base.read_reg_data = Mock(return_value=[0])

        # Act
        data = [1, 2, 3]
        cpxap4iol.write_isdu(data, input_value, input_value, input_value)

        # Assert
        cpxap4iol.base.write_reg_data.assert_has_calls(
            [
                call(MODULE_POSITION + 1, *ISDU_MODULE_NO),
                call(input_value + 1, *ISDU_CHANNEL),
                call(input_value, *ISDU_INDEX),
                call(input_value, *ISDU_SUBINDEX),
                call(len(data) * 2, *ISDU_LENGTH),
                call(data, *ISDU_DATA),
                call(101, *ISDU_COMMAND),
            ]
        )
        cpxap4iol.base.read_reg_data.assert_has_calls(
            [
                call(*ISDU_STATUS),
            ]
        )
