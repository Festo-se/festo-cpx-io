"""CPX dataclasses"""

from dataclasses import dataclass


@dataclass
class StartRegisters:
    """Registers dataclass"""

    inputs: int = None
    outputs: int = None
    diagnosis: int = None
