__author__ = "Plank, Martin"
__copyright__ = "Copyright 2022, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Plank, Martin"
__email__ = "martin.plank@festo.com"
__status__ = "Development"


from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

import logging
import struct

from cpx_base import CPX_BASE

class _ModbusCommands:    
#input registers
#holding registers
    Diagnosis=(11000,100)
    ModuleCount=(12000,1)
    ModuleCode=(15000,2) # (+37*n)
    ModuleClass=(15002,1) # (+37*n)
    CommunicationProfiles=(15003,1) # (+37*n)
    InputSize=(15004,1) # (+37*n)
    InputChannels=(15005,1) # (+37*n)
    OutputSize=(15006,1) # (+37*n)
    OutputChanneles=(15007,1) # (+37*n)
    HWVersion=(15008,1) # (+37*n)
    FWVersion=(15009,3) # (+37*n)
    SerialNumber=(15012,2) # (+37*n)
    ProductKey=(15014,6) # (+37*n)
    OrderText=(15020,16) # (+37*n)

class CPX_AP(CPX_BASE):
    """
    A class to connect to the Festo CPX-AP-I-EP-M12 and read data from IO modules

    Attributes:
        moduleCount -- Integer representing the IO module count (read on `__init__()` or `readStaticInformation()`)
        moduleInformation -- List with detail for the modules (read on `__init__()` or `readStaticInformation()`)

    Methods:
        readRegData(self, register, length=1, type="holding_register") -- Reads and returns holding or input register from Modbus server
        readInputRegData(self, register, length=1) -- Reads and returns input registers from Modbus server
        readHoldingRegData(self, register, length=1) -- Reads and returns holding registers form Modbus server
        readModuleCount(self) -- Reads and returns IO module count
        readModuleInformation(self, module) -- Reads and returns detailed information for a specific IO module
        readStaticInformation(self) -- Manualy reads and updates the class attributes `moduleCount` and `moduleInformation`
        readModuleData(self, module) -- Reads and returns process data of a specific IO module
    """
    def __init__(self):
        # TODO: Is this really neccessary?
        self.readStaticInformation()

    def writeData(self, register, val):
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

    def readModuleCount(self):
        """Reads and returns IO module count
        """
        return self.readHoldingRegData(*_ModbusCommands.ModuleCount)

    def _moduleOffset(self, modbusCommand, module):
        register, length = modbusCommand
        return ((register + 37 * module), length)

    def _swap_bytes(self, registers):
        swapped = []
        for r in registers:
            k = struct.pack('<H', r)
            k = int.from_bytes(k, 'big', signed=False)
            swapped.append(k)
        return swapped

    def _decodeString(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(self._swap_bytes(registers), byteorder=Endian.Big) #Bug in pymodbus! Byteorder does not work for strings. https://github.com/riptideio/pymodbus/issues/508
        return decoder.decode_string(34).decode('ascii').strip("\x00")

    def _decodeSerial(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big)
        return format(decoder.decode_16bit_uint(), "#010x")

    def readModuleInformation(self, module):
        """Reads and returns detailed information for a specific IO module
        
        Arguments:
        module -- Number of the IO module
        """
        logging.debug("readModuleInformation for module {}".format(module))

        moduleCode = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.ModuleCode, module))[0]
        moduleClass = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.ModuleClass, module))
        communicationProfiles = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.CommunicationProfiles, module))
        inputSize = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.InputSize, module))
        inputChannels = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.InputChannels, module))
        outputSize = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.OutputSize, module))
        outputChanneles = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.OutputChanneles, module))
        hWVersion = self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.HWVersion, module))
        fWVersion = ".".join(str(x) for x in self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.FWVersion, module)))
        serialNumber = self._decodeSerial(self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.SerialNumber, module)))
        productKey = self._decodeString(self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.ProductKey, module)))
        orderText = self._decodeString(self.readHoldingRegData(*self._moduleOffset(_ModbusCommands.OrderText, module)))

        return {
            "ModuleCode": moduleCode,
            "ModuleClass": moduleClass,
            "CommunicationProfiles": communicationProfiles,
            "InputSize": inputSize,
            "InputChannels": inputChannels,
            "OutputSize": outputSize,
            "OutputChanneles": outputChanneles,
            "HWVersion": hWVersion,
            "FWVersion": fWVersion,
            "SerialNumber": serialNumber,
            "ProductKey": productKey,
            "OrderText": orderText,
            }

    def readStaticInformation(self):
        """Manualy reads and updates the class attributes `moduleCount` and `moduleInformation`
        """
        logging.debug("readStaticInformation")
        self.moduleCount = self.readModuleCount()
        
        self.moduleInformation = []
        for i in range(self.moduleCount):
            self.moduleInformation.append(self.readModuleInformation(i))

    def _getModuleOffset(self, module):
        offset = 5000
        for i in range(module):
            moduleCode = self.moduleInformation[i]["ModuleCode"]
            moduleInputSize = self.moduleInformation[i]["InputSize"]
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
        logging.debug("readModuleInformation for module {}".format(module))

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
            moduleData = self.readHoldingRegData(moduleOffset, moduleInputSize)
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
            moduleData = self.readHoldingRegData(moduleOffset, moduleInputSize)
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
            moduleData = self.readHoldingRegData(moduleOffset, 1)
            logging.debug("moduleData: {}".format(moduleData))

            moduleDataBin = bin(moduleData)[2:].zfill(8)
            return {"channels": [bool(int(md)) for md in moduleDataBin[::-1]], "raw": hex(moduleData)}

    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
