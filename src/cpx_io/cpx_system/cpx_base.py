'''
# TODO: Add Docstring
'''
import logging

from pymodbus.client import ModbusTcpClient

class CpxInitError(Exception):
    '''Error should be raised if a cpx-... module is instanciated without connecting it to a base module.
    Connect it to the cpx by adding it with add_module(<object instance>)
    '''
    def __init__(self, message="Module must be part of a Cpx class. Use add_module() to add it"):
        super().__init__(message)

class CpxRequestError(Exception):
    '''Error should be raised if a parameter or register request is denied
    '''
    def __init__(self, message="Request failed"):
        super().__init__(message)


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
    @staticmethod
    def _require_base(func):
        def wrapper(self, *args, **kwargs):
            if not self.base:
                raise CpxInitError()
            return func(self, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def int_to_signed16(value: int):
        '''Converts a int to 16 bit register where msb is the sign
        with checking the range
        '''
        if (value <= -2**15) or (value > 2**15):
            raise ValueError(f"Integer value {value} must be in range -32768...32767 (15 bit)")
        
        if value >=0:
            return value
        else:
            return 2**15 | ((value - 2**16) & ((2**16 - 1) // 2))
    
    @staticmethod
    def signed16_to_int(value: int):
        '''Converts a 16 bit register where msb is the sign to python signed int
        by computing the two's complement 
        '''
        if value > 0xFFFF:
            raise ValueError(f"Value {value} must not be bigger than 16 bit")
        
        if (value & (2**15)) != 0:        # if sign bit is set
            value = value - 2**16       # compute negative value
        return value
    
    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
