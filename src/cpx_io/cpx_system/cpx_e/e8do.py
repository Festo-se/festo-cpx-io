"""CPX-E-8DO module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.logging import Logging


class CpxE8Do(CpxModule):
    """Class for CPX-E-8DO module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = self.system_entry_registers.outputs + 1
        self.base.next_input_register = self.system_entry_registers.inputs + 2

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values

        :return: Values of all channels
        :rtype: list[bool]
        """
        data = self.base.read_reg_data(self.system_entry_registers.inputs)
        ret = bytes_to_boollist(data, num_bytes=1)
        Logging.logger.info(f"{self.name}: Reading channels: {ret}")
        return ret

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel

        :param channel: Channel number, starting with 0
        :type channel: int
        :return: Value of the channel
        :rtype: bool
        """
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values

        :param data: list of bool values containing exactly 4 elements for each output channel
        :type data: list[bool]
        """
        if len(data) != 8:
            raise ValueError(f"Data len error: expected: 8, got: {len(data)}")
        integer_data = boollist_to_bytes(data)
        self.base.write_reg_data(integer_data, self.system_entry_registers.outputs)

        Logging.logger.info(f"{self.name}: Setting channels to {data}")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: bool
        """
        data = bytes_to_boollist(
            self.base.read_reg_data(self.system_entry_registers.outputs)
        )
        data[channel] = value
        reg = boollist_to_bytes(data)
        self.base.write_reg_data(reg, self.system_entry_registers.outputs)

        Logging.logger.info(f"{self.name}: Setting channel {channel} to {value}")

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet

        :return: status information (see datasheet)
        :rtype: list[bool]"""
        data = self.base.read_reg_data(self.system_entry_registers.inputs + 1)
        ret = bytes_to_boollist(data)
        Logging.logger.info(f"{self.name}: Reading status: {ret}")
        return ret

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        # get the relevant value from the register and write the inverse
        value = self.read_channel(channel)
        self.write_channel(channel, not value)

    @CpxBase.require_base
    def configure_diagnostics(
        self, short_circuit: bool = None, undervoltage: bool = None
    ) -> None:
        """
        The "Diagnostics of short circuit at output" parameter defines whether
        the diagnostics of the outputs in regard to short circuit or
        overload should be activated or deactivated.
        The "Diagnostics of undervoltage at load supply" parameter defines
        if the diagnostics for the load supply must be activated or
        deactivated with regard to undervoltage.
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.

        :param short_circuit: diagnostics of short circuit
        :type short_circuit: bool
        :param undervoltage: diagnostics of undervoltage
        :type undervoltage: bool
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
        Logging.logger.info(
            f"{self.name}: Writing diagnostics parameter short circuit: {short_circuit}, "
            f"undervoltage: {undervoltage}"
        )

    @CpxBase.require_base
    def configure_power_reset(self, value: bool):
        """
        The "Behaviour after SCO" parameter defines whether
        the voltage remains switched off ("False", default) or
        automatically switches on ("True") again after a short circuit or overload at the outputs.
        In the case of the "Leave power switched off" setting,
        the CPX-E automation system must be switched off and on or
        the corresponding output must be reset and to restore the power.

        :param value: behaviour after power reset
        :type value: bool
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x02
        else:
            value_to_write = reg & 0xFD

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(
            f"{self.name}: Setting behaviour after power reset to {value}"
        )
