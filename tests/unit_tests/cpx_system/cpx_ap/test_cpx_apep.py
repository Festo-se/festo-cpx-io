"""Contains tests for CpxApEp class"""

from unittest.mock import Mock
import pytest

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import LoadSupply


class TestCpxApEp:
    "Test CpxApEp"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        cpxapep = CpxApEp()

        # Assert
        assert isinstance(cpxapep, CpxApEp)

    def test_configure(self):
        """Test configure"""
        # Arrange
        cpxapep = CpxApEp()
        base = Mock()

        # Act
        cpxapep.configure(base, 0)
        # Assert
        assert cpxapep.base == base
        assert cpxapep.position == 0
        assert cpxapep.output_register is None
        assert cpxapep.input_register is None

        assert cpxapep.base.next_output_register == 0
        assert cpxapep.base.next_input_register == 5000

    def test_read_parameters(self):
        """Test read_parameters"""
        # Arrange
        cpxapep = CpxApEp()

        MODULE_POSITION = 0  # pylint: disable=invalid-name

        cpxapep.position = MODULE_POSITION

        cpxapep.base = Mock(read_parameter=Mock())
        cpxapep.base.read_parameter.side_effect = [
            True,
            0xC0A80101,
            0xFFFFFF00,
            0xC0A80100,
            0xC0A80102,
            0xFFFFFF00,
            0xC0A80103,
            [0xDE, 0xAD, 0xC0, 0xFF, 0xEE, 0x00],
            0xFF03,
        ]

        expected = CpxApEp.Parameters(
            dhcp_enable=True,
            ip_address="192.168.1.1",
            subnet_mask="255.255.255.0",
            gateway_address="192.168.1.0",
            active_ip_address="192.168.1.2",
            active_subnet_mask="255.255.255.0",
            active_gateway_address="192.168.1.3",
            mac_address="de:ad:c0:ff:ee:00",
            setup_monitoring_load_supply=3,
        )

        # Act
        params = cpxapep.read_parameters()

        # Assert
        assert params == expected

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
        MODULE_POSITION = 0  # pylint: disable=invalid-name

        cpxapep = CpxApEp()
        cpxapep.position = MODULE_POSITION

        cpxapep.base = Mock(write_parameter=Mock())

        # Act
        cpxapep.configure_monitoring_load_supply(input_value)

        # Assert
        cpxapep.base.write_parameter.assert_called_with(
            MODULE_POSITION, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP, expected_value
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 0  # pylint: disable=invalid-name

        cpxapep = CpxApEp()
        cpxapep.position = MODULE_POSITION

        cpxapep.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            cpxapep.configure_monitoring_load_supply(input_value)
