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
from cpx_io.cpx_system.cpx_ap.vabx_ap import VabxAP
from cpx_io.cpx_system.cpx_ap.vaem_ap import VaemAP
from cpx_io.cpx_system.cpx_ap.vmpal_ap import VmpalAP
from cpx_io.cpx_system.cpx_ap.vaba_ap import VabaAP

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
    "LKA": CpxAp4Iol,
    "LKS": CpxAp4Iol,
    "LKM": CpxAp4Iol,
    "LKC": CpxAp4Iol,
    "LKB": CpxAp4Iol,
    "VABX": VabxAP,
    "VAEM": VaemAP,
    "VMPAL": VmpalAP,
    "VABA": VabaAP,
}

CPX_AP_MODULE_ID_LIST = CPX_AP_MODULE_ID_DICT.values()
