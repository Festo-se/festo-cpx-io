"""Modbus register definitions for CPX-E"""

from collections import namedtuple

# Modbus register definitions for CPX-E constist of holding register address and length
ModbusRegister = namedtuple("ModbusRegister", "register_address, length")

PROCESS_DATA_OUTPUTS = ModbusRegister(40001, 1)
DATA_SYSTEM_TABLE_WRITE = ModbusRegister(40002, 1)

PROCESS_DATA_INPUTS = ModbusRegister(45392, 1)
DATA_SYSTEM_TABLE_READ = ModbusRegister(45393, 1)

MODULE_CONFIGURATION = ModbusRegister(45367, 3)
FAULT_DETECTION = ModbusRegister(45383, 3)
STATUS_REGISTER = ModbusRegister(45391, 1)
