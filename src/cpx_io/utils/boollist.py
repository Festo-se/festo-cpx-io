"""Helper functions for converting lists of boolean values"""


def bytes_to_boollist(data: bytes, num_bytes: int = None, byteorder="little") -> list:
    """Converts data in byte representation to a list of bools"""
    # Compose list of single bytes
    chunkeddata = [data[i : i + 1] for i in range(0, len(data), 1)]

    if byteorder == "big":
        chunkeddata = chunkeddata[::-1]

    # Compose a list of single boolean values
    boollist = sum(
        (
            [int.from_bytes(chunk, "little") >> i & 1 == 1 for i in range(8)]
            for chunk in chunkeddata
        ),
        [],
    )

    if num_bytes is None:
        num_bytes = len(data)

    if num_bytes > len(data):
        boollist += [False] * ((num_bytes - len(data)) * 8)

    boollist = boollist[: num_bytes * 8]

    return boollist


def boollist_to_bytes(boollist: list) -> bytes:
    """Converts a list of bools to byte representation"""
    # Compose list of chunks of 8 bools
    chunkedlist = [boollist[i : i + 8] for i in range(0, len(boollist), 8)]
    # Compose a list where every chunk is an int
    intlist = [
        sum(int(bit) << position for (position, bit) in enumerate(chunk))
        for chunk in chunkedlist
    ]
    return bytes(intlist)


def boollist_to_int(boollist: list) -> int:
    """Converts a list of bools to int representation"""
    return int.from_bytes(boollist_to_bytes(boollist), byteorder="little")


def int_to_boollist(number: int) -> list:
    """Converts an int to a list of bool values"""
    num_bytes = (number.bit_length() + 7) // 8
    return bytes_to_boollist(number.to_bytes(num_bytes, byteorder="little"))
