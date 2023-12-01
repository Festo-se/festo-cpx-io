"""Modbus commands for CPX-AP"""


class ModbusCommands:
    """Modbus start adresses used to read and write registers"""

    # holding registers
    outputs = (0, 4096)
    inputs = (5000, 4096)
    parameter = (10000, 1000)

    diagnosis = (11000, 100)
    module_count = (12000, 1)

    # module information
    module_code = (15000, 2)  # (+37*n)
    module_class = (15002, 1)  # (+37*n)
    communication_profiles = (15003, 1)  # (+37*n)
    input_size = (15004, 1)  # (+37*n)
    input_channels = (15005, 1)  # (+37*n)
    output_size = (15006, 1)  # (+37*n)
    output_channels = (15007, 1)  # (+37*n)
    hw_version = (15008, 1)  # (+37*n)
    fw_version = (15009, 3)  # (+37*n)
    serial_number = (15012, 2)  # (+37*n)
    product_key = (15014, 6)  # (+37*n)
    order_text = (15020, 17)  # (+37*n)
