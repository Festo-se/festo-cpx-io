"""AP Channels dataclass"""

from dataclasses import dataclass


@dataclass
class Channels:
    """Channels dataclass"""

    inputs: list
    outputs: list
    inouts: list
