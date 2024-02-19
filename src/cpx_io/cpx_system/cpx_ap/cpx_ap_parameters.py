"""Parameter definitions for CPX-AP"""

from collections import namedtuple

# Parameter definitions for CPX-AP constist of id and type
ParameterMapItem = namedtuple("ParameterMapItem", "id, dtype")

# AP Parameter IDs
FIELDBUS_SERIAL_NUMBER = ParameterMapItem(246, "UINT32")

PRODUCT_KEY = ParameterMapItem(791, "CHAR[12]")

FIRMWARE_VERSION_STRING = ParameterMapItem(960, "CHAR[30]")

DHCP_ENABLE = ParameterMapItem(12000, "BOOL")
IP_ADDRESS = ParameterMapItem(12001, "UINT32")
SUBNET_MASK = ParameterMapItem(12002, "UINT32")
GATEWAY_ADDRESS = ParameterMapItem(12003, "UINT32")
IP_ADDRESS_ACTIVE = ParameterMapItem(12004, "UINT32")
SUBNET_MASK_ACTIVE = ParameterMapItem(12005, "UINT32")
GATEWAY_ACTIVE = ParameterMapItem(12006, "UINT32")
MAC_ADDRESS = ParameterMapItem(12007, "UINT8[6]")

MODULE_CODE = ParameterMapItem(20000, "UINT32")

INPUT_DEBOUNCE_TIME = ParameterMapItem(20014, "ENUM_ID")

VALVE_DEFECT_DIAG_ENABLE = ParameterMapItem(20021, "BOOL")
LOAD_SUPPLY_DIAG_SETUP = ParameterMapItem(20022, "ENUM_ID")

OVERLOAD_SHORT_CIRCUIT_ENABLE = ParameterMapItem(20026, "BOOL")
OPENLOAD_DIAG_ENABLE = ParameterMapItem(20027, "BOOL")

CONFIGURATION_ERROR_DIAG_ENABLE = ParameterMapItem(20030, "BOOL")

TEMPERATURE_UNIT = ParameterMapItem(20032, "ENUM_ID")
CHANNEL_INPUT_MODE = ParameterMapItem(20043, "ENUM_ID")
UPPER_THRESHOLD_VALUE = ParameterMapItem(20044, "INT16")
LOWER_THRESHOLD_VALUE = ParameterMapItem(20045, "INT16")
DIAGNOSIS_HYSTERESIS = ParameterMapItem(20046, "UINT16")

NOMINAL_CYCLE_TIME = ParameterMapItem(20049, "ENUM_ID")
DEVICE_LOST_DIAGNOSIS_ENABLE = ParameterMapItem(20050, "BOOL")

FAIL_STATE_BEHAVIOUR = ParameterMapItem(20052, "ENUM_ID")

PORT_MODE = ParameterMapItem(20071, "ENUM_ID")
VALIDATION_AND_BACKUP = ParameterMapItem(20072, "ENUM_ID")
NOMINAL_VENDOR_ID = ParameterMapItem(20073, "UINT16")
PORT_STATUS_INFO = ParameterMapItem(20074, "ENUM_ID")
REVISION_ID = ParameterMapItem(20075, "UINT8")
TRANSMISSION_RATE = ParameterMapItem(20076, "ENUM_ID")
ACTUAL_CYCLE_TIME = ParameterMapItem(20077, "UINT16")
ACTUAL_VENDOR_ID = ParameterMapItem(20078, "UINT16")
ACTUAL_DEVICE_ID = ParameterMapItem(20079, "UINT32")
NOMINAL_DEVICE_ID = ParameterMapItem(20080, "UINT32")

TEMPERATURE_VALUE_ASIC = ParameterMapItem(20085, "INT16")

U_ELSEN_VALUE = ParameterMapItem(20087, "UINT16")
U_LOAD_VALUE = ParameterMapItem(20088, "UINT16")

VARIANT_SWITCH = ParameterMapItem(20090, "UINT32")

SENSOR_SUPPLY_ENABLE = ParameterMapItem(20097, "BOOL")

HARDWARE_VERSION = ParameterMapItem(20093, "UINT8")

SMOOTH_FACTOR = ParameterMapItem(20107, "UINT8")
IO_LINK_INPUT_DATA_LENGTH = ParameterMapItem(20108, "UINT8")
IO_LINK_OUTPUT_DATA_LENGTH = ParameterMapItem(20109, "UINT8")

LINEAR_SCALING_ENABLE = ParameterMapItem(20111, "BOOL")

AP_DIAGNOSIS_STATUS = ParameterMapItem(20196, "UINT8[n]")
