"""CPX Base
"""

import struct

from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
from cpx_io.utils.logging import Logging


class CpxInitError(Exception):
    """
    Error should be raised if a cpx-... module
    is instanciated without connecting it to a base module.
    Connect it to the cpx by adding it with add_module(<object instance>)
    """

    def __init__(
        self, message="Module must be part of a Cpx class. Use add_module() to add it"
    ):
        super().__init__(message)


class CpxRequestError(Exception):
    """Error should be raised if a parameter or register request is denied"""

    def __init__(self, message="Request failed"):
        super().__init__(message)


class CpxBase:
    """A class to connect to the Festo CPX system and read data from IO modules"""

    def __init__(self, ip_address=None, port=502, timeout=1):
        if ip_address is None:
            Logging.logger.info("Not connected since no IP address was provided")
            return

        self.client = ModbusTcpClient(
            host=ip_address,
            port=port,
            timeout=timeout,
        )

        self.client.connect()
        Logging.logger.info(f"Connected to {ip_address}:{port} (timeout: {timeout})")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
        Logging.logger.info("Disconnected")
        return False

    def read_reg_data(self, register: int, length=1) -> list:
        """Reads and returns register from Modbus server

        Arguments:
        register -- adress of the first register to read
        length -- number of registers to read (default: 1)
        """

        data = self.client.read_holding_registers(register, length)

        if data.isError():
            raise ValueError("Reading modbus failed")

        return data.registers

    def write_reg_data(self, data: int | list, register: int, length=1):
        """Write data to registers. If data is int, writes one register.
        If data is list, list content is written to given register address and following registers

        """
        if isinstance(data, int):
            for i in range(0, length):
                self.client.write_register(register + i, data)

        elif isinstance(data, list):
            for i, data_item in enumerate(data):
                self.client.write_register(register + i, data_item)
        else:
            raise TypeError("data must be of type int or list")

    @staticmethod
    def _require_base(func):
        def wrapper(self, *args, **kwargs):
            if not self.base:
                raise CpxInitError()
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def swap_bytes(registers):
        swapped = []
        for reg_item in registers:
            k = struct.pack("<H", reg_item)
            k = int.from_bytes(k, byteorder="big", signed=False)
            swapped.append(k)
        return swapped

    @staticmethod
    def encode_int(data: int, data_type="int16", byteorder="big"):
        if byteorder == "little":
            byteorder = Endian.LITTLE
        else:
            byteorder = Endian.BIG

        builder = BinaryPayloadBuilder(byteorder=byteorder)
        if data_type == "uint8":
            builder.add_8bit_uint(data)
        elif data_type == "uint16":
            builder.add_16bit_uint(data)
        elif data_type == "uint32":
            builder.add_32bit_uint(data)
        elif data_type == "int8":
            builder.add_8bit_int(data)
        elif data_type == "int16":
            builder.add_16bit_int(data)
        elif data_type == "int32":
            builder.add_32bit_int(data)
        else:
            raise NotImplementedError(f"Type {data_type} not implemented")

        return builder.to_registers()

    @staticmethod
    def decode_string(registers):
        # swap_bytes has to be used because of a bug in pymodbus!
        # Byteorder does not work for strings. https://github.com/riptideio/pymodbus/issues/508
        decoder = BinaryPayloadDecoder.fromRegisters(
            CpxBase.swap_bytes(registers), byteorder=Endian.BIG
        )
        return decoder.decode_string(34).decode("ascii").strip("\x00")

    @staticmethod
    def decode_int(registers, data_type="uint16", byteorder="big"):
        if byteorder == "little":
            byteorder = Endian.LITTLE
        else:
            byteorder = Endian.BIG

        # on 8 bit types, the data have to be shifted to MSByte for correct decoding
        if data_type in ("uint8", "int8"):
            registers = [(registers[0] & 0xFF) << 8]

        decoder = BinaryPayloadDecoder.fromRegisters(
            registers[::-1], byteorder=byteorder
        )

        if data_type == "uint8":
            return decoder.decode_8bit_uint()
        elif data_type == "uint16":
            return decoder.decode_16bit_uint()
        elif data_type == "uint32":
            return decoder.decode_32bit_uint()
        elif data_type == "int8":
            return decoder.decode_8bit_int()
        elif data_type == "int16":
            return decoder.decode_16bit_int()
        elif data_type == "int32":
            return decoder.decode_32bit_int()
        else:
            raise NotImplementedError(f"Type {data_type} not implemented")

    @staticmethod
    def decode_bool(registers):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers[::-1], byteorder=Endian.BIG
        )
        return bool(decoder.decode_bits(0))

    @staticmethod
    def decode_hex(registers, data_type="uint16"):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG)
        if data_type == "uint16":
            return format(decoder.decode_16bit_uint(), "#010x")
        raise NotImplementedError(f"Type {data_type} not implemented")

    """not needed?
    @staticmethod
    def decode_float(registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.LITTLE)
        return [decoder.decode_32bit_float() for _ in registers]
    """
