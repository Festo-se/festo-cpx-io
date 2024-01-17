"""Contains tests for CpxApEp class"""
from unittest.mock import Mock, call

from cpx_io.cpx_system.cpx_ap.apep import CpxApEp


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
            [0x0100],
            [0xA8C0, 0x0101],
            [0xFFFF, 0x0000],
            [0xA8C0, 0x0001],
            [0xA8C0, 0x0201],
            [0xFFFF, 0x00FF],
            [0xA8C0, 0x0301],
            [0xADDE, 0xFFC0, 0xBAEE],
            [0xFF03],
        ]

        expected = CpxApEp.Parameters(
            dhcp_enable=True,
            ip_address="192.168.1.1",
            subnet_mask="255.255.0.0",
            gateway_address="192.168.1.0",
            active_ip_address="192.168.1.2",
            active_subnet_mask="255.255.255.0",
            active_gateway_address="192.168.1.3",
            mac_address="de:ad:c0:ff:ee:ba",
            setup_monitoring_load_supply=3,
        )

        # Act
        params = cpxapep.read_parameters()

        # Assert
        assert params == expected

    def test_write_parameters(self):
        """Test write_parameters"""
        # Arrange
        cpxapep = CpxApEp()

        MODULE_POSITION = 0  # pylint: disable=invalid-name

        cpxapep.position = MODULE_POSITION

        cpxapep.base = Mock(write_parameter=Mock())

        param = CpxApEp.Parameters(
            dhcp_enable=True,
            ip_address="192.168.1.1",
            subnet_mask="255.255.0.0",
            gateway_address="192.168.1.0",
            setup_monitoring_load_supply=3,
        )

        # Act
        cpxapep.write_parameters(param)

        # Assert
        cpxapep.base.write_parameter.assert_has_calls(
            [
                call(cpxapep.position, 12000, 0, True),
                call(cpxapep.position, 12001, 0, [0xC0, 0xA8, 0x01, 0x01]),
                call(cpxapep.position, 12002, 0, [0xFF, 0xFF, 0x00, 0x00]),
                call(cpxapep.position, 12003, 0, [0xC0, 0xA8, 0x01, 0x00]),
                call(cpxapep.position, 20022, 0, 3),
            ]
        )
