'''TODO: Add module docstring
'''

import logging
import struct

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .cpx_base import CpxBase, CpxInitError

class _ModbusCommands:   
    '''Modbus start adresses used to read and write registers
    ''' 
    # holding registers
    outputs=(0,4096)
    inputs=(5000,4096)
    parameter=(10000,1000)

    diagnosis=(11000,100)
    module_count=(12000,1)

    # module information
    module_code=(15000,2) # (+37*n)
    module_class=(15002,1) # (+37*n)
    communication_profiles=(15003,1) # (+37*n)
    input_size=(15004,1) # (+37*n)
    input_channels=(15005,1) # (+37*n)
    output_size=(15006,1) # (+37*n)
    output_channels=(15007,1) # (+37*n)
    hw_version=(15008,1) # (+37*n)
    fw_version=(15009,3) # (+37*n)
    serial_number=(15012,2) # (+37*n)
    product_key=(15014,6) # (+37*n)
    order_text=(15020,17) # (+37*n)


class CpxAp(CpxBase):
    '''CPX-AP base class
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._next_output_register = None
        self._next_input_register = None
        self._modules = []

        module_count = self.read_module_count()
        for i in range(module_count):
            self.add_module(information=self.read_module_information(i))

    @property
    def modules(self):
        return self._modules
    
    def add_module(self, information:dict):
        '''Adds one module to the base. This is required to use the module.
        The module must be identified by either the module code {"Module Code": 8323}
        or the full module order text {"Order Text": "CPX-AP-I-EP-M12"}
        '''
        module_code = information.get("Module Code")
        order_text = information.get("Order Text")

        if module_code == 8323 or order_text == 'CPX-AP-I-EP-M12':
            module = CpxApEp()
        elif module_code == 8199 or order_text == 'CPX-AP-I-8DI-M8-3P':
            module = CpxAp8Di()
        elif module_code == 8197 or order_text == 'CPX-AP-I-4DI4DO-M12-5P':
            module = CpxAp4Di4Do()
        elif module_code == 8202 or order_text == 'CPX-AP-I-4AI-U-I-RTD-M12':
            module = CpxAp4AiUI()
        elif module_code == 8201 or order_text == 'CPX-AP-I-4IOL-M12':
            module = CpxAp4Iol()
        elif module_code == 8198 or order_text == 'CPX-AP-I-4DI-M8-3P':
            module = CpxAp4Di()
        else:
            raise NotImplementedError("This module is not yet implemented or not available")
    
        module._update_information(information)
        module._initialize(self, len(self._modules))
        self.modules.append(module)
        return module

    def write_data(self, register, val):
         #TODO: Not tested yet!!!
         status = object
         print(f"{register}, {val}")
         try:
             if val < 0:
                 val = val + 2**16
             self.client.write_register(register, val, unit=self.deviceConfig['modbusSlave'])
             status = self.client.read_input_registers(_ModbusCommands.StatusWord, count=1, unit=self.deviceConfig['modbusSlave']) 
             while (status.registers[0] & 1) == 1:
                 status = self.client.read_input_registers(_ModbusCommands.StatusWord, 1, unit=self.deviceConfig['modbusSlave'])
         except Exception as e:
             print("error while writing : ", str(e)) 

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer
        """
        return self.read_reg_data(*_ModbusCommands.module_count)[0]

    def _module_offset(self, modbusCommand, module):
        register, length = modbusCommand
        return ((register + 37 * module), length)

    def _swap_bytes(self, registers):
        swapped = []
        for r in registers:
            k = struct.pack('<H', r)
            k = int.from_bytes(k, byteorder='big', signed=False)
            swapped.append(k)
        return swapped

    def _decode_string(self, registers):
        # _swap_bytes has to be used because of a bug in pymodbus! 
        # Byteorder does not work for strings. https://github.com/riptideio/pymodbus/issues/508
        decoder = BinaryPayloadDecoder.fromRegisters(self._swap_bytes(registers), byteorder=Endian.BIG) 
        return decoder.decode_string(34).decode('ascii').strip("\x00")

    def _decode_serial(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG)
        return format(decoder.decode_16bit_uint(), "#010x")
    
    def _decodeHex(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG)
        return format(decoder.decode_16bit_uint(), "#010x")

    def read_module_information(self, position):
        """Reads and returns detailed information for a specific IO module
        """
        logging.debug(f"read_module_information for module on position {position}")

        module_code = int(self._decode_serial(self.read_reg_data(*self._module_offset(_ModbusCommands.module_code, position))), 16)
        module_class = self.read_reg_data(*self._module_offset(_ModbusCommands.module_class, position))[0]
        communication_profiles = self.read_reg_data(*self._module_offset(_ModbusCommands.communication_profiles, position))[0]
        input_size = self.read_reg_data(*self._module_offset(_ModbusCommands.input_size, position))[0]
        input_channels = self.read_reg_data(*self._module_offset(_ModbusCommands.input_channels, position))[0]
        output_size = self.read_reg_data(*self._module_offset(_ModbusCommands.output_size, position))[0]
        output_channels = self.read_reg_data(*self._module_offset(_ModbusCommands.output_channels, position))[0]
        hW_version = self.read_reg_data(*self._module_offset(_ModbusCommands.hw_version, position))[0]
        fW_version = ".".join(str(x) for x in self.read_reg_data(*self._module_offset(_ModbusCommands.fw_version, position)))
        serial_number = self._decode_serial(self.read_reg_data(*self._module_offset(_ModbusCommands.serial_number, position)))
        product_key = self._decode_string(self.read_reg_data(*self._module_offset(_ModbusCommands.product_key, position)))
        order_text = self._decode_string(self.read_reg_data(*self._module_offset(_ModbusCommands.order_text, position)))

        return {
            "Module Code": module_code,
            "Module Class": module_class,
            "Communication Profiles": communication_profiles,
            "Input Size": input_size,
            "Input Channels": input_channels,
            "Output Size": output_size,
            "Output Channeles": output_channels,
            "HW Version": hW_version,
            "FW Version": fW_version,
            "Serial Number": serial_number,
            "Product Key": product_key,
            "Order Text": order_text,
            }

    def read_module_data(self, module):
        """Reads and returns process data of a specific IO module
        
        Arguments:
        module -- Number of the IO module
        """
        logging.debug("read_module_information for module {}".format(module))

        moduleCode = self.information[module]["Module Code"]
        moduleInputSize = self.information[module]["Input Size"]//2
        moduleOffset = self._get_module_offset(module)

        logging.info("order Text: {}".format(self.information[module]["Order Text"]))
        logging.info("module Code: {}".format(moduleCode))
        logging.info("module InputSize: {}".format(moduleInputSize))
        logging.info("module Offset: {}".format(moduleOffset))

        if(moduleCode == 8323): # CPX-AP-I-EP-M12
            return None
        
        if(moduleCode == 8202): # CPX-AP-I-4AI-U-I-RTD-M12
            moduleData = self.read_reg_data(moduleOffset, moduleInputSize)
            logging.debug("moduleData: {}".format(moduleData))

            decoder = BinaryPayloadDecoder.fromRegisters(moduleData, byteorder=Endian.Little)
            moduleDataHex = [hex(decoder.decode_16bit_uint()) for i in range(len(moduleData))]
            return {
                "channels": [
                    moduleData[0], 
                    moduleData[1], 
                    moduleData[2], 
                    moduleData[3]
                ],
                "raw": moduleDataHex, 
                "registers": moduleData
                }
       
        if(moduleCode == 8212): # CPX-AP-I-4IOL-M12
            moduleData = self.read_reg_data(moduleOffset, moduleInputSize)
            logging.debug("moduleData: {}".format(moduleData))

            decoder = BinaryPayloadDecoder.fromRegisters(moduleData, byteorder=Endian.Little)
            moduleDataHex = [hex(decoder.decode_16bit_uint()) for i in range(len(moduleData))]

            channelSize = (moduleInputSize-2)//4
            return {
                "channels": [
                    moduleData[:channelSize*1],
                    moduleData[channelSize*1:channelSize*2],
                    moduleData[channelSize*2:channelSize*3],
                    moduleData[channelSize*3:]
                ],
                "raw": moduleDataHex,
                "registers": moduleData
                }
        
        if(moduleCode == 8199): #CPX-AP-I-8DI-M8-3P
            moduleData = self.read_reg_data(moduleOffset, 1)
            logging.debug("moduleData: {}".format(moduleData))

            moduleDataBin = bin(moduleData)[2:].zfill(8)
            return {"channels": [bool(int(md)) for md in moduleDataBin[::-1]], "raw": hex(moduleData)}


class _CpxApModule(CpxAp):
    '''Base class for cpx-ap modules
    '''
    def __init__(self):
        self.base = None
        self.position = None
        self.information = None

        self.output_register = None
        self.input_register = None

    def _initialize(self, base, position):
        self.base = base
        self.position = position

    def _update_information(self, information):
        self.information = information

    @staticmethod
    def _require_base(func):
        def wrapper(self, *args, **kwargs):
            if not self.base:
                raise CpxInitError()
            return func(self, *args, **kwargs)
        return wrapper


class CpxApEp(_CpxApModule):
    '''Class for CPX-AP-EP module
    '''
    def _initialize(self, *args):
        super()._initialize(*args)
        self.output_register = _ModbusCommands.outputs[0]
        self.input_register = _ModbusCommands.inputs[0]

        self.base._next_output_register = self.output_register
        self.base._next_input_register = self.input_register
        

class CpxAp4Di(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += self.information["Output Size"]
        self.base._next_input_register += self.information["Input Size"]
        
    @_CpxApModule._require_base
    def read_channels(self) -> list[bool]:
        '''read all channels as a list of bool values
        '''    
        data = self.base.read_reg_data(self.input_register, 1)[0]
        logging.debug("data: {}".format(data))

        dataBin = bin(data)[2:].zfill(4)
        return [bool(int(d)) for d in dataBin[::-1]]

    @_CpxApModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]
    

class CpxAp8Di(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += self.information["Output Size"]
        self.base._next_input_register += self.information["Input Size"]
        
    @_CpxApModule._require_base
    def read_channels(self) -> list[bool]:
        '''read all channels as a list of bool values
        '''
        
        data = self.base.read_reg_data(self.input_register, 1)[0]
        logging.debug("data: {}".format(data))

        dataBin = bin(data)[2:].zfill(8)
        return [bool(d) for d in dataBin[::-1]]

    @_CpxApModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]
    

class CpxAp4AiUI(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += self.information["Output Size"]
        self.base._next_input_register += self.information["Input Size"]

    @_CpxApModule._require_base
    def read_channels(self) -> list[int]:
        '''read all channels as a list of (signed) integers
        '''
        # TODO
        pass

    @_CpxApModule._require_base
    def read_channel(self, channel: int) -> bool:
        '''read back the value of one channel
        '''
        return self.read_channels()[channel]


class CpxAp4Di4Do(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += self.information["Output Size"]
        self.base._next_input_register += self.information["Input Size"]
        #raise NotImplementedError("The module CPX-AP-4DI4DO has not yet been implemented")


class CpxAp4Iol(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += self.information["Output Size"]
        self.base._next_input_register += self.information["Input Size"]
        #raise NotImplementedError("The module CPX-AP-4IOL-M12 has not yet been implemented")
