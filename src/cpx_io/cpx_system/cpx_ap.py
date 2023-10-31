'''TODO: Add module docstring
'''

import logging
import struct

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from .cpx_base import CpxBase

class _ModbusCommands:   
    '''Modbus start adresses used to read and write registers
    ''' 
    #input registers

    #holding registers
    diagnosis=(11000,100)
    module_count=(12000,1)

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


class CpxAP(CpxBase):
    '''CPX-AP base class
    '''
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

    def read_module_information(self, module):
        """Reads and returns detailed information for a specific IO module
        
        Arguments:
        module -- Number of the IO module
        """
        logging.debug(f"read_module_information for module {module}")

        module_code = int(self._decode_serial(self.read_reg_data(*self._module_offset(_ModbusCommands.module_code, module))), 16)
        module_class = self.read_reg_data(*self._module_offset(_ModbusCommands.module_class, module))[0]
        communication_profiles = self.read_reg_data(*self._module_offset(_ModbusCommands.communication_profiles, module))[0]
        input_size = self.read_reg_data(*self._module_offset(_ModbusCommands.input_size, module))[0]
        input_channels = self.read_reg_data(*self._module_offset(_ModbusCommands.input_channels, module))[0]
        output_size = self.read_reg_data(*self._module_offset(_ModbusCommands.output_size, module))[0]
        output_channels = self.read_reg_data(*self._module_offset(_ModbusCommands.output_channels, module))[0]
        hW_version = self.read_reg_data(*self._module_offset(_ModbusCommands.hw_version, module))[0]
        fW_version = ".".join(str(x) for x in self.read_reg_data(*self._module_offset(_ModbusCommands.fw_version, module)))
        serial_number = self._decode_serial(self.read_reg_data(*self._module_offset(_ModbusCommands.serial_number, module)))
        product_key = self._decode_string(self.read_reg_data(*self._module_offset(_ModbusCommands.product_key, module)))
        order_text = self._decode_string(self.read_reg_data(*self._module_offset(_ModbusCommands.order_text, module)))

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

    # TODO: Needed?
    #def update_static_information(self):
    #    """Manualy reads and updates the class attributes `module count` and `moduleInformation`
    #    """
    #    logging.debug("update_static_information")
    #    self.module_count = self.read_module_count()
    #    
    #    self.module_information = []
    #    for i in range(self.module_count):
    #        self.module_information.append(self.read_module_information(i))

    def _getModuleOffset(self, module):
        offset = 5000
        for i in range(module):
            moduleCode = self.moduleInformation[i]["Module Code"]
            moduleInputSize = self.moduleInformation[i]["Input Size"]
            if(moduleCode == 8199): #CPX-AP-I-8DI-M8-3P
                offset += 1
            else:
                offset += moduleInputSize//2
        return (offset)
    
    def _decodeHex(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big)
        return format(decoder.decode_16bit_uint(), "#010x")

    def readModuleData(self, module):
        """Reads and returns process data of a specific IO module
        
        Arguments:
        module -- Number of the IO module
        """
        logging.debug("read_module_information for module {}".format(module))

        moduleCode = self.moduleInformation[module]["ModuleCode"]
        moduleInputSize = self.moduleInformation[module]["InputSize"]//2
        moduleOffset = self._getModuleOffset(module)

        logging.info("orderText: {}".format(self.moduleInformation[module]["OrderText"]))
        logging.info("moduleCode: {}".format(moduleCode))
        logging.info("moduleInputSize: {}".format(moduleInputSize))
        logging.info("moduleOffset: {}".format(moduleOffset))

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

    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
