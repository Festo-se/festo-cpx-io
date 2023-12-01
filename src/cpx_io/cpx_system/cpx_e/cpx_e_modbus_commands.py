"""Modbus commands for CPX-E"""


class ModbusCommands:
    """Modbus start adresses used to read and write registers"""

    # (RegAdress, Length)
    # input registers

    # holding registers
    process_data_outputs = (40001, 1)
    data_system_table_write = (40002, 1)

    process_data_inputs = (45392, 1)
    data_system_table_read = (45393, 1)

    module_configuration = (45367, 3)
    fault_detection = (45383, 3)
    status_register = (45391, 1)
