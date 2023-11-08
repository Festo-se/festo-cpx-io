"""Contains tests for MotionHandler class"""
from cpx_io.cpx_system.cpx_e import CpxE, CpxEEp, CpxE16Di, CpxE8Do
from unittest.mock import Mock


class TestCpxE:
    def test_add_cpx_e_default_constructor(self):
        cpx_e = CpxE()
        assert len(cpx_e.modules) == 1
        assert type(cpx_e.modules[0]) is CpxEEp

    def test_add_cpx_e_constructor_with_two_modules(self):
        cpx_e = CpxE(modules=[CpxEEp(), CpxE16Di()])
        assert len(cpx_e.modules) == 2
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di

    def test_add_cpx_e_default_constructor_modify_modules(self):
        cpx_e = CpxE()
        cpx_e.modules = [CpxEEp(), CpxE16Di(), CpxE8Do()]

        assert len(cpx_e.modules) == 3
        assert type(cpx_e.modules[0]) is CpxEEp
        assert type(cpx_e.modules[1]) is CpxE16Di
        assert type(cpx_e.modules[2]) is CpxE8Do
