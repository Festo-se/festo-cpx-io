"""CPX-AP-EP module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers


class CpxApEp(CpxApModule):
    """Class for CPX-AP-EP module"""

    module_codes = {
        8323: "default",
    }

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = cpx_ap_registers.OUTPUTS[0]
        self.base.next_input_register = cpx_ap_registers.INPUTS[0]

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    @staticmethod
    def convert_uint32_to_octett(value: int) -> str:
        """Convert one uint32 value to octett. Usually used for displaying ip addresses."""
        return f"{value & 0xFF}.{(value >> 8) & 0xFF}.{(value >> 16) & 0xFF}.{(value) >> 24 & 0xFF}"

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        raise NotImplementedError(
            "CPX-AP-EP module has no AP parameters. Use 'read_parameters()' instead"
        )

    @CpxBase.require_base
    def read_parameters(self):
        """Read parameters from EP module"""
        dhcp_enable = CpxBase.decode_bool(
            self.base.read_parameter(self.position, 12000, 0)
        )

        ip_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12001, 0), data_type="uint32"
        )
        ip_address = self.convert_uint32_to_octett(ip_address)

        subnet_mask = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12002, 0), data_type="uint32"
        )
        subnet_mask = self.convert_uint32_to_octett(subnet_mask)

        gateway_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12003, 0), data_type="uint32"
        )
        gateway_address = self.convert_uint32_to_octett(gateway_address)

        active_ip_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12004, 0), data_type="uint32"
        )
        active_ip_address = self.convert_uint32_to_octett(active_ip_address)

        active_subnet_mask = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12005, 0), data_type="uint32"
        )
        active_subnet_mask = self.convert_uint32_to_octett(active_subnet_mask)

        active_gateway_address = CpxBase.decode_int(
            self.base.read_parameter(self.position, 12006, 0), data_type="uint32"
        )
        active_gateway_address = self.convert_uint32_to_octett(active_gateway_address)

        mac_address = ":".join(
            f"{x & 0xFF:02x}:{(x >> 8):02x}"
            for x in self.base.read_parameter(self.position, 12007, 0)
        )

        setup_monitoring_load_supply = CpxBase.decode_int(
            [(self.base.read_parameter(self.position, 20022, 0)[0]) & 0xFF],
            data_type="uint8",
        )

        return {
            "dhcp_enable": dhcp_enable,
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "gateway_address": gateway_address,
            "active_ip_address": active_ip_address,
            "active_subnet_mask": active_subnet_mask,
            "active_gateway_address": active_gateway_address,
            "mac_address": mac_address,
            "setup_monitoring_load_supply": setup_monitoring_load_supply,
        }
