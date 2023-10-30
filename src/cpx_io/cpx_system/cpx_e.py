'''TODO: Add module docstring
'''

import logging
import ctypes

from .cpx_base import CpxBase


class InitError(Exception):
    '''Error should be raised if a cpx-e-... module is instanciated without connecting it to a base module.
    Connect it to the cpx-e by adding it with add_module(<object instance>)
    '''
    def __init__(self, message="Module must be part of a cpx_e class. Use add_module() to add it"):
        super().__init__(message)


class _ModbusCommands:
    '''Modbus start adresses used to read and write registers
    '''
    # (RegAdress, Length)
    # input registers

    # holding registers
    process_data_outputs=(40001,1)
    data_system_table_write=(40002,1)

    process_data_inputs=(45392,1)
    data_system_table_read=(45393,1)

    module_configuration=(45367,3)
    fault_detection=(45383,3)
    status_register=(45391,1)


class CpxE(CpxBase):
    '''CPX-E base class
    '''
    def __init__(self, modules=None, **kwargs):
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13

        self._next_output_register = 0
        self._next_input_register = 0

        self.output_register = None
        self.input_register = None

        self.modules = {}

        if modules:
            for m in modules:
                self.add_module(m)
        else:
            self.add_module(CpxEEp())

    def write_function_number(self, function_number: int, value: int):
        '''Write parameters via function number
        '''
        self.write_reg_data(value, *_ModbusCommands.data_system_table_write)
        # need to write 0 first because there might be an 
        # old unknown configuration in the register
        self.write_reg_data(0, *_ModbusCommands.process_data_outputs)
        self.write_reg_data(self._control_bit_value | self._write_bit_value | function_number,
                            *_ModbusCommands.process_data_outputs)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.read_reg_data(*_ModbusCommands.process_data_inputs)[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.read_reg_data(*_ModbusCommands.data_system_table_read)[0]
        logging.info(f"Write Data({value}) to {function_number}: {data} and {data2}")

    def read_function_number(self, function_number: int):
        '''Read parameters via function number
        '''
        # need to write 0 first because there might be an 
        # old unknown configuration in the register
        self.write_reg_data(0, *_ModbusCommands.process_data_outputs)
        self.write_reg_data(self._control_bit_value | function_number,
                          *_ModbusCommands.process_data_outputs)

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.read_reg_data(*_ModbusCommands.process_data_inputs)[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        data2 = self.read_reg_data(*_ModbusCommands.data_system_table_read)
        logging.info(f"Read Data from {function_number}: {data} and {data2}")
        return data2

    def module_count(self) -> int:
        ''' returns the total count of attached modules
        '''
        data = self.read_reg_data(*_ModbusCommands.module_configuration)
        return sum(d.bit_count() for d in data)

    def fault_detection(self) -> list[bool]:
        ''' returns list of bools with Errors (True = Error)
        '''
        data = self.read_reg_data(*_ModbusCommands.fault_detection)
        data = data[2] << 16 + data[1] << 8 + data[0]
        return [d == "1" for d in bin(data)[2:].zfill(24)[::-1]]

    def status_register(self) -> tuple:
        ''' returns (Write-protected, Force active)
        '''
        write_protect_bit = 1 << 11
        force_active_bit = 1 << 15
        data = self.read_reg_data(*_ModbusCommands.status_register)
        return (bool(data[0] & write_protect_bit), bool(data[0] & force_active_bit))

    def read_device_identification(self) -> int:
        ''' returns Objects IDO 1,2,3,4,5
        '''
        data = self.read_function_number(43)
        return data[0]

    def add_module(self, module):
        '''Adds one module to the base. This is required to use the module.
        '''
        module._initialize(self, len(self.modules))
        return module


class _CpxEModule(CpxE):
    '''Base class for cpx-e modules
    '''
    def __init__(self):
        self.base = None
        self.position = None

    def _initialize(self, base, position):
        self.base = base
        self.position = position

    @staticmethod
    def _require_base(func):
        def wrapper(self, *args, **kwargs):
            if not self.base:
                raise InitError()
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

class CpxEEp(_CpxEModule):
    '''Class for CPX-E-EP module
    '''
    def _initialize(self, *args):
        super()._initialize(*args)

        self.base.modules["CPX-E-EP"] = self.position

        self.output_register = _ModbusCommands.process_data_outputs[0]
        self.input_register = _ModbusCommands.process_data_inputs[0]

        self.base._next_output_register = self.output_register + 2
        self.base._next_input_register = self.input_register + 3


class CpxE8Do(_CpxEModule):
    '''Class for CPX-E-8DO module
    '''
    def _initialize(self, *args):
        super()._initialize(*args)

        self.base.modules["CPX-E-8DO"] = self.position

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register = self.output_register + 1
        self.base._next_input_register = self.input_register + 2

    @_CpxEModule._require_base
    def read_channels(self) -> list[bool]:
        '''read all channels as a list of bool values
        '''
        data = self.base.read_reg_data(self.input_register)[0] & 0x0F
        return [d == "1" for d in bin(data)[2:].zfill(8)[::-1]]

    @_CpxEModule._require_base
    def write_channels(self, data: list[bool]) -> None:
        '''write all channels with a list of bool values
        '''
        # Make binary from list of bools
        binary_string = ''.join('1' if value else '0' for value in reversed(data))
        # Convert the binary string to an integer
        integer_data = int(binary_string, 2)
        self.base.write_reg_data(integer_data, self.output_register)

    @_CpxEModule._require_base
    def read_status(self) -> list[bool]:
        '''read module status register. Further information see module datasheet
        '''
        data = self.base.read_reg_data(self.input_register + 1)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @_CpxEModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]

    @_CpxEModule._require_base
    def set_channel(self, channel: int) -> None:
        '''set one channel to logic high level
        '''
        data = self.base.read_reg_data(self.input_register)[0]
        self.base.write_reg_data(data | 1 << channel , self.output_register)

    @_CpxEModule._require_base
    def clear_channel(self, channel: int) -> None:
        '''set one channel to logic low level
        '''
        data = self.base.read_reg_data(self.input_register)[0]
        self.base.write_reg_data(data & ~(1 << channel), self.output_register)

    @_CpxEModule._require_base
    def toggle_channel(self, channel: int) -> None:
        '''set one channel the inverted of current logic level
        '''
        data = (self.base.read_reg_data(self.input_register)[0] & 1 << channel) >> channel
        if data == 1:
            self.clear_channel(channel)
        elif data == 0:
            self.set_channel(channel)
        else:
            raise ValueError
        
    @_CpxEModule._require_base
    def configure_diagnostics(self, short_circuit=None, undervoltage=None):
        '''The "Diagnostics of short circuit at output" parameter defines whether the diagnostics of the outputs
        in regard to short circuit or overload should be activated or deactivated.
        The "Diagnostics of undervoltage at load supply" parameter defines if the diagnostics for the load
        supply must be activated or deactivated with regard to undervoltage.
        When the diagnostics are activated, the error will be sent to the bus module and displayed on the
        module by the error LED.
        '''
        function_number = 4828 + 64 * self.position + 0
        diagnostics_reg = self.base.read_function_number(function_number)[0]
        
        # Fill in the unchanged values from the register
        if short_circuit == None:
            short_circuit = bool((diagnostics_reg & 0x02) >> 2)
        if undervoltage == None:
            undervoltage = bool((diagnostics_reg & 0x04) >> 4)

        value_to_write = (int(short_circuit) << 1) | (int(undervoltage) << 2)

        self.base.write_function_number(function_number, value_to_write)


    @_CpxEModule._require_base
    def configure_power_reset(self, value: bool):
        '''The "Behaviour after SCO" parameter defines whether the voltage remains switched off ("False", default) or 
        automatically switches on ("True") again after a short circuit or overload at the outputs.
        In the case of the "Leave power switched off" setting, the CPX-E automation system must be switched
        off and on or the corresponding output must be reset and to restore the power.
        '''
        function_number = 4828 + 64 * self.position + 1
        behaviour_reg = self.base.read_function_number(function_number)[0]
        
        # Fill in the unchanged values from the register
        if value:
            value_to_write = behaviour_reg | 0x02
        else:
            value_to_write = behaviour_reg & 0xFD

        self.base.write_function_number(function_number, value_to_write)
                

class CpxE16Di(_CpxEModule):
    '''Class for CPX-E-16DI module
    '''

    def _initialize(self, *args):
        super()._initialize(*args)

        self.base.modules["CPX-E-16DI"] = self.position

        self.output_register = None
        self.input_register = self.base._next_input_register

        #self.base._next_output_register = self.base._next_output_register + 0
        self.base._next_input_register = self.input_register + 2

    @_CpxEModule._require_base
    def read_channels(self) -> list[bool]:
        '''read all channels as a list of bool values
        '''
        data = self.base.read_reg_data(self.input_register)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @_CpxEModule._require_base
    def read_status(self) -> list[bool]:
        '''read module status register. Further information see module datasheet
        '''
        data = self.base.read_reg_data(self.input_register + 1)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @_CpxEModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]
    
    @_CpxEModule._require_base
    def configure_diagnostics(self, value: bool) -> None:
        '''The "Diagnostics of sensor supply short circuit" defines whether the diagnostics of the sensor supply
        in regard to short circuit or overload should be activated ("True", default) or deactivated (False).
        When the diagnostics are activated, the error will be sent to the bus module and displayed on the
        module by the error LED.
        '''
        pass
    
    @_CpxEModule._require_base
    def configure_power_reset(self, value: bool) -> None:
        ''' "Behaviour after SCO" parameter defines whether the voltage remains switched off ("False") or 
        automatically switches on again ("True", default) after a short circuit or overload of the sensor supply.
        In the case of the "Leave power switched off" setting, the CPX-E automation system must be switched
        off and on to restore the power.

        '''
        pass
    
    @_CpxEModule._require_base
    def configrue_debounce_time(self, value: int) -> None:
        '''The "Input debounce time" parameter defines when an edge change of the sensor signal shall be
        assumed as a logical input signal.
        In this way, unwanted signal edge changes can be suppressed during switching operations (bouncing
        of the input signal).
        Accepted values are 0: 0.1 ms; 1: 3 ms (default); 2: 10 ms; 3: 20 ms;
        '''
        if value < 0 or value > 4:
            raise ValueError("Value {value} must be between 0 and 3")
        pass
    
    @_CpxEModule._require_base
    def configure_signal_extension_time(self, value: int) -> None:
        '''The "Signal extension time" parameter defines the minimum valid duration of the assumed signal
        status of the input signal. Edge changes within the signal extension time are ignored.
        Short input signals can also be recorded by defining a signal extension time.
        Accepted values are 0: 0.5 ms; 1: 15 ms (default); 2: 50 ms; 3: 100 ms;
        '''
        if value < 0 or value > 4:
            raise ValueError("Value {value} must be between 0 and 3")
        pass


