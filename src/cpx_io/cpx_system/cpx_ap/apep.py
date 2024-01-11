"""CPX-AP-*-EP module implementation"""

from dataclasses import dataclass
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.utils.helpers import convert_uint32_to_octett


class CpxApEp(CpxApModule):
    """Class for CPX-AP-*-EP module"""

    module_codes = {
        8323: "CPX-AP-I-EP",
        12421: "CPX-AP-A-EP",
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

        self.base.next_output_register = cpx_ap_registers.OUTPUTS.register_address
        self.base.next_input_register = cpx_ap_registers.INPUTS.register_address

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    @CpxBase.require_base
    def read_parameters(self):
        """Read parameters from EP module"""

        params = self.__class__.Parameters(
            dhcp_enable=CpxBase.decode_bool(
                self.base.read_parameter(self.position, 12000, 0)
            ),
            ip_address=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12001, 0),
                    data_type="uint32",
                )
            ),
            subnet_mask=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12002, 0),
                    data_type="uint32",
                )
            ),
            gateway_address=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12003, 0),
                    data_type="uint32",
                )
            ),
            active_ip_address=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12004, 0),
                    data_type="uint32",
                )
            ),
            active_subnet_mask=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12005, 0),
                    data_type="uint32",
                )
            ),
            active_gateway_address=convert_uint32_to_octett(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 12006, 0),
                    data_type="uint32",
                )
            ),
            mac_address=":".join(
                f"{x & 0xFF:02x}:{(x >> 8):02x}"
                for x in self.base.read_parameter(self.position, 12007, 0)
            ),
            setup_monitoring_load_supply=CpxBase.decode_int(
                [(self.base.read_parameter(self.position, 20022, 0)[0]) & 0xFF],
                data_type="uint8",
            ),
        )
        return params
