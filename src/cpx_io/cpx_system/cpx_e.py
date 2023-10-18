__author__ = "Wiesner, Martin"
__copyright__ = "Copyright 2022, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Wiesner, Martin"
__email__ = "martin.wiesner@festo.com"
__status__ = "Development"


from pymodbus.client import ModbusTcpClient

import logging


class CPXE:

    def __init__(self, host="192.168.1.1", tcpPort=502, timeout=1):
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

    def readData(self, register, length=1, type="holding_register"):
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

    def writeData(self, register, data):
        """Todo

        """
        try:
            self.client.write_register(register, data)
        except Exception as e:
            print("Error while writing: ", str(e))

    def writeMultipleData(self, register, data):
        """Todo

        """
        try:
            self.client.write_registers(register, data)
        except Exception as e:
            print("Error while writing: ", str(e))

    def readInputRegData(self, register, length=1):
        """Reads and returns input registers from Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """
        return self.readData(register, length, "input_register")

    def readHoldingRegData(self, register, length=1):
        """Reads and returns holding registers form Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """
        return self.readData(register, length, "holding_register")

    def writeOutputRegData(self, register, data):
        """Todo

        """
        return self.writeData(register, data)

    def writeOutputMultiRegData(self, register, data):
        """Todo

        """
        return self.writeMultipleData(register, data)

    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
