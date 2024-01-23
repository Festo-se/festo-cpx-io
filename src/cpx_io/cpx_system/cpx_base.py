"""CPX Base
"""

import struct
from dataclasses import dataclass, fields
from functools import wraps

from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
from cpx_io.utils.logging import Logging
from cpx_io.utils.boollist import boollist_to_bytes, bytes_to_boollist


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

    def __init__(self, ip_address: str = None):
        """Constructor of CpxBase class.

        Parameters:
            ip_address (str): Required IP address as string e.g. ('192.168.1.1')
        """
        if ip_address is None:
            Logging.logger.info("Not connected since no IP address was provided")
            return

        self.client = ModbusTcpClient(host=ip_address)
        self.client.connect()
        Logging.logger.info(f"Connected to {ip_address}:502")

    def shutdown(self):
        """Shutdown function"""
        if hasattr(self, "client"):
            self.client.close()
            Logging.logger.info("Connection closed")
        else:
            Logging.logger.info("No connection to close")
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

    @dataclass
    class _BitwiseReg:
        """Register functions"""

        byte_size = None

        @classmethod
        def from_bytes(cls, data: bytes):
            """Initializes a BitwiseWord from a byte representation"""
            return cls(*bytes_to_boollist(data))

        @classmethod
        def from_int(cls, value: int):
            """Initializes a BitwiseWord from an integer"""
            return cls.from_bytes(value.to_bytes(cls.byte_size, "little"))

        def to_bytes(self):
            """Returns the bytes representation"""
            blist = [getattr(self, v.name) for v in fields(self)]
            return boollist_to_bytes(blist)

        def __int__(self):
            """Returns the integer representation"""
            return int.from_bytes(self.to_bytes(), "little")

    class BitwiseReg8(_BitwiseReg):
        """Half Register"""

        byte_size: int = 1

    class BitwiseReg16(_BitwiseReg):
        """Full Register"""

        byte_size: int = 2

    def read_reg_data(self, register: int, length: int = 1) -> list[int]:
        """Reads and returns register from Modbus server

        :param register: adress of the first register to read
        :type register: int
        :param length: number of registers to read (default: 1)
        :type length: int
        :return: Register content
        :rtype: list[int]
        """

        data = self.client.read_holding_registers(register, length)

        if data.isError():
            raise ValueError("Reading modbus failed")

        return data.registers

    def write_reg_data(
        self, data: int | list[int], register: int, length: int = 1
    ) -> None:
        """Write data to registers. If data is int, writes one register.
        If data is list, list content is written to given register address and following registers

        :param data: data to write to the register
        :type data: int | list[int]
        :param register: adress of the first register to read
        :type register: int
        :param length: number of registers to read (default: 1)
        :type length: int

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
    def require_base(func):
        """For most module functions, a base is required that handles the registers,
        module numbering, etc."""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.base:
                raise CpxInitError()
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def encode_int(data: int, data_type="int16", byteorder="big"):
        """Encode the content of one register to the given data_type"""
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
        elif data_type == "bool":
            builder.add_16bit_uint(int(data) << 4)
        else:
            raise NotImplementedError(f"Type {data_type} not implemented")

        return builder.to_registers()

    @staticmethod
    def _swap_bytes(registers):
        """Swap bytes. This is needed due to a bug in pymodbus
        Byteorder does not work for strings. https://github.com/riptideio/pymodbus/issues/508
        """
        swapped = []
        for reg_item in registers:
            k = struct.pack("<H", reg_item)
            k = int.from_bytes(k, byteorder="big", signed=False)
            swapped.append(k)
        return swapped

    @staticmethod
    def decode_string(registers: list[int]) -> BinaryPayloadDecoder:
        """Decode the register content to string"""
        # swap_bytes has to be used because of a bug in pymodbus
        decoder = BinaryPayloadDecoder.fromRegisters(
            CpxBase._swap_bytes(registers), byteorder=Endian.BIG
        )
        return decoder.decode_string(34).decode("ascii").strip("\x00")

    @staticmethod
    def decode_int(
        registers: list[int], data_type="uint16", byteorder="big"
    ) -> BinaryPayloadDecoder:
        """Decode the register content to integer"""
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
        if data_type == "uint16":
            return decoder.decode_16bit_uint()
        if data_type == "uint32":
            return decoder.decode_32bit_uint()
        if data_type == "int8":
            return decoder.decode_8bit_int()
        if data_type == "int16":
            return decoder.decode_16bit_int()
        if data_type == "int32":
            return decoder.decode_32bit_int()

        raise NotImplementedError(f"Type {data_type} not implemented")

    @staticmethod
    def decode_bool(registers: list[int]) -> bool:
        """Decode the register content to bool"""
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers[::-1], byteorder=Endian.BIG
        )
        return bool(decoder.decode_8bit_uint() & 0x01)

    @staticmethod
    def decode_hex(registers: list[int], data_type="uint16") -> str:
        """Decode the register content to hex string"""
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers[::-1], byteorder=Endian.BIG
        )
        if data_type == "uint16":
            return format(decoder.decode_16bit_uint(), "#010x")
        raise NotImplementedError(f"Type {data_type} not implemented")
