"""Contains functions which provide mapping of parameter types."""

import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any
from cpx_io.utils.logging import Logging


@dataclass
class Parameter:
    """Parameter dataclass"""

    # pylint: disable=too-many-instance-attributes
    parameter_id: int
    parameter_instances: dict
    is_writable: bool
    array_size: int
    data_type: str
    default_value: int
    description: str
    name: str
    unit: str = ""
    enums: dict = None

    def __repr__(self):
        return (
            f"{self.parameter_id:<8}"
            f"{self.name:<50}"
            f"{'R/W' if self.is_writable else 'R':<6}"
            f"{self.data_type:<8}"
            f"{self.enums if self.enums else ''}"
        )


@dataclass
class ParameterEnum:
    """ParameterEnum dataclass"""

    enum_id: int
    bits: int
    data_type: str
    enum_values: Enum
    ethercat_enum_id: int
    name: str

    def __repr__(self):
        return f"{self.enum_values}"


TYPE_TO_FORMAT_CHAR = {
    "BOOL": "?",
    "INT8": "b",
    "INT16": "h",
    "INT32": "i",
    "INT64": "q",
    "UINT8": "B",
    "UINT16": "H",
    "UINT32": "I",
    "UINT64": "Q",
    "FLOAT": "f",
    "CHAR": "s",
}


def parameter_unpack(
    parameter: Parameter, raw: bytes, forced_format: str = None
) -> Any:
    """Unpacks a raw byte value to specific type.
    The type is determined by the parameters included in ParameterMap.

    param parameter: Parameter that should be unpacked.
    type parameter: Parameter
    param raw: Raw bytes value that should be unpacked.
    type raw: bytes
    param forced_format: Optional format char (see struct) to force the unpacking strategy.
    type forced_format: str
    return: Unpacked value with determined type
    rtype: Any
    """
    array_size = parameter.array_size if parameter.array_size else 1

    if forced_format:
        Logging.logger.info(f"Parameter {parameter} forced to type ({forced_format})")
        unpack_data_type = forced_format
    else:
        if parameter.data_type == "ENUM_ID":
            parameter_data_type = parameter.enums.data_type
        else:
            parameter_data_type = parameter.data_type
        Logging.logger.info(f"Parameter {parameter} is of type {parameter_data_type}")

        unpack_data_type = f"<{array_size * TYPE_TO_FORMAT_CHAR[parameter_data_type]}"

    if "s" in unpack_data_type:
        # for strings, ignore array_size and use length of bytes instead
        value = (
            struct.unpack(f"{len(raw)}{TYPE_TO_FORMAT_CHAR['CHAR']}", raw)[0]
            .decode("ascii")
            .strip("\x00")
        )

    elif any(char in unpack_data_type for char in "?bB"):
        value = struct.unpack(unpack_data_type, raw[:array_size])
    else:
        value = struct.unpack(unpack_data_type, raw)

    if len(value) == 1:
        return value[0]

    return value


def parameter_pack(
    parameter: Parameter, value: Any, forced_format: str = None
) -> bytes:
    """Packs a provided value to raw bytes object.
    The type is determined by the parameters included in ParameterMap.

     param parameter: Parameter of value that should be unpacked.
     type parameter: Parameter
     param value: Value that should be packed.
     type value: Any
     param forced_format: Optional format char (see struct) to force the packing strategy.
     type forced_format: str

     return: Packed value
     rtype: bytes
    """
    if not forced_format:
        array_size = parameter.array_size if parameter.array_size else 1

        if parameter.data_type == "ENUM_ID":
            parameter_data_type = parameter.enums.data_type
        else:
            parameter_data_type = parameter.data_type
        Logging.logger.info(f"Parameter {parameter} is of type {parameter_data_type}")

        # for char arrays, ignore the "Arraysize" and use length of the bytes object instead
        # but check for the size and return index error if too long
        if "CHAR" in parameter_data_type:
            if len(value) > parameter.array_size:
                raise IndexError(
                    f"Value {value} is too long for Parameter {parameter.name}."
                    f"Allowed size is {parameter.array_size} bytes"
                )
            return bytes(value, encoding="ascii")

        pack_data_type = f"<{array_size * TYPE_TO_FORMAT_CHAR[parameter_data_type]}"

        if "INT" in parameter_data_type:
            value = int(value)
        if "FLOAT" in parameter_data_type:
            value = float(value)
        if "BOOL" in parameter_data_type:
            value = bool(value)

        return struct.pack(pack_data_type, value)

    Logging.logger.info(f"Parameter {parameter} forced to type ({forced_format})")
    return struct.pack(forced_format, value)
