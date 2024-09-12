"""CPX SystemEntryRegisters dataclass"""

from dataclasses import dataclass


@dataclass
class SystemEntryRegisters:
    """SystemEntryRegisters dataclass"""

    inputs: int = None
    outputs: int = None
    diagnosis: int = None
