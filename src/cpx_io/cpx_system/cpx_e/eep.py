"""CPX-E-EP module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.cpx_system.cpx_e import cpx_e_registers


class CpxEEp(CpxModule):
    """Class for CPX-E-EP module"""

    # pylint: disable=too-few-public-methods

    def configure(self, base, position):
        self.base = base
        self.position = position

        self.system_entry_registers.outputs = (
            cpx_e_registers.PROCESS_DATA_OUTPUTS.register_address
        )
        self.system_entry_registers.inputs = (
            cpx_e_registers.PROCESS_DATA_INPUTS.register_address
        )

        self.base.next_output_register = self.system_entry_registers.outputs + 2
        self.base.next_input_register = self.system_entry_registers.inputs + 3

        Logging.logger.debug(
            f"Configured {self} with output register {self.system_entry_registers.outputs}"
            f"and input register {self.system_entry_registers.inputs}"
        )
