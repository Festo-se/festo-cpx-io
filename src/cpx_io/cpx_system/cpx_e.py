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

from .cpx_exceptions import UnknownModuleError

class _ModbusCommands:    
    # (RegAdress, Length)
    # input registers

    # holding registers
    # E-EP
    RequestDiagnosis=(40001,1)
    DataSystemTableWrite=(4002,1)

    ResponseDiagnosis=(45392,1)
    DataSystemTableRead=(45393,1)
    ModuleDiagnosisData=(45394,1)

    ModuleConfiguration=(45367,3)
    FaultDetection=(45383,3)
    StatusRegister=(45391,1)
    # E-8DO
    # ...

#TODO: need this??
class _ModbusTCPObjects:
    VendorName = 0
    ProductCode = 1
    MajorMinorRevision = 2
    VendorURL = 3
    ProductName = 4
    ModelName = 5


class CPX_E(CPX_BASE):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13
        
        self._next_output_register = 0
        self._next_input_register = 0

        self.modules = {} 
        self.add_module("CPX-E-EP")

    def writeFunctionNumber(self, FunctionNumber: int, value: int):
        self.writeRegData(value, *_ModbusCommands.DataSystemTableWrite)
        self.writeRegData(0, *_ModbusCommands.RequestDiagnosis)
        self.writeRegData(self._control_bit_value | self._write_bit_value | FunctionNumber, 
                            *_ModbusCommands.RequestDiagnosis)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(*_ModbusCommands.ResponseDiagnosis)[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.readRegData(*_ModbusCommands.DataSystemTableRead)[0]
        logging.info(f"Write Data({value}) to {FunctionNumber}: {data} and {data2} (after {its} iterations)")


    def readFunctionNumber(self, FunctionNumber: int):
        self.writeRegData(0, *_ModbusCommands.RequestDiagnosis)
        self.writeRegData(self._control_bit_value | FunctionNumber, *_ModbusCommands.RequestDiagnosis)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.readRegData(*_ModbusCommands.ResponseDiagnosis)[0]
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

    def fault_detection(self) -> list[bool]:
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

    def read_device_identification(self) -> int:
        ''' returns Objects IDO 1,2,3,4,5
        '''
        data = self.readFunctionNumber(43)
        return data[0] 

    def add_module(self, module_name):
        ''' adds one module at the next available position
        returns module
        '''
        position = len(self.modules)
        self.modules[module_name] = position
    
        if module_name == "CPX-E-EP":
            return CPX_E_EP(self, position)
        elif module_name == "CPX-E-8DO":
            return CPX_E_8DO(self, position)
        elif module_name == "CPX-E-16DI":
            return CPX_E_16DI(self, position)
        elif module_name == "CPX_E_4AI_U_I":
            return CPX_E_4AI_U_I(self, position)
        elif module_name == "CPX_E_4AO_U_I":
            return CPX_E_4AO_U_I(self, position)
        # TODO: Add more modules
        else:
            raise UnknownModuleError

class CPX_E_EP(CPX_E):
    def __init__(self, base: CPX_E, position: int):
        self.position = position
        self.base = base
        
        self.output_register = _ModbusCommands.RequestDiagnosis[0]
        self.input_register = _ModbusCommands.ResponseDiagnosis[0]

        self.base._next_output_register = self.output_register + 2
        self.base._next_input_register = self.input_register + 3

class CPX_E_8DO(CPX_E):
    def __init__(self, base: CPX_E, position: int):
        self.position = position
        self.base = base

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register = self.output_register + 1
        self.base._next_input_register = self.input_register + 2

    def read_channels(self) -> list[bool]:
        # TODO: This register reads back 0
        data = self.base.readRegData(self.input_register)[0] & 0x0F
        return [d == "1" for d in bin(data)[2:].zfill(8)[::-1]]

    def write_channels(self, data: list[bool]) -> None:
        # Make binary from list of bools
        binary_string = ''.join('1' if value else '0' for value in reversed(data))
        # Convert the binary string to an integer
        integer_data = int(binary_string, 2)
        self.base.writeRegData(integer_data, self.output_register)

    def read_status(self) -> list[bool]:
        data = self.base.readRegData(self.input_register + 1)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]
        
    def read_channel(self, channel: int) -> bool:
        return self.read_channels()[channel]

    def set_channel(self, channel: int) -> None:
        data = self.base.readRegData(self.input_register)[0] 
        self.base.writeRegData(data | 1 << channel , self.output_register)

    def clear_channel(self, channel: int) -> None:
        data = self.base.readRegData(self.input_register)[0]
        self.base.writeRegData(data & ~(1 << channel), self.output_register)
    
    def toggle_channel(self, channel: int) -> None:
        data = (self.base.readRegData(self.input_register)[0] & 1 << channel) >> channel
        if data == 1:
            self.clear_channel(channel)
        elif data == 0:
            self.set_channel(channel)
        else:
            raise ValueError

class CPX_E_16DI(CPX_E):
    def __init__(self, base: CPX_E, position: int):
        self.position = position
        self.base = base

        self.output_register = None
        self.input_register = self.base._next_input_register

        #self.base._next_output_register = self.base._next_output_register + 0
        self.base._next_input_register = self.input_register + 2

    def read_channels(self) -> list[bool]:
        data = self.base.readRegData(self.input_register)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    def read_status(self) -> list[bool]:
        data = self.base.readRegData(self.input_register + 1)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    def read_channel(self, channel: int) -> bool:
        return self.read_channels()[channel]

