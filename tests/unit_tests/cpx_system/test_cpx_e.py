"""Contains tests for MotionHandler class"""
import pytest
from cpx_io.cpx_system.cpx_e import (
    CpxE,
    CpxEEp,
    CpxE16Di,
    CpxE8Do,
    CpxE4AiUI,
    CpxE4AoUI,
)


class TestCpxE:
    def test_default_constructor(self):
        cpx_e = CpxE()

        assert len(cpx_e.modules) == 1
        assert type(cpx_e.modules[0]) is CpxEEp

    def test_constructor_with_two_modules(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        assert len(cpx_e.modules) == 2
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di

    def test_default_constructor_modified_modules(self):
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        assert len(cpx_e.modules) == 3
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di
        assert type(cpx_e.modules[2]) is CpxE8Do

    def test_constructor_with_typecode_MLNINO(self):
        cpx_e = CpxE("60E-EP-MLNINO")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di
        assert type(cpx_e.modules[2]) is CpxE8Do
        assert type(cpx_e.modules[3]) is CpxE4AiUI
        assert type(cpx_e.modules[4]) is CpxE4AoUI

    def test_constructor_with_typecode_NIMNOL(self):
        cpx_e = CpxE("60E-EP-NIMNOL")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE4AiUI
        assert type(cpx_e.modules[2]) is CpxE16Di
        assert type(cpx_e.modules[3]) is CpxE4AoUI
        assert type(cpx_e.modules[4]) is CpxE8Do

    def test_constructor_with_typecode_NIMNOL(self):
        cpx_e = CpxE("60E-EP-NIMNOL")

        assert len(cpx_e.modules) == 5
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE4AiUI
        assert type(cpx_e.modules[2]) is CpxE16Di
        assert type(cpx_e.modules[3]) is CpxE4AoUI
        assert type(cpx_e.modules[4]) is CpxE8Do

    def test_name_access_default(self):
        cpx_e = CpxE()

        assert type(cpx_e.cpxeep) is CpxEEp

    def test_name_access_with_two_modules(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])

        assert type(cpx_e.cpxeep) is CpxEEp
        assert type(cpx_e.cpxe16di) is CpxE16Di

    def test_name_access_modified_modules(self):
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        assert type(cpx_e.cpxeep) is CpxEEp
        assert type(cpx_e.cpxe16di) is CpxE16Di
        assert type(cpx_e.cpxe8do) is CpxE8Do

    def test_name_access_modified_modules_custom_names(self):
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m3"), CpxE16Di("m1"), CpxE8Do("m2")]

        assert type(cpx_e.m3) is CpxEEp
        assert type(cpx_e.m1) is CpxE16Di
        assert type(cpx_e.m2) is CpxE8Do

    def test_name_access_modified_modules_custom_names_removed(self):
        cpx_e = CpxE([CpxEEp("m1"), CpxE16Di("m2"), CpxE8Do("m3")])
        cpx_e.modules = [CpxEEp("m4"), CpxE16Di("m5"), CpxE8Do("m6")]

        with pytest.raises(AttributeError):
            cpx_e.m1
        with pytest.raises(AttributeError):
            cpx_e.m2
        with pytest.raises(AttributeError):
            cpx_e.m3
        assert type(cpx_e.m4) is CpxEEp
        assert type(cpx_e.m5) is CpxE16Di
        assert type(cpx_e.m6) is CpxE8Do
