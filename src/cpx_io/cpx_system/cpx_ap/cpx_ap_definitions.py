"""Constant definitions for CPX-AP"""
from collections import namedtuple
from cpx_io.cpx_system.cpx_ap.apep import CpxApEp
from cpx_io.cpx_system.cpx_ap.ap8di import CpxAp8Di
from cpx_io.cpx_system.cpx_ap.ap4di import CpxAp4Di
from cpx_io.cpx_system.cpx_ap.ap4di4do import CpxAp4Di4Do
from cpx_io.cpx_system.cpx_ap.ap4aiui import CpxAp4AiUI
from cpx_io.cpx_system.cpx_ap.ap4iol import CpxAp4Iol

# Modbus register definitions for CPX-E constist of holding register address and length
ModbusRegister = namedtuple("ModbusRegister", "register_address, length")

# holding registers
OUTPUTS = ModbusRegister(0, 4096)
INPUTS = ModbusRegister(5000, 4096)
PARAMETERS = ModbusRegister(10000, 1000)

DIAGNOSIS = ModbusRegister(11000, 100)
MODULE_COUNT = ModbusRegister(12000, 1)

# module information
MODULE_CODE = ModbusRegister(15000, 2)
MODULE_CLASS = ModbusRegister(15002, 1)
COMMUNICATION_PROFILE = ModbusRegister(15003, 1)
INPUT_SIZE = ModbusRegister(15004, 1)
INPUT_CHANNELS = ModbusRegister(15005, 1)
OUTPUT_SIZE = ModbusRegister(15006, 1)
OUTPUT_CHANNELS = ModbusRegister(15007, 1)
HW_VERSION = ModbusRegister(15008, 1)
FW_VERSION = ModbusRegister(15009, 3)
SERIAL_NUMBER = ModbusRegister(15012, 2)
PRODUCT_KEY = ModbusRegister(15014, 6)
ORDER_TEXT = ModbusRegister(15020, 17)

# Dict that maps from module ids to corresponding module classes
MODULE_ID_DICT = {
    "EP": CpxApEp,
    "EX": CpxAp8Di,
    "ER": CpxAp8Di,
    "FR": CpxAp4Di,
    "YR": CpxAp4Di4Do,
    "YX": CpxAp4Di4Do,
    "NI": CpxAp4AiUI,
    "LK4": CpxAp4Iol,
}
