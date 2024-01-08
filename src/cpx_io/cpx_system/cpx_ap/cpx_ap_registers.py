"""Modbus register definitions for CPX-AP"""
from collections import namedtuple

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
