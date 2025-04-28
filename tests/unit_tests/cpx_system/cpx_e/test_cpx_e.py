"""Contains tests for CpxE class"""

from unittest.mock import Mock, patch, call
import pytest
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI

from cpx_io.cpx_system.cpx_e.cpx_e import CpxInitError
import cpx_io.cpx_system.cpx_e.cpx_e_modbus_registers as cpx_e_modbus_registers

from cpx_io.utils.logging import Logging


class TestCpxE:
    """Test for CpxE"""

    def test_default_constructor(self):
        """Test default constructor"""
        # Arrange

        # Act
        cpx_e = CpxE()

        # Assert
        assert len(cpx_e.modules) == 1
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.cpxeep, CpxEEp)  # pylint: disable="no-member"

    def test_constructor_with_two_modules(self):
        """Test constructor with two modules"""
        # Arrange

        # Act
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        # Assert
        assert len(cpx_e.modules) == 2
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE16Di)
        assert isinstance(cpx_e.cpxeep, CpxEEp)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe16di, CpxE16Di)  # pylint: disable="no-member"

    def test_rename_module_reflected_in_base(self):
        """Test constructor with two modules"""
        # Arrange
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        # Act
        cpx_e.cpxe16di.name = "my16di"  # pylint: disable="no-member"

        # Assert
        assert isinstance(cpx_e.my16di, CpxE16Di)  # pylint: disable="no-member"

    @patch.object(Logging.logger, "warning")
    def test_constructor_cpxeep_twice(self, mock_logger_warning):
        """Test default constructor with modified modules"""
        # Arrange

        # Act
        cpx_e = CpxE(modules=[CpxEEp(), CpxEEp()])

        # Assert
        assert len(cpx_e.modules) == 2
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxEEp)
        mock_logger_warning.assert_called_with(
            "Module CpxEEp is assigned multiple times. This is most likey incorrect."
        )

    def test_default_constructor_modified_modules(self):
        """Test default constructor with modified modules"""
        # Arrange

        # Act
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        # Assert
        assert len(cpx_e.modules) == 3
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE16Di)
        assert isinstance(cpx_e.modules[2], CpxE8Do)
        assert isinstance(cpx_e.cpxeep, CpxEEp)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe16di, CpxE16Di)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe8do, CpxE8Do)  # pylint: disable="no-member"

    def test_default_constructor_same_module_naming(self):
        """Test default constructor with modified modules"""
        # Arrange

        # Act
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di(), CpxE16Di(), CpxE16Di()])

        # Assert
        assert len(cpx_e.modules) == 4
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE16Di)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE16Di)
        assert isinstance(cpx_e.cpxeep, CpxEEp)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe16di, CpxE16Di)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe16di_1, CpxE16Di)  # pylint: disable="no-member"
        assert isinstance(cpx_e.cpxe16di_2, CpxE16Di)  # pylint: disable="no-member"

    def test_custom_constructor_modified_modules_custom_names(self):
        """Test name access"""
        # Arrange

        # Act
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m3"), CpxE16Di("m1"), CpxE8Do("m2")]

        # Assert
        assert isinstance(cpx_e.m3, CpxEEp)  # pylint: disable="no-member"
        assert isinstance(cpx_e.m1, CpxE16Di)  # pylint: disable="no-member"
        assert isinstance(cpx_e.m2, CpxE8Do)  # pylint: disable="no-member"

    def test_constructor_with_typecode_MLNINO(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-MLNINO")

        # Assert
        assert len(cpx_e.modules) == 5
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE16Di)
        assert isinstance(cpx_e.modules[2], CpxE8Do)
        assert isinstance(cpx_e.modules[3], CpxE4AiUI)
        assert isinstance(cpx_e.modules[4], CpxE4AoUI)

    def test_constructor_with_typecode_NIMNOL(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-NIMNOL")

        # Assert
        assert len(cpx_e.modules) == 5
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE4AiUI)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE4AoUI)
        assert isinstance(cpx_e.modules[4], CpxE8Do)

    def test_constructor_with_typecode_NIMM(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-NIMM")

        # Assert
        assert len(cpx_e.modules) == 4
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE4AiUI)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE16Di)

    def test_constructor_with_typecode_NI3M(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-NI3M")

        # Assert
        assert len(cpx_e.modules) == 5
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE4AiUI)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE16Di)
        assert isinstance(cpx_e.modules[4], CpxE16Di)

    def test_constructor_with_typecode_NI3M4NO(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-NI3M4NO")

        # Assert
        assert len(cpx_e.modules) == 9
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE4AiUI)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE16Di)
        assert isinstance(cpx_e.modules[4], CpxE16Di)
        assert isinstance(cpx_e.modules[5], CpxE4AoUI)
        assert isinstance(cpx_e.modules[6], CpxE4AoUI)
        assert isinstance(cpx_e.modules[7], CpxE4AoUI)
        assert isinstance(cpx_e.modules[8], CpxE4AoUI)

    def test_constructor_with_typecode_NI12M(self):  # pylint: disable="invalid-name"
        """Test constructor with typecode"""
        # Arrange

        # Act
        cpx_e = CpxE("60E-EP-NI12M")

        # Assert
        assert len(cpx_e.modules) == 14
        assert isinstance(cpx_e.modules[0], CpxEEp)
        assert isinstance(cpx_e.modules[1], CpxE4AiUI)
        assert isinstance(cpx_e.modules[2], CpxE16Di)
        assert isinstance(cpx_e.modules[3], CpxE16Di)
        assert isinstance(cpx_e.modules[4], CpxE16Di)
        assert isinstance(cpx_e.modules[5], CpxE16Di)
        assert isinstance(cpx_e.modules[6], CpxE16Di)
        assert isinstance(cpx_e.modules[7], CpxE16Di)
        assert isinstance(cpx_e.modules[8], CpxE16Di)
        assert isinstance(cpx_e.modules[9], CpxE16Di)
        assert isinstance(cpx_e.modules[10], CpxE16Di)
        assert isinstance(cpx_e.modules[11], CpxE16Di)
        assert isinstance(cpx_e.modules[12], CpxE16Di)
        assert isinstance(cpx_e.modules[13], CpxE16Di)

    def test_constructor_with_incorrect_typecode(self):
        """Test constructor with typecode"""
        # Arrange

        # Act & Assert
        with pytest.raises(TypeError):
            CpxE("60E-EC-NIM")

    def test_name_same_type(self):
        """Test name access"""
        # Arrange

        # Act
        cpx_e = CpxE([CpxEEp(), CpxE16Di(), CpxE16Di()])

        # Assert
        assert cpx_e.modules[0].name == "cpxeep"
        assert cpx_e.modules[1].name == "cpxe16di"
        assert cpx_e.modules[2].name == "cpxe16di_1"

    def test_name_same_name(self):
        """Test name access"""
        # Arrange

        # Act
        cpx_e = CpxE([CpxEEp("EP"), CpxE16Di("E16"), CpxE16Di("E16")])

        # Assert
        assert cpx_e.modules[0].name == "EP"
        assert cpx_e.modules[1].name == "E16"
        assert cpx_e.modules[2].name == "E16_1"

    def test_name_rename(self):
        """Test name access"""
        # Arrange
        cpx_e = CpxE([CpxEEp(), CpxE16Di(), CpxE16Di()])

        # Act
        cpx_e.modules[0].name = "EP"
        cpx_e.modules[1].name = "E16"
        cpx_e.modules[2].name = "E16"

        # Assert
        assert cpx_e.modules[0].name == "EP"
        assert cpx_e.modules[1].name == "E16"
        assert cpx_e.modules[2].name == "E16_1"

    def test_name_access_modified_modules_custom_names_removed(self):
        """Test name access"""
        # Arrange

        # Act
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m4"), CpxE16Di("m5"), CpxE8Do("m6")]

        # Assert
        with pytest.raises(AttributeError):
            _ = cpx_e.m1  # pylint: disable=E1101
        with pytest.raises(AttributeError):
            _ = cpx_e.m2  # pylint: disable=E1101
        with pytest.raises(AttributeError):
            _ = cpx_e.m3  # pylint: disable=E1101
        assert isinstance(cpx_e.m4, CpxEEp)  # pylint: disable="no-member"
        assert isinstance(cpx_e.m5, CpxE16Di)  # pylint: disable="no-member"
        assert isinstance(cpx_e.m6, CpxE8Do)  # pylint: disable="no-member"

    def test_modules_setter_error(self):
        """Test module setter with incorrect type"""
        # Arrange

        # Act
        cpx_e = CpxE([CpxEEp(), CpxE16Di(), CpxE8Do()])

        # Assert
        with pytest.raises(CpxInitError):
            cpx_e.modules = 0

    def test_module_count(self):
        """Test module count"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=b"\xaa\xaa\xaa")

        # Act
        module_count = cpx_e.module_count()

        # Assert
        assert module_count == bin(0xAAAAAA)[2:].count("1")
        cpx_e.read_reg_data.assert_called_with(
            *cpx_e_modbus_registers.MODULE_CONFIGURATION
        )

    def test_read_fault_detection(self):
        """Test read fault detection"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=b"\xaa\xbb\xcc")

        # Act
        fault_detection = cpx_e.read_fault_detection()

        # Assert
        assert fault_detection == [x == "1" for x in bin(0xCCBBAA)[2:]][::-1]
        cpx_e.read_reg_data.assert_called_with(*cpx_e_modbus_registers.FAULT_DETECTION)

    @pytest.mark.parametrize(
        "input_value, expected_value",
        [
            (b"\xca\xfe", (True, True)),
            (b"\x00\x00", (False, False)),
            (b"\x00\x88", (True, True)),
            (b"\x00\x77", (False, False)),
        ],
    )
    def test_read_status(self, input_value, expected_value):
        """Test read status"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=input_value)

        # Act
        status = cpx_e.read_status()

        # Assert
        # tuple of bit (11, 15)
        assert status == expected_value
        cpx_e.read_reg_data.assert_called_with(*cpx_e_modbus_registers.STATUS_REGISTER)

    def test_read_device_identification(self):
        """Test read_device_identification"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_function_number = Mock(return_value=42)
        # Act
        device_identification = cpx_e.read_device_identification()
        # Assert
        assert device_identification == 42

    @pytest.mark.parametrize("input_value", [0, 1, 2, 3])
    def test_write_function_number(self, input_value):
        """Test write_function_number"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=b"\x00\x80")
        cpx_e.write_reg_data = Mock()

        # Act
        FUNC_NUM = 0
        cpx_e.write_function_number(FUNC_NUM, input_value)

        # Assert
        cpx_e.write_reg_data.assert_has_calls(
            [
                call(
                    input_value.to_bytes(2, "little"),
                    cpx_e_modbus_registers.DATA_SYSTEM_TABLE_WRITE.register_address,
                ),
                call(
                    b"\x00\x00",
                    cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
                ),
                call(
                    b"\x00\xa0",
                    cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
                ),
            ]
        )
        cpx_e.read_reg_data.assert_called_with(
            *cpx_e_modbus_registers.PROCESS_DATA_INPUTS
        )

    def test_read_function_number(self):
        """Test read_function_number"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=b"\x00\xa0")
        cpx_e.write_reg_data = Mock()

        # Act
        cpx_e.read_function_number(1)

        # Assert
        cpx_e.write_reg_data.assert_has_calls(
            [
                call(
                    b"\x00\x00",
                    cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
                ),
                call(
                    b"\x01\x80",  # function number | control bit 15
                    cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
                ),
            ]
        )
        cpx_e.read_reg_data.assert_has_calls(
            [
                call(*cpx_e_modbus_registers.PROCESS_DATA_INPUTS),
                call(*cpx_e_modbus_registers.DATA_SYSTEM_TABLE_READ),
            ]
        )
