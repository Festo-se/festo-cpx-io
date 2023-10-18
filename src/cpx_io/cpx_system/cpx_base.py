__author__ = "Wiesner, Martin"
__copyright__ = "Copyright 2023, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Wiesner, Martin"
__email__ = "martin.wiesner@festo.com"
__status__ = "Development"

from pymodbus.client import ModbusTcpClient

import logging

class CPX_BASE:
    """
    A class to connect to the Festo CPX system and read data from IO modules

    Attributes:
        moduleCount -- Integer representing the IO module count (read on `__init__()` or `readStaticInformation()`)
        moduleInformation -- List with detail for the modules (read on `__init__()` or `readStaticInformation()`)

    Methods:
        readData(self, register, length=1, type="holding_register") -- Reads and returns holding or input register from Modbus server
        readInputRegData(self, register, length=1) -- Reads and returns input registers from Modbus server
        readHoldingRegData(self, register, length=1) -- Reads and returns holding registers form Modbus server
        readModuleCount(self) -- Reads and returns IO module count
        readModuleInformation(self, module) -- Reads and returns detailed information for a specific IO module
        readStaticInformation(self) -- Manualy reads and updates the class attributes `moduleCount` and `moduleInformation`
        readModuleData(self, module) -- Reads and returns process data of a specific IO module
    """
    def __init__(self, host="192.168.0.1", tcpPort=502, timeout=1):
        self.moduleCount = None
        self.moduleInformation = []

        self.deviceConfig = {"tcpPort": tcpPort, "ip": host, "modbusSlave": 16, "timeout": timeout}

        try:
            self.client = ModbusTcpClient(host=self.deviceConfig["ip"], port=self.deviceConfig["tcpPort"], timeout=self.deviceConfig["timeout"])
            self.client.connect()
            self.client.write_register(46100, 0)
            logging.info("Connected")

        except Exception as e:
            print("Incorrect Modbus configuration : ", str(e))


    def readRegData(self, register, length=1, type="holding_register"):
        """Reads and returns holding or input register from Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        type -- type of register. Can be `holding_register` or `input_register` (default: `holding_register`)
        """
        try:
            if(type == "holding_register"):
                data = self.client.read_holding_registers(register, length)
            elif(type == "input_register"):
                data = self.client.read_input_registers(register, length)
            else:
                raise Exception("Unknown type")
            if(data.isError()):
                raise Exception("Cannot read register")
            if(length == 1):
                return data.registers[0]
            else:
                return data.registers
        except Exception as e:
            print("Error while reading: ", str(e))

    def readInputRegData(self, register, length=1):
        """Reads and returns input registers from Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """
        return self.readRegData(register, length, "input_register")
    
    def readHoldingRegData(self, register, length=1):
        """Reads and returns holding registers form Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """
        return self.readRegData(register, length, "holding_register")