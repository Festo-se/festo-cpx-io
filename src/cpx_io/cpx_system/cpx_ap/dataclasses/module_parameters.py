"""ModuleParameters dataclass"""

from dataclasses import dataclass


@dataclass
class ModuleParameters:
    """AP Parameters of module"""

    # pylint: disable=too-many-instance-attributes
    fieldbus_serial_number: int
    product_key: str
    firmware_version: str
    module_code: int
    temp_asic: int
    logic_voltage: float
    load_voltage: float
    hw_version: int
    io_link_variant: str = "n.a."
    operating_supply: bool = False
