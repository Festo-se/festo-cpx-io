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
    # (RegAdress, Length)
    # input registers

    # holding registers
    # E-EP
    RequestDiagnosis=(40001,16) # ??
    DataSystemTableWrite=(4002,16)

    ResponseDiagnosis=(45392,16)
    DataSystemTableRead=(45393,16)
    ModuleDiagnosisData=(45394,16)

    ModuleConfiguration=(45367,3)
    FaultDetection=(45383,3)
    StatusRegister=(45391,1)
    # E-8DO
    # ...

class CPX_E(CPX_BASE):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13

    def writeFunctionNumber(self, FunctionNumber: int, value: int):
        self.writeRegData(_ModbusCommands.DataSystemTableWrite[0], value)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], 0)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], self._control_bit_value | self._write_bit_value | FunctionNumber)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(_ModbusCommands.ResponseDiagnosis[0])[0] 
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.readRegData(_ModbusCommands.DataSystemTableRead[0])[0] 
        logging.info(f"Write Data({value}) to {FunctionNumber}: {data} and {data2} (after {its} iterations)")


    def readFunctionNumber(self, FunctionNumber: int):
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], 0)
        self.writeRegData(_ModbusCommands.RequestDiagnosis[0], self._control_bit_value | FunctionNumber)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(_ModbusCommands.ResponseDiagnosis[0])[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.readRegData(*_ModbusCommands.DataSystemTableRead)
        logging.info(f"Read Data from {FunctionNumber}: {data} and {data2} (after {its} iterations)")
        return data2


    def module_count(self) -> int:
        ''' returns the total count of attached modules
        '''
        data = self.readRegData(*_ModbusCommands.ModuleConfiguration)
        return sum([bin(d).count("1") for d in data])


    def fault_detection(self) -> list:
        ''' returns list of bools with Errors (True)
        '''
        data = self.readRegData(*_ModbusCommands.FaultDetection)
        data = data[2] << 16 + data[1] << 8 + data[0] 
        return [d == "1" for d in bin(data)[2:].zfill(24)[::-1]] 


    def status_register(self) -> tuple:
        ''' returns (Write-protected, Force active)
        '''
        writeProtectBit = 11
        forceActiveBit = 15
        data = self.readRegData(*_ModbusCommands.StatusRegister)
        return (bool(data[0] & 1 << writeProtectBit), bool(data[0] & 1 << forceActiveBit))


    def create_cpxe_8do(self, register_nummer: int):
        return self.Cpxe8Do(self, register_nummer)

    class Cpxe8Do:
        def __init__(self, cpxe_control, register_nummer: int):
            self.register_nummer = register_nummer
            self._channel_value_map = 0
            self._cpxe_control = cpxe_control

        def channel_on(self, channel_nummer: int):
            bitmaske = 1 << channel_nummer
            self._channel_value_map = self._channel_value_map | bitmaske
            self._cpxe_control.sps.writeData(self.register_nummer, self._channel_value_map)

        def all_off(self):
            self._channel_value_map = 0
            self._cpxe_control.sps.writeData(self.register_nummer, self._channel_value_map)

        def channel_off(self, channel_nummer: int):
            bitmaske = ~(1 << channel_nummer)
            self._channel_value_map = self._channel_value_map & bitmaske
            self._cpxe_control.sps.writeData(self.register_nummer, self._channel_value_map)

        def create_do_channel(self, channel: int):
            return self.DoChannel(self, channel)

        class DoChannel:
            def __init__(self, cpxe8_do, channel: int):
                self.channel = channel
                self.cpxe8_do = cpxe8_do

            def on(self):
                self.cpxe8_do.channel_on(self.channel)

            def off(self):
                self.cpxe8_do.channel_off(self.channel)

    def create_cpxe_4ai_u_i(self, module_nummer: int, register_nummer: int):
        return self.Cpxe4AiUI(self, module_nummer, register_nummer)

    class Cpxe4AiUI:
        def __init__(self, cpxe_control, module_nummer: int, start_register_nummer: int):
            self.module_nummer = module_nummer
            self.start_register_nummer = start_register_nummer
            self._cpxe_control = cpxe_control
            self._signalrange_01 = 0
            self._signalrange_23 = 0
            self._signalsmothing_01 = 0
            self._signalsmothing_23 = 0

        def set_channel_signalrange(self, channel: int, signalrange: str):
            signal_dir = {
                "None": int("0000", 2),
                "0-10V": int("0001", 2),
                "-10-+10V": int("0010", 2),
                "-5-+5V": int("0011", 2),
                "1-5V": int("0100", 2),
                "0-20mA": int("0101", 2),
                "4-20mA": int("0110", 2),
                "-20-+20mA": int("0111", 2),
                "0-10VoU": int("1000", 2),
                "0-20mAoU": int("1001", 2),
                "4-20mAoU": int("1010", 2)
            }
            if signalrange not in signal_dir:
                raise TypeError(f"'{signalrange}' is not an option")
            keepbits = int("1111", 2)
            bitmask = signal_dir[signalrange]
            if channel == 1 or channel == 3:
                bitmask = bitmask << 4
            else:
                keepbits = keepbits << 4

            if channel < 2:
                funktion_number = 4828 + 64 * self.module_nummer + 13
                self._signalrange_01 = self._signalrange_01 & keepbits
                self._signalrange_01 = self._signalrange_01 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalrange_01)
            else:
                funktion_number = 4828 + 64 * self.module_nummer + 14
                self._signalrange_23 = self._signalrange_23 & keepbits
                self._signalrange_23 = self._signalrange_23 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalrange_23)
                
        def set_channel_signalsmothing(self, channel: int, smothing_potenz: int):
            if smothing_potenz > 15:
                raise TypeError(f"'{smothing_potenz}' is not an option")
            keepbits = int("1111", 2)
            bitmask = smothing_potenz
            if channel == 1 or channel == 3:
                bitmask = bitmask << 4
            else:
                keepbits = keepbits << 4

            if channel < 2:
                funktion_number = 4828 + 64 * self.module_nummer + 15
                self._signalsmothing_01 = self._signalsmothing_01 & keepbits
                self._signalsmothing_01 = self._signalsmothing_01 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalsmothing_01)
            else:
                funktion_number = 4828 + 64 * self.module_nummer + 16
                self._signalsmothing_23 = self._signalsmothing_23 & keepbits
                self._signalsmothing_23 = self._signalsmothing_23 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalsmothing_23)

        def read_channel(self, channel: int):
            return self._cpxe_control.sps.readData(self.start_register_nummer + channel)

        def create_ai_channel(self, channel: int):
            return self.AiChannel(self, channel)

        class AiChannel:
            def __init__(self, cpxe_4ai_u_i, channel):
                self.cpxe_4ai_u_i = cpxe_4ai_u_i
                self.channel = channel

            def set_signalrange(self, signalrange: str):
                self.cpxe_4ai_u_i.set_channel_signalrange(self.channel, signalrange)
                
            def set_signalsmothing(self, smothing_potenz: int):
                self.cpxe_4ai_u_i.set_channel_signalsmothing(self.channel, smothing_potenz)

            def read(self):
                return self.cpxe_4ai_u_i.read_channel(self.channel)

    def create_cpxe_4ao_u_i(self, module_nummer: int, register_nummer: int):
        return self.Cpxe4AoUI(self, module_nummer, register_nummer)

    class Cpxe4AoUI:
        def __init__(self, cpxe_control, module_nummer: int, start_register_nummer: int):
            self.module_nummer = module_nummer
            self.start_register_nummer = start_register_nummer
            self._cpxe_control = cpxe_control
            self._signalrange_01 = int("00010001", 2)
            self._signalrange_23 = int("00010001", 2)

        def set_channel_signalrange(self, channel: int, signalrange: str):
            signal_dir = {
                "0-10V": int("0001", 2),
                "-10-+10V": int("0010", 2),
                "-5-+5V": int("0011", 2),
                "1-5V": int("0100", 2),
                "0-20mA": int("0101", 2),
                "4-20mA": int("0110", 2),
                "-20-+20mA": int("0111", 2)
            }
            if signalrange not in signal_dir:
                raise TypeError(f"'{signalrange}' is not an option")
            keepbits = int("1111", 2)
            bitmask = signal_dir[signalrange]
            if channel == 1 or channel == 3:
                bitmask = bitmask << 4
            else:
                keepbits = keepbits << 4

            if channel < 2:
                funktion_number = 4828 + 64 * self.module_nummer + 11
                self._signalrange_01 = self._signalrange_01 & keepbits
                self._signalrange_01 = self._signalrange_01 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalrange_01)
            else:
                funktion_number = 4828 + 64 * self.module_nummer + 12
                self._signalrange_23 = self._signalrange_23 & keepbits
                self._signalrange_23 = self._signalrange_23 | bitmask
                self._cpxe_control._write_funktion_number(funktion_number, self._signalrange_23)

        def write_channel(self, channel: int, value: int):
            return self._cpxe_control.sps.writeData(self.start_register_nummer + channel, value)

        def create_ao_channel(self, channel: int):
            return self.AoChannel(self, channel)

        class AoChannel:
            def __init__(self, cpxe_4ao_u_i, channel):
                self.cpxe_4ao_u_i = cpxe_4ao_u_i
                self.channel = channel

            def set_signalrange(self, signalrange: str):
                self.cpxe_4ao_u_i.set_channel_signalrange(self.channel, signalrange)

            def write(self, value: int):
                return self.cpxe_4ao_u_i.write_channel(self.channel, value)

    def create_cpxe_16di(self, register_nummer: int):
        return self.Cpxe16Di(self, register_nummer)

    class Cpxe16Di:
        def __init__(self, cpxe_control, register_nummer: int):
            self.register_nummer = register_nummer
            self._cpxe_control = cpxe_control

        def read_channel(self, channel_nummer: int):
            bitmaske = 1 << channel_nummer
            byte_returned = self._cpxe_control.sps.readData(self.register_nummer)
            return int(byte_returned & bitmaske != 0)

        def read_all(self):
            return self._cpxe_control.sps.readData(self.register_nummer)

        def create_di_channel(self, channel: int):
            return self.DiChannel(self, channel)

        class DiChannel:
            def __init__(self, cpxe8_di, channel: int):
                self.channel = channel
                self.cpxe8_di = cpxe8_di

            def read(self):
                return self.cpxe8_di.read_channel(self.channel)

# TODO: Add more Modules
