"""Constant definitions for CPX-E"""

from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol
from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci

# Dict that maps from module ids to corresponding module classes
CPX_E_MODULE_ID_DICT = {
    "EP": CpxEEp,
    "M": CpxE16Di,
    "L": CpxE8Do,
    "NI": CpxE4AiUI,
    "NO": CpxE4AoUI,
    "T51": CpxE4Iol,
    "T53": CpxE1Ci,
}

CPX_E_MODULE_ID_LIST = CPX_E_MODULE_ID_DICT.values()
