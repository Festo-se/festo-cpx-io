"""SystemParameters dataclass"""

from dataclasses import dataclass


@dataclass
class SystemParameters:
    """Parameters of the system"""

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
