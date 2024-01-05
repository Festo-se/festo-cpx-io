"""CPX-AP-EP module implementation"""

from dataclasses import dataclass
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.utils.helpers import convert_uint32_to_octett


class CpxApEp(CpxApModule):
    """Class for CPX-AP-EP module"""

    module_codes = {
        8323: "default",
    }

    @dataclass
    class Parameters:
        """System parameters"""

        # pylint: disable=too-many-instance-attributes
        dhcp_enable: bool
        ip_address: str
        subnet_mask: str
        gateway_address: str
        active_ip_address: str
        active_subnet_mask: str
        active_gateway_address: str
        mac_address: str
        setup_monitoring_load_supply: int

    def configure(self, base, position):
        self.base = base
        self.position = position

        self.output_register = None
        self.input_register = None

        self.base.next_output_register = cpx_ap_registers.OUTPUTS[0]
        self.base.next_input_register = cpx_ap_registers.INPUTS[0]

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    @CpxBase.require_base
    def read_parameters(self):
        """Read parameters from EP module"""

        params = self.__class__.Parameters

        params.dhcp_enable = CpxBase.decode_bool(
            self.base.read_parameter(self.position, 12000, 0)
        )

        ip_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12001, 0), data_type="uint32"
        )
        params.ip_address = convert_uint32_to_octett(ip_address)

        subnet_mask = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12002, 0), data_type="uint32"
        )
        params.subnet_mask = convert_uint32_to_octett(subnet_mask)

        gateway_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12003, 0), data_type="uint32"
        )
        params.gateway_address = convert_uint32_to_octett(gateway_address)

        active_ip_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12004, 0), data_type="uint32"
        )
        params.active_ip_address = convert_uint32_to_octett(active_ip_address)

        active_subnet_mask = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12005, 0), data_type="uint32"
        )
        params.active_subnet_mask = convert_uint32_to_octett(active_subnet_mask)

        active_gateway_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12006, 0), data_type="uint32"
        )
        params.active_gateway_address = convert_uint32_to_octett(active_gateway_address)

        params.mac_address = ":".join(
            f"{x & 0xFF:02x}:{(x >> 8):02x}"
            for x in self.base.read_parameter(self.position, 12007, 0)
        )

        params.setup_monitoring_load_supply = CpxBase.decode_int(
            [(self.base.read_parameter(self.position, 20022, 0)[0]) & 0xFF],
            data_type="uint8",
        )

        return params
