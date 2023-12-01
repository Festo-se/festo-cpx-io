"""Contains tests for cpx_eep class"""
from unittest.mock import Mock


from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

from cpx_io.cpx_system.cpx_e.eep import CpxEEp


class TestCpxEEp:
    """Test cpx-e-ep"""

    def test_initialize(self):
        """Test initialize function"""
        cpx_e = CpxE()
        cpxeep = CpxEEp()

        assert cpxeep.base is None
        assert cpxeep.position is None

        cpxeep = cpx_e.modules[0]

        mocked_base = Mock()
        cpxeep.base = mocked_base

        assert cpxeep.base == mocked_base
        assert cpxeep.position == 0

    def test_repr(self):
        """Test repr"""
        cpx_e = CpxE()
        cpxeep = cpx_e.modules[0]

        mocked_base = Mock()
        cpxeep.base = mocked_base

        assert repr(cpxeep) == "cpxeep (idx: 0, type: CpxEEp)"
