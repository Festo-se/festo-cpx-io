"""Contains tests for CpxAp4Iol class"""

from unittest.mock import Mock, call, patch
import pytest

from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import (
    LoadSupply,
    CycleTime,
    PortMode,
    ReviewBackup,
)


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
        return_value=CpxApModule.ModuleParameters(
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

        cpxap4iol.base = Mock()
        cpxap4iol.base.read_parameter.side_effect = [8201, False]

        # Act
        params = cpxap4iol.read_ap_parameter()

        # Assert
        mock_read_ap_parameter.assert_called_once()
        cpxap4iol.base.read_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, ParameterNameMap()["VariantSwitch"]),
                call(MODULE_POSITION, ParameterNameMap()["SensorSupplyEnable"]),
            ],
            any_order=True,
        )
        assert params.io_link_variant == "CPX-AP-I-4IOL-M12 variant 8"
        assert params.operating_supply is False

    def test_read_channels_correct_values_4byte(self):
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
        cpxap4iol.base = Mock(
            read_reg_data=Mock(
                return_value=b"\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00"
            )
        )

        # Act
        channel_values = cpxap4iol.read_channels()

        # Assert
        # values are in byteorder: little
        assert channel_values == [
            b"\x00\x00\x00\x00",
            b"\x01\x00\x00\x00",
            b"\x02\x00\x00\x00",
            b"\x03\x00\x00\x00",
        ]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.read_channel = Mock(return_value=b"\xAD\xDE\xEF\xBE")
        # Act
        channel_values = [cpxap4iol[idx] for idx in range(4)]

        # Assert
        assert channel_values == [b"\xAD\xDE\xEF\xBE"] * 4

    def test_read_channel_correct_value(self):
        """Test read_channel"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.read_channels = Mock(
            return_value=[
                b"\x4D\xDE\xEF\xBE",
                b"\x4D\xDE\xEF\xBE",
                b"\x4D\xDE\xEF\xBE",
                b"\x4D\xDE\xEF\xBE",
            ]
        )
        cpxap4iol.fieldbus_parameters = [
            {"Input data length": 1},
            {"Input data length": 2},
            {"Input data length": 3},
            {"Input data length": 4},
        ]
        # Act
        channel_values = [cpxap4iol.read_channel(idx) for idx in range(4)]

        # Assert
        assert channel_values == [
            b"\x4D",
            b"\x4D\xDE",
            b"\x4D\xDE\xEF",
            b"\x4D\xDE\xEF\xBE",
        ]

    def test_read_channel_correct_value_full_size(self):
        """Test read_channel"""
        # Arrange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock()
        cpxap4iol.read_channels = Mock(
            return_value=[
                b"\x1D\xDE\xEF\xBE",
                b"\x2D\xDE\xEF\xBE",
                b"\x3D\xDE\xEF\xBE",
                b"\x4D\xDE\xEF\xBE",
            ]
        )
        # Act
        channel_values = [cpxap4iol.read_channel(idx, True) for idx in range(4)]

        # Assert
        assert channel_values == [
            b"\x1D\xDE\xEF\xBE",
            b"\x2D\xDE\xEF\xBE",
            b"\x3D\xDE\xEF\xBE",
            b"\x4D\xDE\xEF\xBE",
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

        # Act
        cpxap4iol.write_channel(channel_number, b"\x00\x01\x02\x03")

        # Assert
        cpxap4iol.base.write_reg_data.assert_called_with(
            b"\x00\x01\x02\x03", cpxap4iol.output_register + 2 * channel_number
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

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (LoadSupply.INACTIVE, 0),
            (LoadSupply.ACTIVE_DIAG_OFF, 1),
            (LoadSupply.ACTIVE, 2),
        ],
    )
    def test_configure_monitoring_load_supply(self, input_value, expected_value):
        """Test configure_monitoring_load_supply and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_monitoring_load_supply(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, ParameterNameMap()["LoadSupplyDiagSetup"], expected_value
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
        "input_value, expected_value",
        [
            (0, 0),
            (16, 16),
            (183, 183),
            (CycleTime.FAST, 0),
            (CycleTime.T_1600US, 16),
            (CycleTime.T_120MS, 183),
        ],
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
        cpxap4iol.configure_target_cycle_time(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["NominalCycleTime"],
                    expected_value,
                    0,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["NominalCycleTime"],
                    expected_value,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["NominalCycleTime"],
                    expected_value,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["NominalCycleTime"],
                    expected_value,
                    3,
                ),
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
        cpxap4iol.configure_target_cycle_time(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, ParameterNameMap()["NominalCycleTime"], expected_value, 0
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
        cpxap4iol.configure_device_lost_diagnostics(input_value)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["DeviceLostDiagnosisEnable"],
                    expected_value,
                    0,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["DeviceLostDiagnosisEnable"],
                    expected_value,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["DeviceLostDiagnosisEnable"],
                    expected_value,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["DeviceLostDiagnosisEnable"],
                    expected_value,
                    3,
                ),
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
        cpxap4iol.configure_device_lost_diagnostics(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["DeviceLostDiagnosisEnable"],
            expected_value,
            0,
        )

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (97, 97),
            (PortMode.DEACTIVATED, 0),
            (PortMode.IOL_MANUAL, 1),
            (PortMode.IOL_AUTOSTART, 2),
            (PortMode.DI_CQ, 3),
            (PortMode.PREOPERATE, 97),
        ],
    )
    def test_configure_port_mode_single_channel(self, input_value, expected_value):
        """Test configure_port_mode and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_port_mode(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["PortMode"],
            expected_value,
            0,
        )

    def test_configure_port_mode_more_channels(self):
        """Test configure_port_mode and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_port_mode(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    0,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    0,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    0,
                    3,
                ),
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
        cpxap4iol.configure_port_mode(97)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    97,
                    0,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    97,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    97,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["PortMode"],
                    97,
                    3,
                ),
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
        "input_value, expected_value",
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (ReviewBackup.NO_TEST, 0),
            (ReviewBackup.COMPATIBLE_V1_0, 1),
            (ReviewBackup.COMPATIBLE_V1_1, 2),
            (ReviewBackup.COMPATIBLE_V1_1_DATA_BACKUP_RESTORE, 3),
            (ReviewBackup.COMPATIBLE_V1_1_DATE_RESTORE, 4),
        ],
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
        cpxap4iol.configure_review_and_backup(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["ValidationAndBackup"],
            expected_value,
            0,
        )

    def test_configure_review_and_backup_more_channels(self):
        """Test configure_review_and_backup and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_review_and_backup(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    0,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    0,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    0,
                    3,
                ),
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
        cpxap4iol.configure_review_and_backup(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    4,
                    0,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    4,
                    1,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    4,
                    2,
                ),
                call(
                    MODULE_POSITION,
                    ParameterNameMap()["ValidationAndBackup"],
                    4,
                    3,
                ),
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
        cpxap4iol.configure_target_vendor_id(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, ParameterNameMap()["NominalVendorID"], expected_value, 0
        )

    def test_configure_target_vendor_id_more_channels(self):
        """Test configure_target_vendor_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_target_vendor_id(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 0, 1),
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 0, 2),
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 0, 3),
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
        cpxap4iol.configure_target_vendor_id(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 4, 0),
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 4, 1),
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 4, 2),
                call(MODULE_POSITION, ParameterNameMap()["NominalVendorID"], 4, 3),
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
        cpxap4iol.configure_setpoint_device_id(input_value, 0)

        # Assert
        cpxap4iol.base.write_parameter.assert_called_with(
            MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], expected_value, 0
        )

    def testconfigure_setpoint_device_id_more_channels(self):
        """Test configure_setpoint_device_id and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_parameter=Mock())

        # Act
        cpxap4iol.configure_setpoint_device_id(0, [1, 2, 3])

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 0, 1),
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 0, 2),
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 0, 3),
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
        cpxap4iol.configure_setpoint_device_id(4)

        # Assert
        cpxap4iol.base.write_parameter.assert_has_calls(
            [
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 4, 0),
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 4, 1),
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 4, 2),
                call(MODULE_POSITION, ParameterNameMap()["NominalDeviceID"], 4, 3),
            ]
        )

    def test_read_fieldbus_parameters_all_channels(self):
        """Test read_fieldbus_parameters"""
        # Arange
        cpxap4iol = CpxAp4Iol()

        cpxap4iol.base = Mock(read_parameter=Mock())
        cpxap4iol.base.read_parameter.side_effect = [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
        ] * 4
        cpxap4iol.input_register = 0
        expected = {
            "Port status information": "DEACTIVATED",
            "Revision ID": 2,
            "Transmission rate": "COM3",
            "Actual cycle time [in 100 us]": 4,
            "Actual vendor ID": 5,
            "Actual device ID": 6,
            "Input data length": 7,
            "Output data length": 8,
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

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_reg_data=Mock())
        cpxap4iol.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        isdu = cpxap4iol.read_isdu(input_value, input_value, input_value)

        # Assert
        cpxap4iol.base.write_reg_data.assert_has_calls(
            [
                call(
                    (MODULE_POSITION + 1).to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_MODULE_NO.register_address,
                ),
                call(
                    (input_value + 1).to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_CHANNEL.register_address,
                ),
                call(
                    input_value.to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_INDEX.register_address,
                ),
                call(
                    input_value.to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_SUBINDEX.register_address,
                ),
                call(b"\x00\x00", cpx_ap_registers.ISDU_LENGTH.register_address),
                call(b"\x64\x00", cpx_ap_registers.ISDU_COMMAND.register_address),
            ]
        )
        cpxap4iol.base.read_reg_data.assert_has_calls(
            [
                call(*cpx_ap_registers.ISDU_STATUS),
                call(*cpx_ap_registers.ISDU_DATA),
            ]
        )
        assert isdu == b"\x00\x00"

    @pytest.mark.parametrize("input_value", [0, 1, 10])
    def test_write_isdu(self, input_value):
        """Test write_isdu"""
        # Arange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        cpxap4iol = CpxAp4Iol()
        cpxap4iol.position = MODULE_POSITION

        cpxap4iol.base = Mock(write_reg_data=Mock())
        cpxap4iol.base.read_reg_data = Mock(return_value=b"\x00\x00")

        # Act
        data = b"\x01\x02\x03\x04"
        cpxap4iol.write_isdu(data, input_value, input_value, input_value)

        # Assert
        cpxap4iol.base.write_reg_data.assert_has_calls(
            [
                call(
                    (MODULE_POSITION + 1).to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_MODULE_NO.register_address,
                ),
                call(
                    (input_value + 1).to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_CHANNEL.register_address,
                ),
                call(
                    input_value.to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_INDEX.register_address,
                ),
                call(
                    input_value.to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_SUBINDEX.register_address,
                ),
                call(
                    len(data * 2).to_bytes(2, byteorder="little"),
                    cpx_ap_registers.ISDU_LENGTH.register_address,
                ),
                call(
                    data,
                    cpx_ap_registers.ISDU_DATA.register_address,
                ),
                call(b"\x65\x00", cpx_ap_registers.ISDU_COMMAND.register_address),
            ]
        )
        cpxap4iol.base.read_reg_data.assert_has_calls(
            [
                call(*cpx_ap_registers.ISDU_STATUS),
            ]
        )
