"""CPX SystemEntryRegisters dataclass"""

from dataclasses import dataclass


@dataclass
class SystemEntryRegisters:
    """Initial modbus registers of the AP system"""

    inputs: int = None
    outputs: int = None
    diagnosis: int = None
