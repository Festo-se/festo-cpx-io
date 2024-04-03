"""Contains tests for VabxAP class"""

from unittest.mock import Mock, call
import struct
import pytest

from cpx_io.cpx_system.cpx_ap.vabx_ap import VabxAP
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.cpx_system.cpx_ap.ap_enums import LoadSupply, FailState


class TestVabxAP:
    "Test VabxAP"

    def test_constructor_correct_type(self):
        """Test constructor"""
        # Arrange

        # Act
        vabx_ap = VabxAP()

        # Assert
        assert isinstance(vabx_ap, VabxAP)

    def test_read_channels_correct_values(self):
        """Test read channels"""
        # Arrange
        vabx_ap = VabxAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vabx_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = vabx_ap.read_channels()

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
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
        ]

    def test_read_channel_correct_values(self):
        """Test read channel"""
        # Arrange
        vabx_ap = VabxAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vabx_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [vabx_ap.read_channel(idx) for idx in range(32)]

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
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
        ]

    def test_get_item_correct_values(self):
        """Test get item"""
        # Arrange
        vabx_ap = VabxAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vabx_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))

        # Act
        channel_values = [vabx_ap[idx] for idx in range(32)]

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
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
        ]

    def test_write_channels_correct_values(self):
        """Test write channels"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.output_register = 0

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
            False,
            True,
            True,
            True,
            True,
            True,
            False,
            True,
        ]

        vabx_ap.write_channels(bool_list)

        # Assert
        vabx_ap.base.write_reg_data.assert_called_with(b"\xad\xde\xef\xbe", 0)

    def test_write_channels_too_long(self):
        """Test write channels, expect error"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(ValueError):
            vabx_ap.write_channels([0] * 33)

    def test_write_channels_too_short(self):
        """Test write channels, expect error"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(ValueError):
            vabx_ap.write_channels([0] * 31)

    def test_write_channels_wrong_type(self):
        """Test write channels, expect error"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())

        # Act and assert
        with pytest.raises(TypeError):
            vabx_ap.write_channels(0)

    def test_write_channel_true(self):
        """Test write channel"""
        # Arange
        vabx_ap = VabxAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vabx_ap.output_register = 0

        # Act
        vabx_ap.write_channel(0, False)

        # Assert
        # exected is DEAC BEEF
        vabx_ap.base.write_reg_data.assert_called_with(b"\xac\xde\xef\xbe", 0)

    def test_write_channel_false(self):
        """Test write channel"""
        # Arange
        vabx_ap = VabxAP()
        ret_data = struct.pack("<HH", *[0xDEAD, 0xBEEF])

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.base = Mock(read_reg_data=Mock(return_value=ret_data))
        vabx_ap.output_register = 0

        # Act
        vabx_ap.write_channel(1, True)

        # Assert
        # exected is DEAF BEEF
        vabx_ap.base.write_reg_data.assert_called_with(b"\xaf\xde\xef\xbe", 0)

    @pytest.mark.parametrize("input_value", [-1, 32])
    def test_write_wrong_channel(self, input_value):
        """Test write channel"""
        # Arange
        vabx_ap = VabxAP()
        vabx_ap.base = Mock(write_reg_data=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            vabx_ap.write_channel(input_value, True)

    def test_set_item(self):
        """Test set item"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock()
        vabx_ap.write_channel = Mock()

        # Act
        vabx_ap[0] = True
        vabx_ap[1] = False
        vabx_ap[2] = True
        vabx_ap[3] = False
        vabx_ap[4] = True
        vabx_ap[5] = False
        vabx_ap[6] = True
        vabx_ap[7] = False
        vabx_ap[8] = True
        vabx_ap[9] = False
        vabx_ap[28] = True
        vabx_ap[29] = False
        vabx_ap[30] = True
        vabx_ap[31] = False

        # Assert
        vabx_ap.write_channel.assert_has_calls(
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
                call(28, True),
                call(29, False),
                call(30, True),
                call(31, False),
            ]
        )

    def test_set_channel(self):
        """Test set channel"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.write_channel = Mock()

        # Act
        vabx_ap.set_channel(0)

        # Assert
        vabx_ap.write_channel.assert_called_with(0, True)

    def test_clear_channel(self):
        """Test clear channel"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.write_channel = Mock()

        # Act
        vabx_ap.clear_channel(0)

        # Assert
        vabx_ap.write_channel.assert_called_with(0, False)

    def test_toggle_channel(self):
        """Test toggle channel"""
        # Arange
        vabx_ap = VabxAP()

        vabx_ap.base = Mock(write_reg_data=Mock())
        vabx_ap.base = Mock(read_reg_data=Mock(return_value=[0xBA]))
        vabx_ap.write_channel = Mock()

        # Act
        vabx_ap.toggle_channel(0)

        # Assert
        vabx_ap.write_channel.assert_called_with(0, True)

    @pytest.mark.parametrize(
        "input_value, expected_value", [(True, True), (False, False)]
    )
    def test_configure_diagnosis_for_defect_valve(self, input_value, expected_value):
        """Test configure_diagnosis_for_defect_valve and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vabx_ap = VabxAP()
        vabx_ap.position = MODULE_POSITION

        vabx_ap.base = Mock(write_parameter=Mock())

        # Act
        vabx_ap.configure_diagnosis_for_defect_valve(input_value)

        # Assert
        vabx_ap.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["ValveDefectDiagEnable"],
            expected_value,
        )

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

        vabx_ap = VabxAP()
        vabx_ap.position = MODULE_POSITION

        vabx_ap.base = Mock(write_parameter=Mock())

        # Act
        vabx_ap.configure_monitoring_load_supply(input_value)

        # Assert
        vabx_ap.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["LoadSupplyDiagSetup"],
            expected_value,
        )

    @pytest.mark.parametrize("input_value", [-1, 3])
    def test_configure_monitoring_load_supply_raise_error(self, input_value):
        """Test configure_monitoring_load_supply and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vabx_ap = VabxAP()
        vabx_ap.position = MODULE_POSITION

        vabx_ap.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            vabx_ap.configure_monitoring_load_supply(input_value)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [(0, 0), (1, 1), (FailState.RESET_OUTPUTS, 0), (FailState.HOLD_LAST_STATE, 1)],
    )
    def test_configure_behaviour_in_fail_state(self, input_value, expected_value):
        """Test configure_behaviour_in_fail_state and expect success"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vabx_ap = VabxAP()
        vabx_ap.position = MODULE_POSITION

        vabx_ap.base = Mock(write_parameter=Mock())

        # Act
        vabx_ap.configure_behaviour_in_fail_state(input_value)

        # Assert
        vabx_ap.base.write_parameter.assert_called_with(
            MODULE_POSITION,
            ParameterNameMap()["FailStateBehaviour"],
            expected_value,
        )

    @pytest.mark.parametrize("input_value", [-1, 2])
    def test_configure_behaviour_in_fail_state_raise_error(self, input_value):
        """Test configure_behaviour_in_fail_state and expect error"""
        # Arrange
        MODULE_POSITION = 1  # pylint: disable=invalid-name

        vabx_ap = VabxAP()
        vabx_ap.position = MODULE_POSITION

        vabx_ap.base = Mock(write_parameter=Mock())

        # Act & Assert
        with pytest.raises(ValueError):
            vabx_ap.configure_behaviour_in_fail_state(input_value)
