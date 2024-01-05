"""Helper functions for converting lists of boolean values"""


def bytes_to_boollist(data: bytes, num_bytes: int = None):
    """Converts data in byte representation to a list of bools"""
    # Compose list of single bytes
    chunkeddata = [data[i : i + 1] for i in range(0, len(data), 1)]
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


def boollist_to_bytes(boollist: list):
    """Converts a list of bools to byte representation"""
    # Compose list of chunks of 8 bools
    chunkedlist = [boollist[i : i + 8] for i in range(0, len(boollist), 8)]
    # Compose a list where every chunk is an int
    intlist = [
        sum(int(bit) << position for (position, bit) in enumerate(chunk))
        for chunk in chunkedlist
    ]
    return bytes(intlist)


def int_to_boollist(data: int, num_bytes: int = None):
    """Converts integer data to a list of bools"""
    if num_bytes is None:
        # round up to nearest whole byte
        num_bytes = (data.bit_length() + 7) // 8

    return [d == "1" for d in bin(data)[2:].zfill(num_bytes * 8)[::-1]]


def boollist_to_int(boollist: list):
    """Converts list of bools to integer"""
    # Make binary from list of bools
    binary_string = "".join("1" if value else "0" for value in reversed(boollist))
    # Convert the binary string to an integer
    return int(binary_string, 2)
