"""CPX-E-EP module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule
from cpx_io.cpx_system.cpx_e import cpx_e_definitions


class CpxEEp(CpxEModule):
    """Class for CPX-E-EP module"""

    # pylint: disable=too-few-public-methods

    def configure(self, base, position):
        self.base = base
        self.position = position

        self.output_register = cpx_e_definitions.PROCESS_DATA_OUTPUTS.register_address
        self.input_register = cpx_e_definitions.PROCESS_DATA_INPUTS.register_address

        self.base.next_output_register = self.output_register + 2
        self.base.next_input_register = self.input_register + 3

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register}"
            f"and input register {self.input_register}"
        )
