"""CPX-E-4IOL module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

import struct
from typing import Union
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.cpx_system.cpx_e import cpx_e_modbus_registers
from cpx_io.cpx_system.cpx_e.cpx_e_supported_datatypes import SUPPORTED_ISDU_DATATYPES
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_enums import OperatingMode, AddressSpace


class CpxE4Iol(CpxModule):
    """Class for CPX-E-4IOL io-link master module"""

    def __init__(self, address_space: Union[int, AddressSpace] = 2, **kwargs):
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

    def _configure(self, *args):
        super()._configure(*args)

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
    def read_channels(self, bytelength: int = None) -> list[bytes]:
        """read all channels as a list of bytes values

        :parameter bytelength: Length of the expected data in bytes. (optional)
        :type bytelength: int
        :return: All registers from all channels
        :rtype: list[bytes (byteorder big endian)]
        """

        reg = self.base.read_reg_data(
            self.system_entry_registers.inputs, length=self.module_input_size * 4
        )
        # module_input_size is in 16bit registers per channel
        # channel_size should be in bytes
        channel_size = self.module_input_size * 2
        if bytelength is None:
            bytelength = channel_size

        channels = [
            reg[: channel_size * 1][:bytelength],
            reg[channel_size * 1 : channel_size * 2][:bytelength],
            reg[channel_size * 2 : channel_size * 3][:bytelength],
            reg[channel_size * 3 :][:bytelength],
        ]
        Logging.logger.info(f"{self.name}: Reading channels: {channels}")
        return channels

    @CpxBase.require_base
    def read_channel(self, channel: int, bytelength: int = None) -> bytes:
        """read back the value of one channel

        :parameter channel: Channel number, starting with 0
        :type channel: int
        :parameter bytelength: Length of the expected data in bytes. (optional)
        :type bytelength: int
        :return: Channel value
        :rtype: bytes (byteorder big endian)
        """
        channel_size = self.module_input_size * 2
        if bytelength is None:
            bytelength = channel_size
        register_index = (
            self.system_entry_registers.inputs + channel_size * channel // 2
        )
        return self.base.read_reg_data(register_index, length=channel_size // 2)[
            :bytelength
        ]

    @CpxBase.require_base
    def write_channel(self, channel: int, data: bytes) -> None:
        """set one channel to a value

        :param channel: Channel number, starting with 0
        :type channel: int
        :param data: Value to write
        :type data: bytes (byteorder big endian)
        """
        byte_channel_size = self.module_output_size * 2

        if len(data) > byte_channel_size:
            raise ValueError(
                f"Your current IO-Link datalength only allows {byte_channel_size} bytes. "
                f"The provided data length is {len(data)} bytes"
            )

        # add missing bytes for full modbus register
        if len(data) % 2:
            data += b"\x00"
        # add missing bytes for full master length
        if len(data) != byte_channel_size:
            data += b"\x00" * (byte_channel_size - len(data))

        self.base.write_reg_data(
            data, self.system_entry_registers.outputs + byte_channel_size // 2 * channel
        )
        Logging.logger.info(f"{self.name}: Setting channel {channel} to {data}")

    @CpxBase.require_base
    def write_channels(self, data: list[bytes]) -> None:
        """set all channels to values from a list of 4 elements

        :param data: Values to write
        :type data: list[bytes (byteorder big endian)]
        """
        byte_channel_size = self.module_output_size * 2

        if any(len(d) > byte_channel_size for d in data):
            raise ValueError(
                f"Your current IO-Link datalength only allows {byte_channel_size} bytes. "
                f"The provided data length is {len(data)} bytes"
            )
        if len(data) != 4:
            raise ValueError(f"Data len error: expected: 4, got: {len(data)}")

        for d in data:
            # if data has an uneven bytesize, fill on the left
            if len(d) % 2 != 0:
                d = b"\x00" + d
            # if data is smaller than the master size, fill on right side
            if len(d) != byte_channel_size:
                d += b"\x00" * (byte_channel_size - len(d))

        # Join all channel values to one bytes object so it can be written in one modbus command
        all_register_data = b"".join(data)

        self.base.write_reg_data(all_register_data, self.system_entry_registers.outputs)
        Logging.logger.info(f"{self.name}: Setting all channels to {data}")

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
        self, value: tuple[int], channel: Union[int, list] = None
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
    def configure_pl_supply(
        self, value: bool, channel: Union[int, list] = None
    ) -> None:
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
        self, value: Union[OperatingMode, int], channel: Union[int, list] = None
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
    def read_line_state(
        self, channel: Union[int, list] = None
    ) -> Union[list[str], str]:
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
    def read_device_error(
        self, channel: Union[int, list] = None
    ) -> Union[tuple[int], int]:
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

    @CpxBase.require_base
    def read_isdu(
        self, channel: int, index: int, subindex: int = 0, *, data_type: str = "raw"
    ) -> any:
        """Read isdu (device parameter) from defined channel.
        Raises CpxRequestError when read failed.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: (optional) io-link parameter subindex
        :type subindex: int
        :param data_type: (optional) datatype for correct interptetation.
            Check `cpx_e_supported_datatypes.SUPPORTED_ISDU_DATATYPES` for a list of
            supported datatypes
        :type data_type: str
        :return : Value depending on the datatype
        :rtype : any
        """

        module_index = (self.position).to_bytes(2, "little")  # starts with 0 on CPX-E
        channel = (channel).to_bytes(2, "little")
        index = index.to_bytes(2, "little")
        subindex = subindex.to_bytes(2, "little")
        length = (0).to_bytes(2, "little")  # always zero when reading
        # command: 50 Read(with byte swap), 51 write(with byte swap)
        command = (50).to_bytes(2, "little")

        if data_type not in SUPPORTED_ISDU_DATATYPES:
            raise TypeError(f"Datatype '{data_type}' is not supported by read_isdu()")

        # select module, starts with 0
        self.base.write_reg_data_with_single_cmds(
            module_index, cpx_e_modbus_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 0
        self.base.write_reg_data_with_single_cmds(
            channel, cpx_e_modbus_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data_with_single_cmds(
            index, cpx_e_modbus_registers.ISDU_INDEX.register_address
        )
        # select subindex
        self.base.write_reg_data_with_single_cmds(
            subindex, cpx_e_modbus_registers.ISDU_SUBINDEX.register_address
        )
        # select length of data in bytes
        self.base.write_reg_data_with_single_cmds(
            length, cpx_e_modbus_registers.ISDU_LENGTH.register_address
        )
        # command
        self.base.write_reg_data_with_single_cmds(
            command, cpx_e_modbus_registers.ISDU_COMMAND.register_address
        )

        stat, cnt = 1, 0
        while stat > 0 and cnt < 1000:
            try:
                stat = int.from_bytes(
                    self.base.read_reg_data(*cpx_e_modbus_registers.ISDU_STATUS),
                    byteorder="little",
                )
            # CPX-E responds with an error that needs to be caught
            except ConnectionAbortedError:
                continue
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data read failed")

        # read back the actual length from the length register (this is in bytes)
        actual_length = int.from_bytes(
            self.base.read_reg_data(
                cpx_e_modbus_registers.ISDU_LENGTH.register_address
            ),
            byteorder="little",
        )

        ret = self.base.read_reg_data(
            cpx_e_modbus_registers.ISDU_DATA.register_address, actual_length
        )
        Logging.logger.info(f"{self.name}: Reading ISDU for channel {channel}: {ret}")

        if data_type == "raw":
            return ret[:actual_length]
        if data_type == "str":
            return ret.decode("ascii").split("\x00", 1)[0]
        if data_type.startswith("uint"):
            chunks = [ret[i : i + 2] for i in range(0, actual_length, 2)]
            inverted_chunks = reversed(chunks)
            ret_inverted_registers = b"".join(inverted_chunks)
            return int.from_bytes(
                ret_inverted_registers[:actual_length], byteorder="big"
            )
        if data_type.startswith("int"):
            chunks = [ret[i : i + 2] for i in range(0, actual_length, 2)]
            inverted_chunks = reversed(chunks)
            ret_inverted_registers = b"".join(inverted_chunks)
            return int.from_bytes(
                ret_inverted_registers[:actual_length], byteorder="big", signed=True
            )
        if data_type == "bool":
            chunks = [ret[i : i + 2] for i in range(0, actual_length, 2)]
            inverted_chunks = reversed(chunks)
            ret_inverted_registers = b"".join(inverted_chunks)
            return bool.from_bytes(
                ret_inverted_registers[:actual_length], byteorder="big"
            )
        if data_type == "float32":
            return struct.unpack("!f", ret[:actual_length])[0]

        # this is unnecessary but required for consistent return statements
        raise TypeError(f"Datatype '{data_type}' is not supported by read_isdu()")

    @CpxBase.require_base
    def write_isdu(
        self,
        data: Union[bytes, str, int, bool, float],
        channel: int,
        index: int,
        subindex: int = 0,
        *,
        data_type: str = "raw",
    ) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed.

        :param data: Data to write.
        :type data: bytes|str|int|bool
        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: (optional) io-link parameter subindex
        :type subindex: int
        :param data_type: (optional) datatype for correct interptetation.
            Check `cpx_e_supported_datatypes.SUPPORTED_ISDU_DATATYPES` for a list of
            supported datatypes.
        :type data_type: str
        """

        # pylint: disable=too-many-arguments
        # Keep structure of CPX-AP but with additional requirements for CPX-E

        module_index = (self.position).to_bytes(2, "little")  # starts with 0 on CPX-E
        channel = (channel).to_bytes(2, "little")
        index = (index).to_bytes(2, "little")
        subindex = (subindex).to_bytes(2, "little")
        command = (51).to_bytes(2, "little")  # 51: write

        # unfortunately cpx-e is picky about the length of the data and we cannot
        # detect it automatically for all of the datatypes. This is why the user
        # needs to provide the data_type to specify the length correctly.

        if data_type == "raw" and isinstance(data, bytes):
            length = (len(data)).to_bytes(2, "little")

        elif data_type == "str" and isinstance(data, str):
            length = (len(data)).to_bytes(2, "little")
            data = data.encode(encoding="ascii")

        elif data_type == "bool" and isinstance(data, bool):
            length = (1).to_bytes(2, "little")
            data = data.to_bytes(1, byteorder="big")

        elif data_type == "uint8" and isinstance(data, int):
            length = (1).to_bytes(2, "little")
            data = data.to_bytes(1, byteorder="big")

        elif data_type == "uint16" and isinstance(data, int):
            length = (2).to_bytes(2, "little")
            data = data.to_bytes(2, byteorder="big")

        elif data_type == "uint32" and isinstance(data, int):
            length = (4).to_bytes(2, "little")
            data = data.to_bytes(4, byteorder="big")

        elif data_type == "int8" and isinstance(data, int):
            length = (1).to_bytes(2, "little")
            data = data.to_bytes(1, byteorder="big", signed=True)

        elif data_type == "int16" and isinstance(data, int):
            length = (2).to_bytes(2, "little")
            data = data.to_bytes(2, byteorder="big", signed=True)

        elif data_type == "int32" and isinstance(data, int):
            length = (4).to_bytes(2, "little")
            data = data.to_bytes(4, byteorder="big", signed=True)

        elif data_type == "float32" and isinstance(data, float):
            data = struct.pack("!f", data)
            length = len(data).to_bytes(2, "little")

        else:
            raise TypeError(
                f"{type(data)} is not supported by write_isdu() "
                f"with data_type set to '{data_type}'"
            )

        # select module, starts with 0
        self.base.write_reg_data_with_single_cmds(
            module_index, cpx_e_modbus_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 0
        self.base.write_reg_data_with_single_cmds(
            channel, cpx_e_modbus_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data_with_single_cmds(
            index, cpx_e_modbus_registers.ISDU_INDEX.register_address
        )
        # select subindex
        self.base.write_reg_data_with_single_cmds(
            subindex, cpx_e_modbus_registers.ISDU_SUBINDEX.register_address
        )
        # select length of data in bytes
        self.base.write_reg_data_with_single_cmds(
            length, cpx_e_modbus_registers.ISDU_LENGTH.register_address
        )
        # write data to data register
        self.base.write_reg_data_with_single_cmds(
            data, cpx_e_modbus_registers.ISDU_DATA.register_address
        )
        # command
        self.base.write_reg_data_with_single_cmds(
            command, cpx_e_modbus_registers.ISDU_COMMAND.register_address
        )

        Logging.logger.info(
            f"{self.name}: Write ISDU {data} to channel {channel} ({index},{subindex})"
        )
