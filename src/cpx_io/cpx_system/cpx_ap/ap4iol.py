"""CPX-AP-`*`-4IOL-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

import struct
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.cpx_system.cpx_base import CpxRequestError
from cpx_io.utils.helpers import div_ceil
from cpx_io.utils.logging import Logging


class CpxAp4Iol(CpxApModule):
    """Class for CPX-AP-`*`-4IOL-`*` module"""

    module_codes = {
        8201: "CPX-AP-I-4IOL-M12 variant 8",
        8205: "CPX-AP-I-4IOL-M12 variant 8 OE",
        8206: "CPX-AP-I-4IOL-M12 variant 2",
        8207: "CPX-AP-I-4IOL-M12 variant 2 OE",
        8208: "CPX-AP-I-4IOL-M12 variant 4",
        8209: "CPX-AP-I-4IOL-M12 variant 4 OE",
        8210: "CPX-AP-I-4IOL-M12 variant 16",
        8211: "CPX-AP-I-4IOL-M12 variant 16 OE",
        8212: "CPX-AP-I-4IOL-M12 variant 23",
        8213: "CPX-AP-I-4IOL-M12 variant 32 OE",
        12302: "CPX-AP-A-4IOL-M12 variant 2",
        12303: "CPX-AP-A-4IOL-M12 variant 2 OE",
        12304: "CPX-AP-A-4IOL-M12 variant 4",
        12305: "CPX-AP-A-4IOL-M12 variant 4 OE",
        12300: "CPX-AP-A-4IOL-M12 variant 8",
        12301: "CPX-AP-A-4IOL-M12 variant 8 OE",
        12306: "CPX-AP-A-4IOL-M12 variant 16",
        12307: "CPX-AP-A-4IOL-M12 variant 16 OE",
        12308: "CPX-AP-A-4IOL-M12 variant 32",
        12309: "CPX-AP-A-4IOL-M12 variant 32 OE",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldbus_parameters = None

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        self.fieldbus_parameters = self.read_fieldbus_parameters()

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters

        :return: All AP parameters
        :rtype: dict
        """
        params = super().read_ap_parameter()

        io_link_variant = self.base.read_parameter(
            self.position, cpx_ap_parameters.VARIANT_SWITCH
        )

        activation_operating_voltage = self.base.read_parameter(
            self.position, cpx_ap_parameters.SENSOR_SUPPLY_ENABLE
        )

        params.io_link_variant = self.__class__.module_codes[io_link_variant]
        params.operating_supply = activation_operating_voltage
        Logging.logger.info(f"{self.name}: Reading AP parameters")
        return params

    @CpxBase.require_base
    def read_channels(self) -> list[bytes]:
        """read all IO-Link input data register order is [msb, ... , lsb]

        :return: All registers from all channels
        :rtype: list[bytes]
        """
        module_input_size = div_ceil(self.information.input_size, 2) - 2

        reg = self.base.read_reg_data(self.input_register, length=module_input_size)

        # 4 channels per module but channel_size should be in bytes while module_input_size
        # is in 16bit registers
        channel_size = (module_input_size) // 4 * 2

        channels = [
            reg[: channel_size * 1],
            reg[channel_size * 1 : channel_size * 2],
            reg[channel_size * 2 : channel_size * 3],
            reg[channel_size * 3 :],
        ]
        Logging.logger.info(f"{self.name}: Reading channels: {channels}")
        return channels

    @CpxBase.require_base
    def read_channel(self, channel: int, full_size: bool = False) -> bytes:
        """read back the register values of one channel
        register order is [msb, ... , ... , lsb]

        :parameter channel: Channel number, starting with 0
        :type channel: int
        :parameter full: Return all bytes for the channel ignoring device information
        :type full: bool
        :return: Value of the channel
        :rtype: bytes
        """

        if full_size:
            return self.read_channels()[channel]

        return self.read_channels()[channel][
            : self.fieldbus_parameters[channel]["Input data length"]
        ]

    @CpxBase.require_base
    def write_channel(self, channel: int, data: bytes) -> None:
        """set one channel to list of uint16 values

        :param channel: Channel number, starting with 0
        :type channel: int
        :param data: Value to write
        :type data: bytes
        """
        module_output_size = div_ceil(self.information.output_size, 2)
        channel_size = (module_output_size) // 4

        self.base.write_reg_data(data, self.output_register + channel_size * channel)
        Logging.logger.info(f"{self.name}: Setting channel {channel} to {data}")

    @CpxBase.require_base
    def read_pqi(self, channel: int = None) -> dict | list[dict]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels

        :param channel: Channel number, starting with 0, optional
        :type channel: int
        :return: PQI information as dict for one channel or as list of dicts for more channels
        :rtype: dict | list[dict] depending on param channel
        """
        data45 = self.base.read_reg_data(self.input_register + 16)[0]
        data67 = self.base.read_reg_data(self.input_register + 17)[0]
        data = [
            data45 & 0xFF,
            (data45 & 0xFF00) >> 8,
            data67 & 0xFF,
            (data67 & 0xFF00) >> 8,
        ]

        channels_pqi = []

        for data_item in data:
            port_qualifier = (
                "input data is valid"
                if (data_item & 0b10000000) >> 7
                else "input data is invalid"
            )
            device_error = (
                "there is at least one error or warning on the device or port"
                if (data_item & 0b01000000) >> 6
                else "there are no errors or warnings on the device or port"
            )
            dev_com = (
                "device is in status PREOPERATE or OPERATE"
                if (data_item & 0b00100000) >> 5
                else "device is not connected or not yet in operation"
            )

            channels_pqi.append(
                {
                    "Port Qualifier": port_qualifier,
                    "Device Error": device_error,
                    "DevCOM": dev_com,
                }
            )
        if channel is None:
            return channels_pqi

        Logging.logger.info(f"{self.name}: Reading PQI of channel(s) {channel}")
        return channels_pqi[channel]

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Configure the monitoring of the load supply.

        Accepted values are
          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Setting of monitoring of load supply in range 0..3 (see datasheet)
        :type value: int
        """

        if not 0 <= value <= 2:
            raise ValueError(f"Value {value} must be between 0 and 2")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP, value
        )

        value_str = [
            "inactive",
            "active, diagnosis suppressed in case of switch-off",
            "active",
        ]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")

    @CpxBase.require_base
    def configure_target_cycle_time(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Target cycle time in ms for the given channels. If no channel is specified,
        target cycle time is applied to all channels.

        Accepted values are
          *  0: as fast as possible (default)
          * 16: 1.6 ms
          * 32: 3.2 ms
          * 48: 4.8 ms
          * 68: 8.0 ms
          * 73: 10.0 ms
          * 78: 12.0 ms
          * 88: 16.0 ms
          * 98: 20.0 ms
          * 133: 40.0 ms
          * 158: 80.0 ms
          * 183: 120.0 ms

        :param value: target cycle time (see datasheet)
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "0 ms",
            16: "1.6 ms",
            32: "3.2 ms",
            48: "4.8 ms",
            68: "8.0 ms",
            73: "10.0 ms",
            78: "12.0 ms",
            88: "16.0 ms",
            98: "20.0 ms",
            133: "40.0 ms",
            158: "80.0 ms",
            183: "120.0 ms",
        }

        if value not in allowed_values:
            raise ValueError(
                f"Value {value} not valid, must be one of {allowed_values}"
            )

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position, cpx_ap_parameters.NOMINAL_CYCLE_TIME, value, c
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} target "
            f"cycle time to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_device_lost_diagnostics(
        self, value: bool, channel: int | list[int] = None
    ) -> None:
        """Activation of diagnostics for IO-Link device lost (default: True) for
        given channel. If no channel is provided, value will be written to all channels.

        :param value: activate (True) or deactivate (False) diagnostics for given channel(s)
        :type value: bool
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position, cpx_ap_parameters.DEVICE_LOST_DIAGNOSIS_ENABLE, value, c
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} device lost diagnostics to {value}"
        )

    @CpxBase.require_base
    def configure_port_mode(self, value: int, channel: int | list[int] = None) -> None:
        """configure the port mode

        Accepted values are
          * 0: DEACTIVATED (factory setting)
          * 1: IOL_MANUAL
          * 2: IOL_AUTOSTART
          * 3: DI_CQ
          * 97: PREOPERATE (Only supported in combination with IO-Link V1.1 devices)

        :param value: port mode (see datasheet)
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "DEACTIVATED",
            1: "IOL_MANUAL",
            2: "IOL_AUTOSTART",
            3: "DI_CQ",
            97: "PREOPERATE",
        }

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position, cpx_ap_parameters.PORT_MODE, value, c
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} port mode to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_review_and_backup(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Review and backup.

        Accepted values are
          * 0: no test (factory setting)
          * 1: device compatible V1.0
          * 2: device compatible V1.1
          * 3: device compatible V1.1 Data storage Backup+ Restore
          * 4: device compatible V1.1 Data storage Restore
        Changes only become effective when the port mode is changed (ID 20071).

        :param value: review and backup option (see datasheet)
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "no test",
            1: "device compatible V1.0",
            2: "device compatible V1.1",
            3: "device compatible V1.1 Data storage Backup+ Restore",
            4: "device compatible V1.1 Data storage Restore",
        }

        if value not in allowed_values:
            raise ValueError("Value {value} must be between 0 and 4")

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position,
                cpx_ap_parameters.VALIDATION_AND_BACKUP,
                value,
                c,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} port mode to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_target_vendor_id(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Target Vendor ID
        Changes only become effective when the port mode is changed (ID 20071).

        :param value: target vendor id
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position, cpx_ap_parameters.NOMINAL_VENDOR_ID, value, c
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} port mode to {value}"
        )

    @CpxBase.require_base
    def configure_setpoint_device_id(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Setpoint device ID
        Changes only become effective when the port mode is changed (ID 20071).

        :param value: setpoint device id
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for c in channel:
            self.base.write_parameter(
                self.position, cpx_ap_parameters.NOMINAL_DEVICE_ID, value, c
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} device id to {value}"
        )

    @CpxBase.require_base
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels.

        :return: a dict of parameters for every channel.
        :rtype: list[dict]
        """

        channel_params = []

        port_status_dict = {
            0: "NO_DEVICE",
            1: "DEACTIVATED",
            2: "PORT_DIAG",
            3: "PREOPERATE",
            4: "OPERATE",
            5: "DI_CQ",
            6: "DO_CQ",
            254: "PORT_POWER_OFF",
            255: "NOT_AVAILABLE",
        }
        transmission_rate_dict = {0: "not detected", 1: "COM1", 2: "COM2", 3: "COM3"}

        for c in range(4):
            port_status_information = port_status_dict.get(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.PORT_STATUS_INFO, c
                ),
            )

            revision_id = self.base.read_parameter(
                self.position, cpx_ap_parameters.REVISION_ID, c
            )

            transmission_rate = transmission_rate_dict.get(
                self.base.read_parameter(
                    self.position, cpx_ap_parameters.TRANSMISSION_RATE, c
                ),
            )

            actual_cycle_time = self.base.read_parameter(
                self.position, cpx_ap_parameters.ACTUAL_CYCLE_TIME, c
            )

            actual_vendor_id = self.base.read_parameter(
                self.position, cpx_ap_parameters.ACTUAL_VENDOR_ID, c
            )

            actual_device_id = self.base.read_parameter(
                self.position, cpx_ap_parameters.ACTUAL_DEVICE_ID, c
            )

            input_data_length = self.base.read_parameter(
                self.position, cpx_ap_parameters.IO_LINK_INPUT_DATA_LENGTH, c
            )

            output_data_length = self.base.read_parameter(
                self.position, cpx_ap_parameters.IO_LINK_OUTPUT_DATA_LENGTH, c
            )

            channel_params.append(
                {
                    "Port status information": port_status_information,
                    "Revision ID": revision_id,
                    "Transmission rate": transmission_rate,
                    "Actual cycle time [in 100 us]": actual_cycle_time,
                    "Actual vendor ID": actual_vendor_id,
                    "Actual device ID": actual_device_id,
                    "Input data length": input_data_length,
                    "Output data length": output_data_length,
                }
            )

        Logging.logger.info(
            f"{self.name}: Reading fieldbus parameters for all channels: {channel_params}"
        )
        # update the instance
        self.fieldbus_parameters = channel_params
        return channel_params

    @CpxBase.require_base
    def read_isdu(self, channel: int, index: int, subindex: int) -> bytes:
        """Read isdu (device parameter) from defined channel
        Raises CpxRequestError when read failed

        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        :return: device parameter (index/subindex) for given channel
        :rtype: bytes
        """
        module_index = struct.pack("<H", self.position + 1)
        channel = struct.pack("<H", channel + 1)
        index = struct.pack("<H", index)
        subindex = struct.pack("<H", subindex)
        length = struct.pack("<H", 0)  # always zero when reading
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = struct.pack("<H", 100)

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, cpx_ap_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(
            channel, cpx_ap_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data(index, cpx_ap_registers.ISDU_INDEX.register_address)
        # select subindex
        self.base.write_reg_data(
            subindex, cpx_ap_registers.ISDU_SUBINDEX.register_address
        )
        # select length of data in bytes
        length = struct.pack("<H", 0)
        self.base.write_reg_data(length, cpx_ap_registers.ISDU_LENGTH.register_address)
        # command
        self.base.write_reg_data(
            command, cpx_ap_registers.ISDU_COMMAND.register_address
        )

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 1000:
            stat = int.from_bytes(
                self.base.read_reg_data(*cpx_ap_registers.ISDU_STATUS),
                byteorder="little",
            )

            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data read failed")

        ret = self.base.read_reg_data(*cpx_ap_registers.ISDU_DATA)
        Logging.logger.info(f"{self.name}: Reading ISDU for channel {channel}: {ret}")

        return ret

    @CpxBase.require_base
    def write_isdu(self, data: bytes, channel: int, index: int, subindex: int) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed

        :param data: Data as 16bit register values in list
        :type data: list[int]
        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        """
        module_index = struct.pack("<H", self.position + 1)
        channel = struct.pack("<H", channel + 1)
        index = struct.pack("<H", index)
        subindex = struct.pack("<H", subindex)
        length = struct.pack("<H", len(data) * 2)
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = struct.pack("<H", 101)

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, cpx_ap_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(
            channel, cpx_ap_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data(index, cpx_ap_registers.ISDU_INDEX.register_address)
        # select subindex
        self.base.write_reg_data(
            subindex, cpx_ap_registers.ISDU_SUBINDEX.register_address
        )
        # select length of data in bytes
        self.base.write_reg_data(length, cpx_ap_registers.ISDU_LENGTH.register_address)
        # write data to data register
        self.base.write_reg_data(data, cpx_ap_registers.ISDU_DATA.register_address)
        # command
        self.base.write_reg_data(
            command, cpx_ap_registers.ISDU_COMMAND.register_address
        )

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 1000:
            stat = int.from_bytes(
                self.base.read_reg_data(*cpx_ap_registers.ISDU_STATUS),
                byteorder="little",
            )
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data write failed")

        Logging.logger.info(
            f"{self.name}: Write ISDU {data} to channel {channel} ({index},{subindex})"
        )
