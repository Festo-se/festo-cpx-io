"""Contains functions which provide mapping of parameter types."""

import struct
from typing import Any
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters

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
    "ENUM_ID": "H",  # interpret ENUM_ID as UINT16
}


def parameter_unpack(
    parameter: cpx_ap_parameters.ApParameter, raw: bytes, forced_format: str = None
) -> Any:
    """Unpacks a raw byte value to specific type.
    The type is determined by the parameters included in cpx_ap_parameters.

    param parameter: Parameter that should be unpacked.
    type parameter: ApParameter
    param raw: Raw bytes value that should be unpacked.
    type raw: bytes
    param forced_format: Optional format char (see struct) to force the unpacking strategy.
    type forced_format: str
    return: Unpacked value with determined type
    rtype: Any
    """
    array_size = 1
    if forced_format:
        Logging.logger.info(f"Parameter {parameter} forced to type ({forced_format})")
        unpack_data_type = forced_format
    else:
        parameter_data_type = parameter.dtype
        Logging.logger.info(f"Parameter {parameter} is of type {parameter_data_type}")

        # if "Arraysize" is given, set array_size
        if "[" in parameter_data_type:
            parameter_data_type, array_size = parameter_data_type.rstrip("]").split("[")
            array_size = int(array_size)
            unpack_data_type = (
                f"{array_size * TYPE_TO_FORMAT_CHAR[parameter_data_type]}"
            )

        else:
            unpack_data_type = TYPE_TO_FORMAT_CHAR[parameter_data_type]

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
    parameter: cpx_ap_parameters.ApParameter, value: Any, forced_format: str = None
) -> bytes:
    """Packs a provided value to raw bytes object.
    The type is determined by the parameters included in cpx_ap_parameters.

     param parameter: Parameter of value that should be unpacked.
     type parameter: ApParameter
     param value: Value that should be packed.
     type value: Any
     param forced_format: Optional format char (see struct) to force the packing strategy.
     type forced_format: str

     return: Packed value
     rtype: bytes
    """
    if not forced_format:
        array_size = 1
        parameter_data_type = parameter.dtype
        Logging.logger.info(f"Parameter {parameter} is of type {parameter_data_type}")

        # for char arrays, ignore the "Arraysize" and use length of the bytes object instead
        if "CHAR" in parameter_data_type:
            return struct.pack("s", bytes(value, encoding="ascii"))

        # handle arrays
        if "[" in parameter_data_type:
            parameter_data_type, array_size = parameter_data_type.rstrip("]").split("[")
            array_size = int(array_size)
            if array_size != len(value):
                Logging.logger.warning(
                    f"Length of value {value} does not fit length of ApParameter ({array_size})"
                )
            pack_data_type = f"{array_size * TYPE_TO_FORMAT_CHAR[parameter_data_type]}"
        else:
            pack_data_type = TYPE_TO_FORMAT_CHAR[parameter_data_type]

        if "INT" in parameter_data_type:
            value = int(value)
        if "FLOAT" in parameter_data_type:
            value = float(value)
        if "BOOL" in parameter_data_type:
            value = bool(value)

        if any(type_str in parameter_data_type for type_str in ["INT8", "BOOL"]):
            # bool and uint8 needs to be in MSbyte, so fill it with 0
            return struct.pack(pack_data_type, value) + b"\x00"

        return struct.pack(pack_data_type, value)

    Logging.logger.info(f"Parameter {parameter} forced to type ({forced_format})")
    return struct.pack(forced_format, value)
