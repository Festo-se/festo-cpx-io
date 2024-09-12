"""ModuleDicts dataclass"""

from dataclasses import dataclass


@dataclass
class ModuleDicts:
    """Dictionaries of the module"""

    parameters: dict
    diagnosis: dict
