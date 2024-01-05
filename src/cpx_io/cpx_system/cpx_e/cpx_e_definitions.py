"""Constant definitions for CPX-E"""

from collections import namedtuple
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol
from cpx_io.cpx_system.cpx_e.e1ci import CpxE1Ci

# Modbus register definitions for CPX-E constist of holding register address and length
ModbusRegister = namedtuple("ModbusRegister", "register_address, length")

PROCESS_DATA_OUTPUTS = ModbusRegister(40001, 1)
DATA_SYSTEM_TABLE_WRITE = ModbusRegister(40002, 1)

PROCESS_DATA_INPUTS = ModbusRegister(45392, 1)
DATA_SYSTEM_TABLE_READ = ModbusRegister(45393, 1)

MODULE_CONFIGURATION = ModbusRegister(45367, 3)
FAULT_DETECTION = ModbusRegister(45383, 3)
STATUS_REGISTER = ModbusRegister(45391, 1)

# Dict that maps from module ids to corresponding module classes
MODULE_ID_DICT = {
    "EP": CpxEEp,
    "M": CpxE16Di,
    "L": CpxE8Do,
    "NI": CpxE4AiUI,
    "NO": CpxE4AoUI,
    "T51": CpxE4Iol,
    "T53": CpxE1Ci,
}
