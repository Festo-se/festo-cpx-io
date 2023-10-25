'''
# TODO: Add Docstring
'''
import logging

from pymodbus.client import ModbusTcpClient


class CpxBase:
    """
    A class to connect to the Festo CPX system and read data from IO modules

    Attributes:
        moduleCount -- Integer representing the IO module count 
            (read on `__init__()` or `readStaticInformation()`)
        moduleInformation -- List with detail for the modules 
            (read on `__init__()` or `readStaticInformation()`)

    Methods:
        readData(self, register, length=1, type="holding_register") 
            -- Reads and returns holding or input register from Modbus server
        readInputRegData(self, register, length=1) 
            -- Reads and returns input registers from Modbus server
        readHoldingRegData(self, register, length=1) 
            -- Reads and returns holding registers form Modbus server
        readModuleCount(self) -- Reads and returns IO module count
        readModuleInformation(self, module) 
            -- Reads and returns detailed information for a specific IO module
        readStaticInformation(self) 
            -- Manualy reads and updates the class attributes `moduleCount` and `moduleInformation`
        readModuleData(self, module) 
            -- Reads and returns process data of a specific IO module
    """
    def __init__(self, host="192.168.1.1", tcp_port=502, timeout=1):
        # TODO:
        #self.moduleCount = None -> must go to CPX-AP only
        #self.moduleInformation = [] -> must go to CPX-AP only

        self.device_config = {"tcp_port": tcp_port,
                             "ip": host,
                             "modbus_slave": 16,
                             "timeout": timeout
                             }

        self.client = ModbusTcpClient(host=self.device_config["ip"],
                                      port=self.device_config["tcp_port"],
                                      timeout=self.device_config["timeout"])

        self.client.connect()
        logging.info("Connected")

    def read_reg_data(self, register:int, length=1) -> list:
        """Reads and returns register from Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """

        data = self.client.read_holding_registers(register, length)

        if data.isError():
            raise ValueError("Reading modbus failed")

        return data.registers

    # TODO: Check if needed here
    '''
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
    '''
    def write_reg_data(self, data: int|list, register: int, length=1):
        """Todo

        """
        if isinstance(data, int):
            for i in range(0, length):
                self.client.write_register(register + i, data)

        elif isinstance(data, list):
            for i, d in enumerate(data):
                self.client.write_register(register + i, d)
        else:
            raise TypeError("data must be of type int or list")

    # TODO: Check if needed here
    '''
    def writeMultipleData(self, register, data):
        """Todo

        """
        try:
            self.client.write_registers(register, data)
        except Exception as e:
            print("Error while writing: ", str(e))


    def writeOutputRegData(self, register, data):
        """Todo

        """
        return self.writeData(register, data)

    def writeOutputMultiRegData(self, register, data):
        """Todo

        """
        return self.writeMultipleData(register, data)
    '''
    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
