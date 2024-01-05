"""CPX-E-4AO-UI module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule
from cpx_io.utils.boollist import int_to_boollist


class CpxE4AoUI(CpxEModule):
    """Class for CPX-E-4AO-UI module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = self.base.next_output_register
        self.input_register = self.base.next_input_register

        self.base.next_output_register = self.output_register + 4
        self.base.next_input_register = self.input_register + 5

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register}"
            f"and input register {self.input_register}"
        )

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers"""
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        data = [CpxBase.decode_int([x]) for x in raw_data]
        return data

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet"""
        data = self.base.read_reg_data(self.input_register + 4)[0]
        return int_to_boollist(data, 2)

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[int]) -> None:
        """write data to module channels in ascending order"""
        reg_data = [CpxBase.decode_int([x]) for x in data]
        self.base.write_reg_data(reg_data, self.output_register, length=4)

    @CpxBase.require_base
    def write_channel(self, channel: int, data: int) -> None:
        """write data to module channel number"""
        reg_data = CpxBase.decode_int([data])
        self.base.write_reg_data(reg_data, self.output_register + channel)

    @CpxBase.require_base
    def configure_diagnostics(
        self, short_circuit=None, undervoltage=None, param_error=None
    ):
        """The parameter "Diagnostics of short circuit in actuator supply" defines if
        the diagnostics for the actuator supply with regard to short circuit or
        overload must be activated ("True", default) or deactivated ("False").
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.
        """
        function_number = 4828 + 64 * self.position + 0
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if short_circuit is None:
            short_circuit = bool(reg & 0x02)
        if undervoltage is None:
            undervoltage = bool(reg & 0x04)
        if param_error is None:
            param_error = bool(reg & 0x80)

        value_to_write = (
            (reg & 0x79)
            | (int(short_circuit) << 1)
            | (int(undervoltage) << 2)
            | (int(param_error) << 7)
        )

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_power_reset(self, value: bool) -> None:
        """The parameter “Behaviour after SCS actuator supply” defines if
        the power remains switched off ("False) after a short circuit or
        overload of the actuator supply or
        if it should be switched on again automatically ("True", default).
        In the case of the "Leave power switched off" setting,
        the automation system CPX-E must be switched off and on to restore the power.
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x02
        else:
            value_to_write = reg & 0xFD

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_behaviour_overload(self, value: bool) -> None:
        """The parameter “Behaviour after SCS analogue output” defines if
        the power remains switched off ("False") after a short circuit or
        overload at the outputs or
        if it should be switched on again automatically ("True", default).
        In the case of the "Leave power switched off" setting,
        the automation system CPX-E must be switched off and on to restore the power.
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x08
        else:
            value_to_write = reg & 0xF7

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_data_format(self, value: bool) -> None:
        """The parameter “Data format” defines the data format "Sign + 15 bit” or “linear scaled".
        * False (default): Sign + 15 bit
        * True: Linear scaled
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_actuator_supply(self, value: bool) -> None:
        """The parameter “Actuator supply” defines if the diagnostics for the actuator supply
        must be activated ("True", default) or deactivated ("False").

        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x20
        else:
            value_to_write = reg & 0xDF

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_wire_break(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable wire break / idling diagnostics” defines whether the
        diagnostics of the outputs with regard to wire break/idling should be activated
        or deactivated. When the diagnostics are activated, the error will be sent to
        the bus module and displayed on the module by the error LED
        """

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFB) | (int(value) << 2)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_overload_short_circuit(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable overload/short circuit diagnostics” defines if the
        diagnostics for the outputs with regard to overload/short circuit must be
        activated or deactivated. When the diagnostics are activated, the error
        will be sent to the bus module and displayed on the module by the error LED.
        """

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xEF) | (int(value) << 4)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_parameter_error(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable parameter error diagnostics” defines if the diagnostics
        for the outputs with regard to parameter errors must be activated or deactivated.
        When the diagnostics are activated, the error will be sent to the bus node and
        displayed with the error LED on the module
        """

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0x7F) | (int(value) << 7)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_range(self, channel: int, signalrange: str):
        """Set the signal range and type of one channel"""

        bitmask = {
            "0-10V": 0b0001,
            "-10-+10V": 0b0010,
            "-5-+5V": 0b0011,
            "1-5V": 0b0100,
            "0-20mA": 0b0101,
            "4-20mA": 0b0110,
            "-20-+20mA": 0b0111,
        }
        if signalrange not in bitmask:
            raise ValueError(
                f"'{signalrange}' is not an option. Choose from {bitmask.keys()}"
            )

        function_number = 4828 + 64 * self.position

        reg_01 = self.base.read_function_number(function_number + 11)
        reg_23 = self.base.read_function_number(function_number + 12)

        if channel == 0:
            function_number += 11
            value_to_write = (reg_01 & 0xF0) | bitmask[signalrange]
        elif channel == 1:
            function_number += 11
            value_to_write = (reg_01 & 0x0F) | bitmask[signalrange] << 4
        elif channel == 2:
            function_number += 12
            value_to_write = (reg_23 & 0xF0) | bitmask[signalrange]
        elif channel == 3:
            function_number += 12
            value_to_write = (reg_23 & 0x0F) | bitmask[signalrange] << 4
        else:
            raise ValueError(f"'{channel}' is not in range 0...3")

        self.base.write_function_number(function_number, value_to_write)
