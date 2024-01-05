"""Helper functions"""


def div_ceil(x: int, y: int) -> int:
    """Divides two integers and returns the ceiled result"""
    return (x + y - 1) // y


def convert_uint32_to_octett(value: int) -> str:
    """Convert one uint32 value to octett. Usually used for displaying ip addresses."""
    return f"{value & 0xFF}.{(value >> 8) & 0xFF}.{(value >> 16) & 0xFF}.{(value) >> 24 & 0xFF}"
