"""Helper functions"""


def div_ceil(x_val: int, y_val: int) -> int:
    """Divides two integers and returns the ceiled result"""
    return (x_val + y_val - 1) // y_val


def convert_uint32_to_octett(value: int) -> str:
    """Convert one uint32 value to octett. Usually used for displaying ip addresses."""
    return f"{(value >> 24) & 0xFF}.{(value >> 16) & 0xFF}.{(value >> 8) & 0xFF}.{(value) & 0xFF}"


def convert_octett_to_uint32(octetts: str) -> int:
    """Convert octett string to 32 bit value. Usually used for converting ip addresses."""
    str_list = octetts.split(".")
    return (
        int(str_list[0] << 24)
        | (int(str_list[1]) << 16)
        | (int(str_list[2]) << 8)
        | (int(str_list[3]) << 0)
    )


def convert_to_mac_string(values: list[int]) -> str:
    """Convert list of uint8 to mac adderss string."""
    return ":".join(format(x, "02x") for x in values)

def unwrap_cpxe_typecode(typecode: str) -> str:
    """Takes care of the cpx-e typecode merging more than two of the same module
    type into a number. For example MMM will be merged to 3M while MM stays."""
    typecode_header = typecode[:7]
    typecode_config = typecode[7:]

    if typecode_header == "60E-EP-":
        result = ""
        i = 0
        while i < len(typecode_config):
            if typecode_config[i].isdigit():
                num = ""
                while i < len(typecode_config) and typecode_config[i].isdigit():
                    num += typecode_config[i]
                    i += 1
                result += typecode_config[i] * int(num)
            else:
                result += typecode_config[i]
            i += 1
        return typecode_header + result

    raise TypeError("Your CPX-E configuration must include the Ethernet/IP "
                    "Busmodule to be compatible with this software")

def module_list_from_typecode(typecode: str, module_id_dict: dict) -> list:
    """Creates a module list from a provided typecode."""
    module_list = []
    typecode = unwrap_cpxe_typecode(typecode)
    for i in range(len(typecode)):
        substring = typecode[i:]
        for key, value in module_id_dict.items():
            if substring.startswith(key):
                module_list.append(value())

    return module_list


def _args_to_start_stop(args):
    """If one argument is provided, will check range(0, arg)
    If two arguments are provided, will check range(arg[0], arg[1])"""
    num_args = len(args)
    if num_args == 0:
        raise TypeError("Expected at least 1 argument, got 0")
    if num_args == 1:
        start = 0
        stop = args[0]
    elif num_args == 2:
        start = args[0]
        stop = args[1]
    else:
        raise TypeError(f"Expected at most 2 arguments, got {num_args}")
    return (start, stop)


def value_range_check(value: int, *args):
    """Raises ValueError if value is not in the given range."""

    start, stop = _args_to_start_stop(args)

    if value not in range(start, stop):
        raise ValueError(f"Value {value} must be in range({start}, {stop})")


def channel_range_check(channel: int, *args):
    """Raises IndexError if channel is not in the given range."""

    start, stop = _args_to_start_stop(args)

    if channel not in range(start, stop):
        raise IndexError(f"Channel {channel} must be in range({start}, {stop})")


def instance_range_check(instance: int, *args):
    """Raises IndexError if instance is not in the given range."""

    start, stop = _args_to_start_stop(args)

    if instance not in range(start, stop):
        raise IndexError(f"Instance {instance} must be in range({start}, {stop})")
