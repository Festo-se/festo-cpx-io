"""Contains tests for CpxE class"""
import pytest
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE  # pylint: disable=E0611

from cpx_io.cpx_system.cpx_e.eep import CpxEEp  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI  # pylint: disable=E0611
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI  # pylint: disable=E0611


class TestCpxE:
    """Test for CpxE"""

    def test_default_constructor(self):
        """Test default constructor"""
        cpx_e = CpxE()

        assert len(cpx_e.modules) == 1
        assert type(cpx_e.modules[0]) is CpxEEp

    def test_constructor_with_two_modules(self):
        """Test constructor with two modules"""
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        assert len(cpx_e.modules) == 2
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di

    def test_default_constructor_modified_modules(self):
        """Test default constructor with modified modules"""
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        assert len(cpx_e.modules) == 3
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di
        assert type(cpx_e.modules[2]) is CpxE8Do

    def test_constructor_with_typecode_MLNINO(self):
        """Test constructor with typecode"""
        cpx_e = CpxE("60E-EP-MLNINO")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di
        assert type(cpx_e.modules[2]) is CpxE8Do
        assert type(cpx_e.modules[3]) is CpxE4AiUI
        assert type(cpx_e.modules[4]) is CpxE4AoUI

    def test_constructor_with_typecode_NIMNOL(self):
        """Test constructor with typecode"""
        cpx_e = CpxE("60E-EP-NIMNOL")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE4AiUI
        assert type(cpx_e.modules[2]) is CpxE16Di
        assert type(cpx_e.modules[3]) is CpxE4AoUI
        assert type(cpx_e.modules[4]) is CpxE8Do

    def test_constructor_with_typecode_NIMNOL(self):
        """Test constructor with typecode"""
        cpx_e = CpxE("60E-EP-NIMNOL")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE4AiUI
        assert type(cpx_e.modules[2]) is CpxE16Di
        assert type(cpx_e.modules[3]) is CpxE4AoUI
        assert type(cpx_e.modules[4]) is CpxE8Do

    def test_name_access_default(self):
        """Test name access"""
        cpx_e = CpxE()

        assert type(cpx_e.cpxeep) is CpxEEp

    def test_name_access_with_two_modules(self):
        """Test name access"""
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        assert type(cpx_e.cpxeep) is CpxEEp
        assert type(cpx_e.cpxe16di) is CpxE16Di

    def test_name_access_modified_modules(self):
        """Test name access"""
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        assert type(cpx_e.cpxeep) is CpxEEp
        assert type(cpx_e.cpxe16di) is CpxE16Di
        assert type(cpx_e.cpxe8do) is CpxE8Do

    def test_name_access_modified_modules_custom_names(self):
        """Test name access"""
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m3"), CpxE16Di("m1"), CpxE8Do("m2")]

        assert type(cpx_e.m3) is CpxEEp
        assert type(cpx_e.m1) is CpxE16Di
        assert type(cpx_e.m2) is CpxE8Do

    def test_name_access_modified_modules_custom_names_removed(self):
        """Test name access"""
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m4"), CpxE16Di("m5"), CpxE8Do("m6")]

        with pytest.raises(AttributeError):
            cpx_e.m1  # pylint: disable=E1101
        with pytest.raises(AttributeError):
            cpx_e.m2  # pylint: disable=E1101
        with pytest.raises(AttributeError):
            cpx_e.m3  # pylint: disable=E1101
        assert type(cpx_e.m4) is CpxEEp
        assert type(cpx_e.m5) is CpxE16Di
        assert type(cpx_e.m6) is CpxE8Do
