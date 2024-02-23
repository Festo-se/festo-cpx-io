"""CPX-AP-`*`-EP module implementation"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.utils.helpers import (
    convert_uint32_to_octett,
    convert_to_mac_string,
)
from cpx_io.utils.logging import Logging


class CpxApEp(CpxApModule):
    """Class for CPX-AP-`*`-EP module"""

    module_codes = {
        8323: "CPX-AP-I-EP",
        12421: "CPX-AP-A-EP",
    }

    @dataclass
    class Parameters:
        """System parameters"""

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

    def configure(self, base: CpxBase, position: int) -> None:
        """Setup a module with the according base and position in the system.
        This overwrites the inherited configure function because the Busmodule -EP is
        always on position 0 in the system and needs to pull its registers directly from
        the cpx_ap_parameters.

        :param base: Base module that implements the modbus functions
        :type base: CpxBase
        :param position: Module position in CPX-AP system starting with 0 for Busmodule
        :type position: int
        """
        self.base = base
        self.position = position

        if self.position != 0:
            Logging.logger.warning(
                f"{self} is not on module position 0. Check if this intended"
            )

        self.output_register = None
        self.input_register = None

        self.base.next_output_register = cpx_ap_registers.OUTPUTS.register_address
        self.base.next_input_register = cpx_ap_registers.INPUTS.register_address

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    @CpxBase.require_base
    def read_parameters(self) -> Parameters:
        """Read parameters from EP module

        :return: Parameters object containing all r/w parameters
        :rtype: Parameters
        """
        params = self.__class__.Parameters(
            dhcp_enable=self.base.read_parameter(
                self.position, cpx_ap_parameters.DHCP_ENABLE
            ),
            ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, cpx_ap_parameters.IP_ADDRESS)
            ),
            subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(self.position, cpx_ap_parameters.SUBNET_MASK),
            ),
            gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.GATEWAY_ADDRESS
                )
            ),
            active_ip_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.IP_ADDRESS_ACTIVE
                )
            ),
            active_subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.SUBNET_MASK_ACTIVE
                )
            ),
            active_gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.GATEWAY_ACTIVE
                )
            ),
            mac_address=convert_to_mac_string(
                self.base.read_parameter(self.position, cpx_ap_parameters.MAC_ADDRESS)
            ),
            setup_monitoring_load_supply=self.base.read_parameter(
                self.position, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP
            )
            & 0xFF,
        )
        Logging.logger.info(f"{self.name}: Reading parameters: {params}")
        return params

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Configure the monitoring of the load supply.

        Accepted values are
          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Setting of monitoring of load supply in range 0..3 (see datasheet)
        :type value: int
        """

        if not 0 <= value <= 2:
            raise ValueError(f"Value {value} must be between 0 and 2")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP, value
        )

        value_str = [
            "inactive",
            "active, diagnosis suppressed in case of switch-off",
            "active",
        ]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")
