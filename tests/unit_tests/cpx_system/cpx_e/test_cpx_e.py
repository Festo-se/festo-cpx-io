"""Contains tests for CpxE class"""
from unittest.mock import Mock, patch
import pytest
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI

from cpx_io.cpx_system.cpx_e.cpx_e import CpxInitError
import cpx_io.cpx_system.cpx_e.cpx_e_registers as cpx_e_registers

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
        cpx_e.read_reg_data = Mock(return_value=[0xAA, 0xAA, 0xAA])

        # Act
        module_count = cpx_e.module_count()

        # Assert
        assert module_count == bin(0xAAAAAA)[2:].count("1")
        cpx_e.read_reg_data.assert_called_with(*cpx_e_registers.MODULE_CONFIGURATION)

    def test_fault_detection(self):
        """Test fault detection"""
        # Arrange
        cpx_e = CpxE()
        cpx_e.read_reg_data = Mock(return_value=[0xAA, 0xBB, 0xCC])

        # Act
        fault_detection = cpx_e.fault_detection()

        # Assert
        assert fault_detection == [x == "1" for x in bin(0xCCBBAA)[2:]][::-1]
        cpx_e.read_reg_data.assert_called_with(*cpx_e_registers.FAULT_DETECTION)
