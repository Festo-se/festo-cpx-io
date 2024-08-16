"""Contains tests for cpx_eep class"""

from unittest.mock import Mock
from cpx_io.cpx_system.cpx_e.eep import CpxEEp


class TestCpxEEp:
    """Test cpx-e-ep"""

    def test_constructor_default(self):
        """Test initialize function"""
        # Arrange

        # Act
        cpxeep = CpxEEp()

        # Assert
        assert cpxeep.base is None
        assert cpxeep.position is None

    def test_configure(self):
        """Test configure function"""
        # Arrange
        cpxeep = CpxEEp()
        mocked_base = Mock()

        # Act
        MODULE_POSITION = 0
        cpxeep.configure(mocked_base, MODULE_POSITION)

        # Assert
        assert cpxeep.base == mocked_base
        assert cpxeep.position == MODULE_POSITION

    def test_repr_correct_string(self):
        """Test repr"""
        # Arrange
        cpxeep = CpxEEp()
        cpxeep.position = 0

        # Act
        module_repr = repr(cpxeep)

        # Assert
        assert module_repr == "cpxeep (idx: 0, type: CpxEEp)"
