__author__ = "Wiesner, Martin"
__copyright__ = "Copyright 2022, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Wiesner, Martin"
__email__ = "martin.wiesner@festo.com"
__status__ = "Development"


import logging

from .cpx_base import CPX_BASE

class _ModbusCommands:    
#input registers
#holding registers
    # E-EP
    RequestDiagnosis=(40001,16)
    DataSystemTableWrite=(4002,16)
    ResponseDiagnosis=(45392,16)
    DataSystemTableRead=(45393,16)
    ModuleDiagnosisData=(45394,16)
    # E-8DO
    # ...


class CPX_E(CPX_BASE):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13

    def writeFunctionNumber(self, number: int, value: int):
        self.writeRegData(_ModbusCommands.DataSystemTableWrite[0], value)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], 0)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], self._control_bit_value | self._write_bit_value | number)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(_ModbusCommands.ResponseDiagnosis[0])[0] 
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.readRegData(_ModbusCommands.DataSystemTableRead[0])[0] 
        logging.info(f"Write Data({value}) to {number}: {data} and {data2} (after {its} iterations)")


    def readFunctionNumber(self, number: int):
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], 0)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], self._control_bit_value | number)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(_ModbusCommands.ResponseDiagnosis[0])[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.readRegData(*_ModbusCommands.DataSystemTableRead)
        logging.info(f"Read Data from {number}: {data} and {data2} (after {its} iterations)")
        return data2

    def module_count(self) -> int:
        ''' returns the number of attached modules
        '''
        module_available_address = 45367
        data = self.readRegData(module_available_address, length=3)
        number = 0
        for n in data:
            number += bin(n).count("1")
        return number
