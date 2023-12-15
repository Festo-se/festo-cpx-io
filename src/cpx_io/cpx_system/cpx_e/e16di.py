"""CPX-E-16DI module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule


class CpxE16Di(CpxEModule):
    """Class for CPX-E-16DI module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base.next_input_register

        self.base.next_input_register = self.input_register + 2

        Logging.logger.debug(
            f"Configured {self} with input register {self.input_register}"
        )

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values"""
        data = self.base.read_reg_data(self.input_register)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet"""
        data = self.base.read_reg_data(self.input_register + 1)[0]
        return [d == "1" for d in bin(data)[2:].zfill(16)[::-1]]

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def configure_diagnostics(self, value: bool) -> None:
        """
        The "Diagnostics of sensor supply short circuit" defines whether
        the diagnostics of the sensor supply in regard to short circuit or
        overload should be activated ("True", default) or deactivated (False).
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.
        """
        function_number = 4828 + 64 * self.position + 0
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_power_reset(self, value: bool) -> None:
        """
        "Behaviour after SCO" parameter defines whether
        the voltage remains switched off ("False") or
        automatically switches on again ("True", default)
        after a short circuit or overload of the sensor supply.
        In the case of the "Leave power switched off" setting,
        the CPX-E automation system must be switched off and on to restore the power.
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_debounce_time(self, value: int) -> None:
        """
        The "Input debounce time" parameter defines when
        an edge change of the sensor signal shall be assumed as a logical input signal.
        In this way, unwanted signal edge changes can be suppressed during switching operations
        (bouncing of the input signal).
        Accepted values are 0: 0.1 ms; 1: 3 ms (default); 2: 10 ms; 3: 20 ms;
        """
        if value < 0 or value > 3:
            raise ValueError(f"Value {value} must be between 0 and 3")

        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register, delete bit 4+5 from it
        # and refill it with value
        value_to_write = (reg & 0xCF) | (value << 4)

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_signal_extension_time(self, value: int) -> None:
        """
        The "Signal extension time" parameter defines
        the minimum valid duration of the assumed signal status of the input signal.
        Edge changes within the signal extension time are ignored.
        Short input signals can also be recorded by defining a signal extension time.
        Accepted values are 0: 0.5 ms; 1: 15 ms (default); 2: 50 ms; 3: 100 ms;
        """
        if value < 0 or value > 3:
            raise ValueError(f"Value {value} must be between 0 and 3")

        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register, delete bit 6+7 from it
        # and refill it with value
        value_to_write = (reg & 0x3F) | (value << 6)

        self.base.write_function_number(function_number, value_to_write)
