"""CPX-AP-`*`-EP module implementation"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.utils.helpers import (
    convert_uint32_to_octett,
    convert_to_mac_string,
    value_range_check,
)
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import LoadSupply


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
        the ParameterMap.

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
                self.position, ParameterNameMap()["dhcpenable"]
            ),
            ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, ParameterNameMap()["ipaddress"])
            ),
            subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["subnetmask"]
                ),
            ),
            gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["gatewayAddress"]
                )
            ),
            active_ip_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["ipaddressActive"]
                )
            ),
            active_subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["subnetmaskActive"]
                )
            ),
            active_gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["gatewayActive"]
                )
            ),
            mac_address=convert_to_mac_string(
                self.base.read_parameter(
                    self.position, ParameterNameMap()["macAddress"]
                )
            ),
            setup_monitoring_load_supply=self.base.read_parameter(
                self.position, ParameterNameMap()["LoadSupplyDiagSetup"]
            )
            & 0xFF,
        )
        Logging.logger.info(f"{self.name}: Reading parameters: {params}")
        return params

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: LoadSupply | int) -> None:
        """Configures the monitoring load supply for all channels.

          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Monitoring load supply for all channels. Use LoadSupply from cpx_ap_enums
        or see datasheet.
        :type value: LoadSupply | int
        """

        if isinstance(value, LoadSupply):
            value = value.value

        value_range_check(value, 3)

        self.base.write_parameter(
            self.position, ParameterNameMap()["LoadSupplyDiagSetup"], value
        )

        Logging.logger.info(f"{self.name}: Setting Load supply monitoring to {value}")
