"""AP module dataclasses"""

from dataclasses import dataclass


@dataclass
class SystemParameters:
    """SystemParameters"""

    # pylint: disable=too-many-instance-attributes
    dhcp_enable: bool = None
    ip_address: str = None
    subnet_mask: str = None
    gateway_address: str = None
    active_ip_address: str = None
    active_subnet_mask: str = None
    active_gateway_address: str = None
    mac_address: str = None
    setup_monitoring_load_supply: int = None


@dataclass
class ApddInformation:
    """ApddInformation"""

    # pylint: disable=too-many-instance-attributes
    description: str
    name: str
    module_type: str
    configurator_code: str
    part_number: str
    module_class: str
    module_code: str
    order_text: str
    product_category: str
    product_family: str


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


@dataclass
class ModuleDiagnosis:
    """ModuleDiagnosis dataclass"""

    description: str
    diagnosis_id: str
    guideline: str
    name: str


@dataclass
class Channels:
    """Channels dataclass"""

    inputs: list
    outputs: list
    inouts: list


@dataclass
class ModuleDicts:
    """ModuleDicts dataclass"""

    parameters: dict
    diagnosis: dict
