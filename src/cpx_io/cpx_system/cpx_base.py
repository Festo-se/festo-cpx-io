"""CPX Base
"""

import struct
from dataclasses import dataclass, fields
from functools import wraps

from pymodbus.client import ModbusTcpClient
from pymodbus.pdu.mei_message import ReadDeviceInformationRequest
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

        :param ip_address: Required IP address as string e.g. ('192.168.1.1')
        :type ip_address: str
        """
        self._modules = []
        self._module_names = []
        self.base = None
        self.ip_address = ip_address

        if ip_address is None:
            Logging.logger.info("Not connected since no IP address was provided")
            return

        self.client = ModbusTcpClient(host=ip_address)
        if self.client.connect():
            Logging.logger.info(f"Connected to {ip_address}:502")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

    def update_module_names(self):
        """Updates the module name list and attributes accordingly"""
        for name in self._module_names:
            delattr(self, name)

        self._module_names = [module.name for module in self._modules]
        for name, module in zip(self._module_names, self._modules):
            setattr(self, name, module)

    def shutdown(self):
        """Shutdown function"""
        if hasattr(self, "client"):
            self.client.close()
            Logging.logger.info("Connection closed")
        else:
            Logging.logger.info("No connection to close")
        return False

    def read_device_info(self) -> dict:
        """Reads device info from the CPX system and returns dict with containing values

        return: Contains device information values
        rtype: dict
        """
        dev_info = {}

        # Read device information
        rreq = ReadDeviceInformationRequest(0x1, 0)
        rres = self.client.execute(rreq)
        dev_info["vendor_name"] = rres.information[0].decode("ascii")
        dev_info["product_code"] = rres.information[1].decode("ascii")
        dev_info["revision"] = rres.information[2].decode("ascii")

        rreq = ReadDeviceInformationRequest(0x2, 0)
        rres = self.client.execute(rreq)
        dev_info["vendor_url"] = rres.information[3].decode("ascii")
        dev_info["product_name"] = rres.information[4].decode("ascii")
        dev_info["model_name"] = rres.information[5].decode("ascii")

        for key, value in dev_info.items():
            Logging.logger.info(f"{key.replace('_',' ').title()}: {value}")

        return dev_info

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

    def read_reg_data(self, register: int, length: int = 1) -> bytes:
        """Reads and returns register(s) from Modbus server without interpreting the data

        :param register: adress of the first register to read
        :type register: int
        :param length: number of registers to read (default: 1)
        :type length: int
        :return: Register(s) content
        :rtype: bytes
        """

        response = self.client.read_holding_registers(register, length)

        if response.isError():
            raise ConnectionAbortedError(response.message)

        data = struct.pack("<" + "H" * len(response.registers), *response.registers)
        return data

    def write_reg_data(self, data: bytes, register: int) -> None:
        """Write bytes object data to register(s).

        :param data: data to write to the register(s)
        :type data: bytes
        :param register: adress of the first register to write
        :type register: int
        """
        # if odd number of bytes, add one zero byte
        if len(data) % 2 != 0:
            data += b"\x00"
        # Convert to list of words
        reg = list(struct.unpack("<" + "H" * (len(data) // 2), data))
        # Write data
        self.client.write_registers(register, reg)

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
