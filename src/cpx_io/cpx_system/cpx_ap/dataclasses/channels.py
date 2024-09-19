"""Channels dataclass"""

from dataclasses import dataclass


@dataclass
class Channels:
    """Channels of the module"""

    inputs: list
    outputs: list
    inouts: list
