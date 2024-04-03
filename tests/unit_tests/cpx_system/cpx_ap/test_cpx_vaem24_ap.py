"""Contains tests for VaemAP class"""

from unittest.mock import Mock, call
import struct
import pytest

from cpx_io.cpx_system.cpx_ap.vaem_ap import VaemAP
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.cpx_system.cpx_ap.ap_enums import LoadSupply, FailState


class TestVaemAP24:
    "Test VaemAP"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        vaem_ap = VaemAP()

        # Assert
        assert isinstance(vaem_ap, VaemAP)

    def test_read_channels_correct_values(self):
        """Test read 24 channels"""
        # Arrange
        vaem_ap = VaemAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vaem_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        channel_values = vaem_ap.read_channels()

        # Assert
        assert channel_values == [
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
        ]

    def test_read_channel_correct_values(self):
        """Test read one of 24 channels"""
        # Arrange
        vaem_ap = VaemAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vaem_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        channel_values = [vaem_ap.read_channel(idx) for idx in range(24)]

        # Assert
        assert channel_values == [
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
        ]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        vaem_ap = VaemAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vaem_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        channel_values = [vaem_ap[idx] for idx in range(24)]

        # Assert
        assert channel_values == [
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
        ]

    def test_write_channels_correct_values(self):
        """Test write channels"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.output_register = 0
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        bool_list = [
            True,
            False,
            True,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
        ]

        vaem_ap.write_channels(bool_list)

        # Assert
        vaem_ap.base.write_reg_data.assert_called_with(b"\xad\xde\xef", 0)

    def test_write_channels_too_long(self):
        """Test write channels, expect error"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act and assert
        with pytest.raises(ValueError):
            vaem_ap.write_channels([0] * 25)

    def test_write_channels_too_short(self):
        """Test write channels, expect error"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act and assert
        with pytest.raises(ValueError):
            vaem_ap.write_channels([0] * 23)

    def test_write_channels_wrong_type(self):
        """Test write channels, expect error"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(TypeError):
            vaem_ap.write_channels(0)

    def test_write_channel_true(self):
        """Test write channel"""
        # Arange
        vaem_ap = VaemAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)
        vaem_ap.output_register = 0

        # Act
        vaem_ap.write_channel(0, False)

        # Assert
        # exected is DEAC BEEF
        vaem_ap.base.write_reg_data.assert_called_with(b"\xac\xde\xef\xbe", 0)

    def test_write_channel_false(self):
        """Test write channel"""
        # Arange
        vaem_ap = VaemAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vaem_ap.output_register = 0
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        vaem_ap.write_channel(1, True)

        # Assert
        # exected is DEAF BEEF
        vaem_ap.base.write_reg_data.assert_called_with(b"\xaf\xde\xef\xbe", 0)

    @pytest.mark.parametrize("input_value", [-1, 24])
    def test_write_wrong_channel(self, input_value):
        """Test write channel"""
        # Arange
        vaem_ap = VaemAP()
        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act & Assert
        with pytest.raises(ValueError):
            vaem_ap.write_channel(input_value, True)

    def test_set_item(self):
        """Test set item"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock()
        vaem_ap.write_channel = Mock()

        # Act
        vaem_ap[0] = True
        vaem_ap[1] = False
        vaem_ap[2] = True
        vaem_ap[3] = False
        vaem_ap[4] = True
        vaem_ap[5] = False
        vaem_ap[6] = True
        vaem_ap[7] = False
        vaem_ap[8] = True
        vaem_ap[9] = False
        vaem_ap[20] = True
        vaem_ap[21] = False
        vaem_ap[22] = True
        vaem_ap[23] = False

        # Assert
        vaem_ap.write_channel.assert_has_calls(
            [
                call(0, True),
                call(1, False),
                call(2, True),
                call(3, False),
                call(4, True),
                call(5, False),
                call(6, True),
                call(7, False),
                call(8, True),
                call(9, False),
                call(20, True),
                call(21, False),
                call(22, True),
                call(23, False),
            ]
        )

    def test_set_channel(self):
        """Test set channel"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.write_channel = Mock()

        # Act
        vaem_ap.set_channel(0)

        # Assert
        vaem_ap.write_channel.assert_called_with(0, True)

    def test_clear_channel(self):
        """Test clear channel"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.write_channel = Mock()

        # Act
        vaem_ap.clear_channel(0)

        # Assert
        vaem_ap.write_channel.assert_called_with(0, False)

    def test_toggle_channel(self):
        """Test toggle channel"""
        # Arange
        vaem_ap = VaemAP()

        vaem_ap.base = Mock(write_reg_data=Mock())
        vaem_ap.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        vaem_ap.write_channel = Mock()
        vaem_ap.information = CpxAp.ModuleInformation(output_channels=24, output_size=3)

        # Act
        vaem_ap.toggle_channel(0)

        # Assert
        vaem_ap.write_channel.assert_called_with(0, True)

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

        vaem_ap = VaemAP()
        vaem_ap.position = MODULE_POSITION

        vaem_ap.base = Mock(write_parameter=Mock())

        # Act
        vaem_ap.configure_monitoring_load_supply(input_value)

        # Assert
        vaem_ap.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["LoadSupplyDiagSetup"],
            expected_value,
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vaem_ap = VaemAP()
        vaem_ap.position = MODULE_POSITION

        vaem_ap.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            vaem_ap.configure_monitoring_load_supply(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(0, 0), (1, 1), (FailState.RESET_OUTPUTS, 0), (FailState.HOLD_LAST_STATE, 1)],
    )
    def test_configure_behaviour_in_fail_state(self, input_value, expected_value):
        """Test configure_behaviour_in_fail_state and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vaem_ap = VaemAP()
        vaem_ap.position = MODULE_POSITION

        vaem_ap.base = Mock(write_parameter=Mock())

        # Act
        vaem_ap.configure_behaviour_in_fail_state(input_value)

        # Assert
        vaem_ap.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["FailStateBehaviour"],
            expected_value,
        )

    @pytest.mark.parametrize("input_value", [-1, 2])
    def test_configure_behaviour_in_fail_state_raise_error(self, input_value):
        """Test configure_behaviour_in_fail_state and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vaem_ap = VaemAP()
        vaem_ap.position = MODULE_POSITION

        vaem_ap.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            vaem_ap.configure_behaviour_in_fail_state(input_value)
