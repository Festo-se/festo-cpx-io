"""CPX-E-EP module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_modbus_commands import (
    ModbusCommands,
)
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule


class CpxEEp(CpxEModule):
    """Class for CPX-E-EP module"""

    def configure(self, *args):
        super().configure(*args)

        self.output_register = ModbusCommands.process_data_outputs[0]
        self.input_register = ModbusCommands.process_data_inputs[0]

        self.base.next_output_register = self.output_register + 2
        self.base.next_input_register = self.input_register + 3

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register} and input register {self.input_register}"
        )
