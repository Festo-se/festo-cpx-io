"""CPX-E-4AO-UI module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

import struct
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.helpers import value_range_check, channel_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_enums import ChannelRange


class CpxE4AoUI(CpxModule):
    """Class for CPX-E-4AO-UI module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = self.system_entry_registers.outputs + 4
        self.base.next_input_register = self.system_entry_registers.inputs + 5

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers

        :return: Values of all channels
        :rtype: list[int]
        """
        reg = self.base.read_reg_data(self.system_entry_registers.inputs, length=4)
        values = list(struct.unpack("<" + "h" * (len(reg) // 2), reg))
        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet

        :return: status information (see datasheet)
        :rtype: list[bool]"""
        data = self.base.read_reg_data(self.system_entry_registers.inputs + 4)
        ret = bytes_to_boollist(data)
        Logging.logger.info(f"{self.name}: Reading status: {ret}")
        return ret

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel

        :param channel: Channel number, starting with 0
        :type channel: int"""

        channel_range_check(channel, 4)

        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, values: list[int]) -> None:
        """write (signed 16bit int) data list to module channels in ascending order

        :param values: values to write to the channels
        :type values: list[int]
        """
        if len(values) != 4:
            raise ValueError(f"Data len error: expected: 4, got: {len(values)}")

        reg_data = struct.pack("<hhhh", *values)
        self.base.write_reg_data(reg_data, self.system_entry_registers.outputs)
        Logging.logger.info(f"{self.name}: Writing {values} to channels")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: int) -> None:
        """write (signed 16 bit) value to module channel number

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Value to write to the channel
        :type value: int"""

        channel_range_check(channel, 4)

        reg_data = value.to_bytes(2, byteorder="little", signed=True)
        self.base.write_reg_data(
            reg_data, self.system_entry_registers.outputs + channel
        )
        Logging.logger.info(f"{self.name}: Writing {value} to channel {channel}")

    @CpxBase.require_base
    def configure_diagnostics(
        self,
        short_circuit: bool = None,
        undervoltage: bool = None,
        param_error: bool = None,
    ) -> None:
        """The parameter "Diagnostics of short circuit in actuator supply" defines if
        the diagnostics for the actuator supply with regard to short circuit or
        overload must be activated ("True", default) or deactivated ("False").
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.

        :param short_circuit: diagnostics of short circuit
        :type short_circuit: bool
        :param undervoltage: diagnostics of undervoltage
        :type undervoltage: bool
        :param param_error: diagnostics of parameter error
        :type param_error: bool
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
        Logging.logger.info(
            f"{self.name}: Writing diagnostics parameter short circuit: {short_circuit}, "
            f"undervoltage: {undervoltage}, parmeter error: {param_error}"
        )

    @CpxBase.require_base
    def configure_power_reset(self, value: bool) -> None:
        """The parameter “Behaviour after SCS actuator supply” defines if
        the power remains switched off ("False) after a short circuit or
        overload of the actuator supply or
        if it should be switched on again automatically ("True", default).
        In the case of the "Leave power switched off" setting,
        the automation system CPX-E must be switched off and on to restore the power.

        :param value: behaviour after short circuit or overload at actuator supply
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
            f"{self.name}: Setting behaviour after SCS actuator supply to {value}"
        )

    @CpxBase.require_base
    def configure_behaviour_overload(self, value: bool) -> None:
        """The parameter “Behaviour after SCS analogue output” defines if
        the power remains switched off ("False") after a short circuit or
        overload at the outputs or
        if it should be switched on again automatically ("True", default).
        In the case of the "Leave power switched off" setting,
        the automation system CPX-E must be switched off and on to restore the power.

        :param value: behaviour after short circuit at analogue output
        :type value: bool
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x08
        else:
            value_to_write = reg & 0xF7

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(
            f"{self.name}: Setting behavoiur after SCS analogue output to {value}"
        )

    @CpxBase.require_base
    def configure_data_format(self, value: bool) -> None:
        """The parameter “Data format” defines the data format "Sign + 15 bit” or “linear scaled".
          * False (default): Sign + 15 bit
          * True: Linear scaled
        :param value: data format
        :type value: bool
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: data format to {value}")

    @CpxBase.require_base
    def configure_actuator_supply(self, value: bool) -> None:
        """The parameter “Actuator supply” defines if the diagnostics for the actuator supply
        must be activated ("True", default) or deactivated ("False").

        :param value: actuator supply
        :type value: bool
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x20
        else:
            value_to_write = reg & 0xDF

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: data format to {value}")

    @CpxBase.require_base
    def configure_channel_diagnostics_wire_break(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable wire break / idling diagnostics” defines whether the
        diagnostics of the outputs with regard to wire break/idling should be activated
        or deactivated. When the diagnostics are activated, the error will be sent to
        the bus module and displayed on the module by the error LED

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: wirebrake diagnostics
        :type value: bool
        """

        channel_range_check(channel, 4)

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFB) | (int(value) << 2)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} wirebrake diagnostics to {value}"
        )

    @CpxBase.require_base
    def configure_channel_diagnostics_overload_short_circuit(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable overload/short circuit diagnostics” defines if the
        diagnostics for the outputs with regard to overload/short circuit must be
        activated or deactivated. When the diagnostics are activated, the error
        will be sent to the bus module and displayed on the module by the error LED.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: overload/short circuit diagnostics
        :type value: bool
        """

        channel_range_check(channel, 4)

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xEF) | (int(value) << 4)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} overload/short circuit diagnostics to {value}"
        )

    @CpxBase.require_base
    def configure_channel_diagnostics_parameter_error(
        self, channel: int, value: bool
    ) -> None:
        """The parameter “Enable parameter error diagnostics” defines if the diagnostics
        for the outputs with regard to parameter errors must be activated or deactivated.
        When the diagnostics are activated, the error will be sent to the bus node and
        displayed with the error LED on the module

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: parameter error diagnostics
        :type value: bool
        """

        channel_range_check(channel, 4)

        function_number = 4828 + 64 * self.position + 7 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0x7F) | (int(value) << 7)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} parameter error diagnostics to {value}"
        )

    @CpxBase.require_base
    def configure_channel_range(self, channel: int, value: ChannelRange | int) -> None:
        """Set the signal range and type of one channel

          * 1: 0...10 V
          * 2: -10...+10 V
          * 3: -5...+5 V
          * 4: 1...5 V
          * 5: 0...20 mA
          * 6: 4...20 mA
          * 7: -20...+20 mA

        :param channel: Channel number, starting with 0
        :type channel: int
        :param signalrange: Channel range. Use ChannelRange from cpx_e_enums or see datasheet
        :type signalrange: ChannelRange | int
        """
        if isinstance(value, ChannelRange):
            value = value.value

        channel_range_check(channel, 4)

        value_range_check(value, 1, 8)

        function_number = 4828 + 64 * self.position

        reg_01 = self.base.read_function_number(function_number + 11)
        reg_23 = self.base.read_function_number(function_number + 12)

        value_to_write = None
        if channel == 0:
            function_number += 11
            value_to_write = (reg_01 & 0xF0) | value
        elif channel == 1:
            function_number += 11
            value_to_write = (reg_01 & 0x0F) | (value << 4)
        elif channel == 2:
            function_number += 12
            value_to_write = (reg_23 & 0xF0) | value
        elif channel == 3:
            function_number += 12
            value_to_write = (reg_23 & 0x0F) | (value << 4)

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Setting channel {channel} range to {value}")
