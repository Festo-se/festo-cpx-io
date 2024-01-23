"""CPX-E-8DO module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule
from cpx_io.utils.boollist import int_to_boollist, boollist_to_int
from cpx_io.utils.logging import Logging


class CpxE8Do(CpxEModule):
    """Class for CPX-E-8DO module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = self.output_register + 1
        self.base.next_input_register = self.input_register + 2

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values"""
        data = self.base.read_reg_data(self.input_register)[0]
        return int_to_boollist(data, num_bytes=1)

    @CpxBase.require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values"""
        if len(data) != 8:
            raise ValueError(f"Data len error: expected: 8, got: {len(data)}")
        integer_data = boollist_to_int(data)
        self.base.write_reg_data(integer_data, self.output_register)

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet

        :return: status information (see datasheet)
        :rtype: list[bool]"""
        data = self.base.read_reg_data(self.input_register + 1)[0]
        ret = int_to_boollist(data, 2)
        Logging.logger.info(f"{self.name}: Reading status: {ret}")
        return ret

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value"""
        data = self.base.read_reg_data(self.input_register)[0]  # read current value
        mask = 1 << channel  # Compute mask, an integer with just bit 'channel' set.
        data &= ~mask  # Clear the bit indicated by the mask
        if value:
            data |= mask  # If x was True, set the bit indicated by the mask.

        self.base.write_reg_data(data, self.output_register)

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level"""
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level"""
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level"""
        data = (
            self.base.read_reg_data(self.input_register)[0] & 1 << channel
        ) >> channel
        if data == 1:
            self.clear_channel(channel)
        elif data == 0:
            self.set_channel(channel)
        else:
            raise ValueError(f"Value {data} must be between 0 and 1")

    @CpxBase.require_base
    def configure_diagnostics(self, short_circuit=None, undervoltage=None):
        """
        The "Diagnostics of short circuit at output" parameter defines whether
        the diagnostics of the outputs in regard to short circuit or
        overload should be activated or deactivated.
        The "Diagnostics of undervoltage at load supply" parameter defines
        if the diagnostics for the load supply must be activated or
        deactivated with regard to undervoltage.
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.
        """
        function_number = 4828 + 64 * self.position + 0
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if short_circuit is None:
            short_circuit = bool((reg & 0x02) >> 1)
        if undervoltage is None:
            undervoltage = bool((reg & 0x04) >> 2)

        mask = 0xF9
        value_to_write = (
            reg & mask | (int(short_circuit) << 1) | (int(undervoltage) << 2)
        )

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_power_reset(self, value: bool):
        """
        The "Behaviour after SCO" parameter defines whether
        the voltage remains switched off ("False", default) or
        automatically switches on ("True") again after a short circuit or overload at the outputs.
        In the case of the "Leave power switched off" setting,
        the CPX-E automation system must be switched off and on or
        the corresponding output must be reset and to restore the power.
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x02
        else:
            value_to_write = reg & 0xFD

        self.base.write_function_number(function_number, value_to_write)
