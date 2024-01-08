"""Constant definitions for CPX-AP"""
from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol
from cpx_io.cpx_system.cpx_ap.ap8do import CpxAp8Do
from cpx_io.cpx_system.cpx_ap.ap12di4do import CpxAp12Di4Do
from cpx_io.cpx_system.cpx_ap.ap16di import CpxAp16Di

# Dict that maps from module ids to corresponding module classes
CPX_AP_MODULE_ID_DICT = {
    "EP": CpxApEp,
    "FR": CpxAp4Di,
    "EX": CpxAp8Di,
    "ER": CpxAp8Di,
    "NM": CpxAp16Di,
    "LM": CpxAp8Do,
    "YR": CpxAp4Di4Do,
    "YX": CpxAp4Di4Do,
    "AM": CpxAp12Di4Do,
    "NI": CpxAp4AiUI,
    "LK4": CpxAp4Iol,
}

CPX_AP_MODULE_ID_LIST = CPX_AP_MODULE_ID_DICT.values()