class CPX_E_4AI_U_I(CPX_E):
    def __init__(self, base: CPX_E, position: int):
        self.position = position
        self.base = base

        self.output_register = None
        self.input_register = self.base._next_input_register

        #self.base._next_output_register = self.base._next_output_register + 0
        self.base._next_input_register = self.input_register + 5

        self._signalrange_01 = 0
        self._signalrange_23 = 0
        self._signalsmothing_01 = 0
        self._signalsmothing_23 = 0

    def read_channels(self) -> list[bool]:
        # TODO: add signal conversion according to signalrange of the channel
        data = self.base.readRegData(self.input_register, length=4)
        return data

    def read_status(self) -> list[bool]:
        data = self.base.readRegData(self.input_register + 4)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    def read_channel(self, channel: int) -> bool:
        return self.read_channels()[channel]

    def set_channel_range(self, channel: int, signalrange: str) -> None:
        signal_dict = {
            "None": 0b0000,
            "0-10V": 0b0001,
            "-10-+10V": 0b0010,
            "-5-+5V": 0b0011,
            "1-5V": 0b0100,
            "0-20mA": 0b0101,
            "4-20mA": 0b0110,
            "-20-+20mA": 0b0111,
            "0-10VoU": 0b1000,
            "0-20mAoU": 0b1001,
            "4-20mAoU": 0b1010
        }
        if signalrange not in signal_dict:
            raise ValueError(f"'{signalrange}' is not an option")

        keepbits = 0x0F
        bitmask = signal_dict[signalrange]

        if channel in [1,3]:
            bitmask <<= 4
        else:
            keepbits <<= 4

        if channel < 2:
            functionNumber = 4828 + 64 * self.position + 13
            self._signalrange_01 &= keepbits
            self._signalrange_01 |= bitmask
            self.base.writeFunctionNumber(functionNumber, self._signalrange_01)
        elif 2 <= channel < 4:
            functionNumber = 4828 + 64 * self.position + 14
            self._signalrange_23 &= keepbits
            self._signalrange_23 |= bitmask
            self.base.writeFunctionNumber(functionNumber, self._signalrange_23)
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")
                
    def set_channel_smothing(self, channel: int, smothing_power: int) -> None:
        if smothing_power > 15:
            raise ValueError(f"'{smothing_power}' is not an option")

        keepbits = 0x0F
        bitmask = smothing_power

        if channel in [1, 3]:
            bitmask <<= 4
        else:
            keepbits <<= 4

        if channel < 2:
            functionNumber = 4828 + 64 * self.position + 15
            self._signalsmothing_01 &= keepbits
            self._signalsmothing_01 |=  bitmask
            self.base.writeFunctionNumber(functionNumber, self._signalsmothing_01)
        elif 2 <= channel < 4:
            functionNumber = 4828 + 64 * self.position + 16
            self._signalsmothing_23 &= keepbits
            self._signalsmothing_23 |= bitmask
            self.base.writeFunctionNumber(functionNumber, self._signalsmothing_23)
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")

class CPX_E_4AO_U_I(CPX_E):
    def __init__(self, base: CPX_E, position: int):
        self.position = position
        self.base = base

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register = self.output_register  + 4
        self.base._next_input_register = self.input_register + 5

        self._signalrange_01 = 0b00010001
        self._signalrange_23 = 0b00010001

    def read_channels(self) -> list[bool]:
        # TODO: add signal conversion according to signalrange of the channel
        data = self.base.readRegData(self.input_register, length=4)
        return data

    def read_status(self) -> list[bool]:
        data = self.base.readRegData(self.input_register + 4)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    def read_channel(self, channel: int) -> bool:
        return self.read_channels()[channel]

    def write_channels(self, data: list[int]) -> None:
        # TODO: scaling to given signalrange
        self.base.writeRegData(data, self.output_register, length=4)

    def write_channel(self, channel: int, data: int) -> None:
        # TODO: scaling to given signalrange
        self.base.writeRegData(data, self.output_register + channel)

    def set_channel_range(self, channel: int, signalrange: str):
        signal_dict = {
            "0-10V": 0b0001,
            "-10-+10V": 0b0010,
            "-5-+5V": 0b0011,
            "1-5V": 0b0100,
            "0-20mA": 0b0101,
            "4-20mA": 0b0110,
            "-20-+20mA": 0b0111
        }
        if signalrange not in signal_dict:
            raise ValueError(f"'{signalrange}' is not an option")

        keepbits = 0b1111
        bitmask = signal_dict[signalrange]

        if channel in [1, 3]:
            bitmask <<= 4
        else:
            keepbits <<= 4

        if channel < 2:
            funcionNumber = 4828 + 64 * self.position + 11
            self._signalrange_01 = self._signalrange_01 & keepbits
            self._signalrange_01 = self._signalrange_01 | bitmask
            self.base.writeFunctionNumber(funcionNumber, self._signalrange_01)
        elif 2 <= channel < 4:
            funcionNumber = 4828 + 64 * self.position + 12
            self._signalrange_23 = self._signalrange_23 & keepbits
            self._signalrange_23 = self._signalrange_23 | bitmask
            self.base.writeFunctionNumber(funcionNumber, self._signalrange_23)
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")

# functions copied over
    def create_cpxe_8do(self, register_nummer: int):
        return self.Cpxe8Do(self, register_nummer)

    def create_cpxe_4ai_u_i(self, module_nummer: int, register_nummer: int):
        return self.Cpxe4AiUI(self, module_nummer, register_nummer)

    class Cpxe4AiUI:
               

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


# TODO: Add more Modules
