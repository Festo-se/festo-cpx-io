from dataclasses import dataclass


@dataclass
class Parameter:
    """Parameter dataclass"""

    parameter_id: int
    array_size: int
    data_type: str
    default_value: int
    description: str
    name: str
