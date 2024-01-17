"""CPX-AP-*-EP module implementation"""

from dataclasses import dataclass
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.utils.helpers import convert_uint32_to_octett, convert_octett_to_uint32


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
        dhcp_enable: bool = None
        ip_address: str = None
        subnet_mask: str = None
        gateway_address: str = None
        active_ip_address: str = None
        active_subnet_mask: str = None
        active_gateway_address: str = None
        mac_address: str = None
        setup_monitoring_load_supply: int = None

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
    def read_parameters(self) -> Parameters:
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

    @CpxBase.require_base
    def write_parameters(self, params: Parameters) -> None:
        """Write parameters to EP module"""

        if params.dhcp_enable is not None:
            self.base.write_parameter(self.position, 12000, 0, params.dhcp_enable)

        if params.ip_address is not None:
            value = convert_octett_to_uint32(params.ip_address)
            registers = [
                value & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF,
            ]
            self.base.write_parameter(self.position, 12001, 0, registers)

        if params.subnet_mask is not None:
            value = convert_octett_to_uint32(params.subnet_mask)
            registers = [
                value & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF,
            ]
            self.base.write_parameter(self.position, 12002, 0, registers)

        if params.gateway_address is not None:
            value = convert_octett_to_uint32(params.gateway_address)
            registers = [
                value & 0xFF,
                (value >> 8) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 24) & 0xFF,
            ]
            self.base.write_parameter(self.position, 12003, 0, registers)

        if params.setup_monitoring_load_supply is not None:
            self.base.write_parameter(
                self.position, 20022, 0, params.setup_monitoring_load_supply
            )