class CpxE4AiUI(_CpxEModule):
    '''Class for CPX-E-4AI-UI module
    '''

    def __init__(self, *args):
        super().__init__(*args)

        self._signalrange_01 = 0x00
        self._signalrange_23 = 0x00
        self._signalsmothing_01 = 0x00
        self._signalsmothing_23 = 0x00

    def _initialize(self, *args):
        super()._initialize(*args)

        self.base.modules["CPX-E-4AI-U-I"] = self.position

        self.output_register = None
        self.input_register = self.base._next_input_register

        #self.base._next_output_register = self.base._next_output_register + 0
        self.base._next_input_register = self.input_register + 5

    @_CpxEModule._require_base
    def read_channels(self) -> list[int]:
        '''read all channels as a list of (signed) integers
        '''
        # TODO: add signal conversion according to signalrange of the channel
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        signed_integers = [self.signed16_to_int(x) for x in raw_data]
        return signed_integers

    @_CpxEModule._require_base
    def read_status(self) -> list[bool]:
        '''read module status register. Further information see module datasheet
        '''
        data = self.base.read_reg_data(self.input_register + 4)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @_CpxEModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]

    @_CpxEModule._require_base
    def set_channel_range(self, channel: int, signalrange: str) -> None:
        '''set the signal range and type of one channel
        '''
        bitmask = {
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
        if signalrange not in bitmask:
            raise ValueError(f"'{signalrange}' is not an option. Choose from {bitmask.keys()}")

        function_number = 4828 + 64 * self.position
        if channel == 0:
            function_number += 13
            self._signalrange_01 |= bitmask[signalrange]
            value_to_write = self._signalrange_01
        elif channel == 1:
            function_number += 13
            self._signalrange_01 |= bitmask[signalrange] << 4
            value_to_write = self._signalrange_01
        elif channel == 2:
            function_number += 14
            self._signalrange_23 |= bitmask[signalrange]
            value_to_write = self._signalrange_23
        elif channel == 3:
            function_number += 14
            self._signalrange_23 |= bitmask[signalrange] << 4
            value_to_write = self._signalrange_23     
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")
        
        self.base.write_function_number(function_number, value_to_write)

    @_CpxEModule._require_base
    def set_channel_smothing(self, channel: int, smothing_power: int) -> None:
        '''set the signal smoothing of one channel
        '''
        if smothing_power > 15:
            raise ValueError(f"'{smothing_power}' is not an option")

        bitmask = smothing_power

        function_number = 4828 + 64 * self.position

        if channel == 0:
            function_number += 15
            self._signalsmothing_01 |=  bitmask
            value_to_write = self._signalsmothing_01
        elif channel == 1:
            function_number += 15
            self._signalsmothing_01 |=  bitmask << 4
            value_to_write = self._signalsmothing_01
        elif channel == 2:
            function_number += 16
            self._signalsmothing_23 |=  bitmask
            value_to_write = self._signalsmothing_23
        elif channel == 3:
            function_number += 16
            self._signalsmothing_23 |=  bitmask << 4
            value_to_write = self._signalsmothing_23
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")
        
        self.base.write_function_number(function_number, value_to_write)


class CpxE4AoUI(_CpxEModule):
    '''Class for CPX-E-4AO-UI module
    '''
    def __init__(self, *args):
        super().__init__(*args)

        self._signalrange_01 = 0b00010001
        self._signalrange_23 = 0b00010001

    def _initialize(self, *args):
        super()._initialize(*args)

        self.base.modules["CPX-E-4AO-U-I"] = self.position

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register = self.output_register  + 4
        self.base._next_input_register = self.input_register + 5

    @_CpxEModule._require_base
    def read_channels(self) -> list[int]:
        '''read all channels as a list of integer values
        '''
        # TODO: add signal conversion according to signalrange of the channel
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        signed_integers = [self.signed16_to_int(x) for x in raw_data]
        return signed_integers

    @_CpxEModule._require_base
    def read_status(self) -> list[bool]:
        '''read module status register. Further information see module datasheet
        '''
        data = self.base.read_reg_data(self.input_register + 4)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @_CpxEModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]

    @_CpxEModule._require_base
    def write_channels(self, data: list[int]) -> None:
        '''write data to module channels in ascending order
        '''
        # TODO: scaling to given signalrange
        reg_data = [self.int_to_signed16(x) for x in data]
        self.base.write_reg_data(reg_data, self.output_register, length=4)

    @_CpxEModule._require_base
    def write_channel(self, channel: int, data: int) -> None:
        '''write data to module channel number
        '''
        # TODO: scaling to given signalrange
        reg_data = self.int_to_signed16(data)
        self.base.write_reg_data(reg_data, self.output_register + channel)

    @_CpxEModule._require_base
    def set_channel_range(self, channel: int, signalrange: str):
        '''set the signal range and type of one channel
        '''
        bitmask = {
            "0-10V": 0b0001,
            "-10-+10V": 0b0010,
            "-5-+5V": 0b0011,
            "1-5V": 0b0100,
            "0-20mA": 0b0101,
            "4-20mA": 0b0110,
            "-20-+20mA": 0b0111
        }
        if signalrange not in bitmask:
            raise ValueError(f"'{signalrange}' is not an option. Choose from {bitmask.keys()}")

        function_number = 4828 + 64 * self.position

        if channel == 0:
            function_number += 11
            self._signalrange_01 |= bitmask[signalrange]
            value_to_write = self._signalrange_01
        elif channel == 1:
            function_number += 11
            self._signalrange_01 |= bitmask[signalrange]
            value_to_write = self._signalrange_01
        elif channel == 2:
            function_number += 12
            self._signalrange_23 |= bitmask[signalrange]
            value_to_write = self._signalrange_23
        elif channel == 3:
            function_number += 12
            self._signalrange_23 |= bitmask[signalrange]
            value_to_write = self._signalrange_23
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")

        self.base.write_function_number(function_number, value_to_write)


# TODO: Add IO-Link module
