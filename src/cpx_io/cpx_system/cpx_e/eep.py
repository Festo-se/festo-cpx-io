"""CPX-E-EP module implementation"""

from cpx_io.utils.logging import Logging
import cpx_io.cpx_system.cpx_e.cpx_e_registers as cpx_e_registers
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule


class CpxEEp(CpxEModule):
    """Class for CPX-E-EP module"""

    def configure(self, *args):
        super().configure(*args)

        self.output_register = cpx_e_registers.PROCESS_DATA_OUTPUTS[0]
        self.input_register = cpx_e_registers.PROCESS_DATA_INPUTS[0]

        self.base.next_output_register = self.output_register + 2
        self.base.next_input_register = self.input_register + 3

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register}"
            f"and input register {self.input_register}"
        )
