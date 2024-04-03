"""Modbus register definitions for CPX-AP"""

from collections import namedtuple

# Modbus register definitions for CPX-AP constist of holding register address and length
ModbusRegister = namedtuple("ModbusRegister", "register_address, length")

# holding registers
OUTPUTS = ModbusRegister(0, 4096)
INPUTS = ModbusRegister(5000, 4096)
PARAMETERS = ModbusRegister(10000, 1000)

DIAGNOSIS = ModbusRegister(11000, 100)
MODULE_COUNT = ModbusRegister(12000, 1)
TIMEOUT = ModbusRegister(14000, 2)

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

# IO-Link ISDU access
ISDU_STATUS = ModbusRegister(34000, 1)
ISDU_COMMAND = ModbusRegister(34001, 1)
ISDU_MODULE_NO = ModbusRegister(34002, 1)
ISDU_CHANNEL = ModbusRegister(34003, 1)
ISDU_INDEX = ModbusRegister(34004, 1)
ISDU_SUBINDEX = ModbusRegister(34005, 1)
ISDU_LENGTH = ModbusRegister(34006, 1)
ISDU_DATA = ModbusRegister(34007, 119)
