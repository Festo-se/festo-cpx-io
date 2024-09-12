"""CPX-E-4IOL module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_enums import OperatingMode, AddressSpace


class CpxE4Iol(CpxModule):
    """Class for CPX-E-4IOL io-link master module"""

    def __init__(self, address_space: int | AddressSpace = 2, **kwargs):
        """The address space (inputs/outputs) provided by the module is set using DIL
        switches (see Datasheet CPX-E-4IOL-...)

          * 2: Per port: 2 E / 2 A  Module: 8 E / 8 A (default)
          * 4: Per port: 4 E / 4 A  Module: 16 E / 16 A
          * 8: Per port: 8 E / 8 A  Module: 32 E / 32 A
          * 16: Per port: 16 E / 16 A  Module: 32 E /32 A
          * 32: Per port: 32 E / 32 A  Module: 32 E / 32 A

        :param address_space: Use AddressSpace from cpx_e_enums or see datasheet
        :type address_space: int | AddressSpace
        """
        super().__init__(**kwargs)
        if isinstance(address_space, AddressSpace):
            address_space = address_space.value

        if address_space not in [2, 4, 8, 16, 32]:
            raise ValueError("address_space must be 2, 4, 8, 16 or 32")

        self.module_input_size = address_space // 2
        self.module_output_size = address_space // 2

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = (
            self.system_entry_registers.outputs + self.module_input_size * 4
        )
        # include echo output registers and one diagnosis register
        self.base.next_input_register = (
            self.system_entry_registers.inputs
            + self.module_input_size * 4
            + self.module_output_size * 4
            + 1
        )

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
    def read_channels(self) -> list[bytes]:
        """read all channels as a list of bytes values

        :return: All registers from all channels
        :rtype: list[bytes]
        """

        reg = self.base.read_reg_data(
            self.system_entry_registers.inputs, length=self.module_input_size * 4
        )
        # module_input_size is in 16bit registers per channel
        # channel_size should be in bytes
        channel_size = self.module_input_size * 2

        channels = [
            reg[: channel_size * 1],
            reg[channel_size * 1 : channel_size * 2],
            reg[channel_size * 2 : channel_size * 3],
            reg[channel_size * 3 :],
        ]
        Logging.logger.info(f"{self.name}: Reading channels: {channels}")
        return channels

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bytes:
        """read back the value of one channel

        :parameter channel: Channel number, starting with 0
        :type channel: int
        :return: Channel value
        :rtype: bytes
        """
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channel(self, channel: int, data: list[int]) -> None:
        """set one channel to list of uint16 values

        :param channel: Channel number, starting with 0
        :type channel: int
        :param data: Value to write
        :type data: bytes
        """
        channel_size = self.module_output_size

        self.base.write_reg_data(
            data, self.system_entry_registers.outputs + channel_size * channel
        )
        Logging.logger.info(f"{self.name}: Setting channel {channel} to {data}")

    @CpxBase.require_base
    def configure_monitoring_uload(self, value: bool) -> None:
        """The "Monitoring Uload" parameter defines whether the monitoring of the load voltage
        supply shall be activated or deactivated in regard to undervoltage. When the monitoring
        is activated, the error is sent to the bus module and indicated by the error LED on the
        module

        :param value: monitoring uload value (see datasheet)
        :type value: int
        """
        function_number = 4828 + 64 * self.position
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x04
        else:
            value_to_write = reg & 0xFB

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Setting monitoring uload to {value}")

    @CpxBase.require_base
    def configure_behaviour_after_scl(self, value: bool) -> None:
        """The "Behaviour after SCS" parameter defines whether the voltage remains deactivated or
        reactivates automatically after a short circuit or overload at the IO-Link® interfaces
        (ports). The voltage can be switched on again with the "leave switched off" setting by
        deactivating and then reactivating the "PS supply" parameter. Otherwise the activation
        and deactivation of the automation system CPX-E is required to restore the voltage.

        :param value: behaviour after scs (see datasheet)
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

        Logging.logger.info(f"{self.name}: Setting behaviour after scs to {value}")

    @CpxBase.require_base
    def configure_behaviour_after_sco(self, value: bool) -> None:
        """The "Behaviour after SCO" parameter defines whether the voltage remains deactivated or
        reactivates automatically after a short circuit or overload at the IO-Link® interfaces
        (ports). The voltage can be switched on again with the "leave switched off" setting by
        deactivating and then reactivating the "PS supply" parameter. Otherwise the
        activation and deactivation of the automation system CPX-E is required to restore the
        voltage.

        :param value: behaviour after sco (see datasheet)
        :type value: int
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x02
        else:
            value_to_write = reg & 0xFD

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Setting behaviour after sco to {value}")

    @CpxBase.require_base
    def configure_ps_supply(self, value: bool) -> None:
        """The "PS supply" parameter defines whether the operating voltage supply shall be
        deactivated or activated. The setting applies for all IO-Link interfaces (ports).

        :param value: ps supply
        :type value: int
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: ps supply to {value}")

    @CpxBase.require_base
    def configure_cycle_time(
        self, value: tuple[int], channel: int | list = None
    ) -> None:
        """The "Cycle time" parameter defines the cycle time (low/high) set by the IO-Link master.
        The setting can be made separately for each IO-Link interface (port).
        The value becomes effective at the start of the IO-Link connection by setting the
        "Operating mode" parameter to "IO-Link". Changes during IO-Link operation are not made
        until the connection has been deactivated and then reactivated again.
        Values are tuple of (low, high) 16 bit in us unit. Default is 0 (minimum supported cycle
        time). If no channels are specified, all channels are set to the given value.

        :param value: cycle time (see datasheet) as tuple (low, high)
        :type value: tuple[int]
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        function_number = [
            4828 + 64 * self.position + 8,
            4828 + 64 * self.position + 12,
            4828 + 64 * self.position + 16,
            4828 + 64 * self.position + 20,
        ]

        if isinstance(channel, int):
            channel = [channel]

        if any(c not in range(4) for c in channel):
            raise ValueError("Channel must be between 0 and 3")

        for item in channel:
            self.base.write_function_number(function_number[item], value[0])
            self.base.write_function_number(function_number[item] + 1, value[1])

        Logging.logger.info(
            f"{self.name}: setting channel(s) {channel} cycle time to {value}"
        )

    @CpxBase.require_base
    def configure_pl_supply(self, value: bool, channel: int | list = None) -> None:
        """The "PL supply" parameter defines whether the load voltage supply shall
        be deactivated or activated. The setting can be made separately for each
        IO-Link interface (port). If no channel is specified, the value will be
        applied to all channels.

        :param value: pl supply
        :type value: bool
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        if channel is None:
            channel = [0, 1, 2, 3]

        function_number = [
            4828 + 64 * self.position + 10,
            4828 + 64 * self.position + 14,
            4828 + 64 * self.position + 18,
            4828 + 64 * self.position + 22,
        ]

        if isinstance(channel, int):
            channel = [channel]

        if any(c not in range(4) for c in channel):
            raise ValueError("Channel must be between 0 and 3")

        for item in channel:
            reg = self.base.read_function_number(function_number[item])

            # Fill in the unchanged values from the register
            if value:
                value_to_write = reg | 0x01
            else:
                value_to_write = reg & 0xFE

            self.base.write_function_number(function_number[item], value_to_write)

        Logging.logger.info(
            f"{self.name}: setting channel(s) {channel} pl supply to {value}"
        )

    @CpxBase.require_base
    def configure_operating_mode(
        self, value: OperatingMode | int, channel: int | list = None
    ) -> None:
        """The "Operating mode" parameter defines the operating mode of the
        IO-Link® interface (port). The setting can be made separately for
        each IO-Link interface (port).

          * 0: Inactive: Port is not in use (default)
          * 1: DI: Port acts like a digital input
          * 2: [DO]: reserved
          * 3: IO-Link: IO-Link communication

        :param value: operating mode. Use OperatingMode from cpx_e_enums or see datasheet.
        :type value: OperatingMode | int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        if isinstance(value, OperatingMode):
            value = value.value

        if channel is None:
            channel = [0, 1, 2, 3]

        function_number = [
            4828 + 64 * self.position + 11,
            4828 + 64 * self.position + 15,
            4828 + 64 * self.position + 19,
            4828 + 64 * self.position + 23,
        ]

        value_range_check(value, 4)

        if isinstance(channel, int):
            channel = [channel]

        if any(c not in range(4) for c in channel):
            raise ValueError("Channel must be between 0 and 3")

        for item in channel:
            # delete two lsb from register to write the new value there
            reg = self.base.read_function_number(function_number[item]) & 0xFC

            value_to_write = reg | value

            self.base.write_function_number(function_number[item], value_to_write)

        Logging.logger.info(
            f"{self.name}: setting channel(s) {channel} operating mode to {value}"
        )

    @CpxBase.require_base
    def read_line_state(self, channel: int | list = None) -> list[str] | str:
        """Line state for all channels. If no channel is provided, list of all channels
        is returned.

        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        :return: Line state for all or all requested channels
        :rtype: list[str] | str
        """
        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int) and channel not in range(4):
            raise ValueError("Channel must be between 0 and 3")
        if isinstance(channel, list) and any(c not in range(4) for c in channel):
            raise ValueError("All channel numbers must be between 0 and 3")

        function_number = [
            4828 + 64 * self.position + 24,
            4828 + 64 * self.position + 27,
            4828 + 64 * self.position + 30,
            4828 + 64 * self.position + 33,
        ]
        states = [
            "INACTIVE",
            "DI",
            "_",
            "CHECKFAULT",
            "PREOPERATE",
            "OPERATE",
            "SCANNING",
            "DEVICELOST",
        ]

        line_state = []
        for item in range(4):
            reg = self.base.read_function_number(function_number[item]) & 0x07
            try:
                line_state.append(states[reg])
            except IndexError as exc:
                raise ValueError(
                    f"Read unknown linestate {reg} for channel {item}"
                ) from exc

        if isinstance(channel, int) and channel in range(4):
            return line_state[channel]

        ret = [line_state[c] for c in channel]
        Logging.logger.info(
            f"{self.name}: Reading channel(s) {channel} line state: {ret}"
        )
        return ret

    @CpxBase.require_base
    def read_device_error(self, channel: int | list = None) -> tuple[int] | int:
        """the "Device error code" parameter displays the current lowest-value error code
        (event code) of the connected IO-Link device. If no event is reported, the parameter
        has a value of 0.
        Returns list of tuples of (Low, High) values in hexadecimal strings for each requested
        channel. If only one channel is requested, only one tuple is returned.

        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        :return: device error for all or all requested channels
        :rtype: tuple[int] | int
        """
        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int) and channel not in range(4):
            raise ValueError("Channel must be between 0 and 3")
        if isinstance(channel, list) and any(c not in range(4) for c in channel):
            raise ValueError("All channel numbers must be between 0 and 3")

        function_number = [
            4828 + 64 * self.position + 25,
            4828 + 64 * self.position + 28,
            4828 + 64 * self.position + 31,
            4828 + 64 * self.position + 34,
        ]

        device_error = [0, 0, 0, 0]
        for item in range(4):
            low = self.base.read_function_number(function_number[item]) & 0x0F
            high = self.base.read_function_number(function_number[item] + 1) & 0x0F
            device_error[item] = (hex(low), hex(high))

        if isinstance(channel, int) and channel in range(4):
            return device_error[channel]

        ret = [device_error[c] for c in channel]
        Logging.logger.info(
            f"{self.name}: Reading channel(s) {channel} device error: {ret}"
        )
        return ret
