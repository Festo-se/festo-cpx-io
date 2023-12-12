"""Helper functions"""


def div_ceil(x: int, y: int) -> int:
    """Divides two integers and returns the ceiled result"""
    return (x + y - 1) // y
