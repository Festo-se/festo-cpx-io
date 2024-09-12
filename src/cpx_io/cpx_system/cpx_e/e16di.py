"""CPX-E-16DI module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_enums import DebounceTime, SignalExtension


class CpxE16Di(CpxModule):
    """Class for CPX-E-16DI module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.base.next_input_register = self.system_entry_registers.inputs + 2

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values

        :return: Values of all channels
        :rtype: list[bool]
        """
        data = self.base.read_reg_data(self.system_entry_registers.inputs)
        ret = bytes_to_boollist(data)
        Logging.logger.info(f"{self.name}: Reading channels: {ret}")
        return ret

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel

        :param channel: Channel number, starting with 0
        :type channel: int
        :return: Value of the channel
        :rtype: bool"""
        return self.read_channels()[channel]

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
    def configure_diagnostics(self, value: bool) -> None:
        """
        The "Diagnostics of sensor supply short circuit" defines whether the diagnostics of
        the sensor supply in regard to short circuit or overload should be activated
        ("True", default) or deactivated (False). When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.

        :param value: diagnostics of sensor supply short circuit
        :type value: int
        """
        function_number = 4828 + 64 * self.position + 0
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)
        Logging.logger.info(
            f"{self.name}: Setting diagnostics of sensor supply short circuit to {value}"
        )

    @CpxBase.require_base
    def configure_power_reset(self, value: bool) -> None:
        """
        "Behaviour after SCO" parameter defines whether the voltage remains switched off
        ("False") or automatically switches on again ("True", default) after a short circuit
        or overload of the sensor supply. In the case of the "Leave power switched off" setting,
        the CPX-E automation system must be switched off and on to restore the power.

        :param value: behaviour after sco
        :type value: int
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)
        Logging.logger.info(f"{self.name}: Setting behaviour after sco to {value}")

    @CpxBase.require_base
    def configure_debounce_time(self, value: DebounceTime | int) -> None:
        """
        The "Input debounce time" parameter defines when an edge change of the sensor signal
        shall be assumed as a logical input signal. In this way, unwanted signal edge changes
        can be suppressed during switching operations (bouncing of the input signal).

            * 0: 0.1 ms
            * 1: 3 ms (default)
            * 2: 10 ms
            * 3: 20 ms

        :param value: Debounce time for all channels. Use DebounceTime from cpx_e_enums or
        see datasheet.
        :type value: DebounceTime | int
        """
        if isinstance(value, DebounceTime):
            value = value.value

        value_range_check(value, 4)

        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register, delete bit 4+5 from it
        # and refill it with value
        value_to_write = (reg & 0xCF) | (value << 4)

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Setting debounce time to {value}")

    @CpxBase.require_base
    def configure_signal_extension_time(self, value: SignalExtension | int) -> None:
        """
        The "Signal extension time" parameter defines the minimum valid duration of the assumed
        signal status of the input signal. Edge changes within the signal extension time are
        ignored. Short input signals can also be recorded by defining a signal extension time.

          * 0: 0.5 ms
          * 1: 15 ms (default)
          * 2: 50 ms
          * 3: 100 ms

        :param value: Signal extension time
        :type value: SignalExtension | int
        """
        if isinstance(value, SignalExtension):
            value = value.value

        value_range_check(value, 4)

        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register, delete bit 6+7 from it
        # and refill it with value
        value_to_write = (reg & 0x3F) | (value << 6)

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Setting signal extension time to {value}")
