"""CPX-AP-*-4IOL-* module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.cpx_base import CpxRequestError
from cpx_io.utils.helpers import div_ceil


class CpxAp4Iol(CpxApModule):
    """Class for CPX-AP-*-4IOL-* module"""

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

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters"""
        params = super().read_ap_parameter()

        io_link_variant = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20090, 0)[:-1], data_type="uint16"
        )

        activation_operating_voltage = CpxBase.decode_bool(
            self.base.read_parameter(self.position, 20097, 0)
        )

        params.io_link_variant = self.__class__.module_codes[io_link_variant]
        params.operating_supply = activation_operating_voltage
        return params

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all IO-Link input data
        register order is [msb, ... , ... , lsb]
        """
        module_input_size = div_ceil(self.information.input_size, 2) - 2

        data = self.base.read_reg_data(self.input_register, length=module_input_size)
        data = [
            CpxBase.decode_int([d], data_type="uint16", byteorder="little")
            for d in data
        ]

        channel_size = (module_input_size) // 4

        channels = [
            data[: channel_size * 1],
            data[channel_size * 1 : channel_size * 2],
            data[channel_size * 2 : channel_size * 3],
            data[channel_size * 3 :],
        ]
        return channels

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the register values of one channel
        register order is [msb, ... , ... , lsb]
        channel order is [0, 1, 2, 3]
        """
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channel(self, channel: int, data: list[int]) -> None:
        """set one channel to list of uint16 values
        channel order is [0, 1, 2, 3]
        """
        module_output_size = div_ceil(self.information.output_size, 2)
        channel_size = (module_output_size) // 4

        register_data = [
            CpxBase.encode_int(d, data_type="uint16", byteorder="little")[0]
            for d in data
        ]
        self.base.write_reg_data(
            register_data, self.output_register + channel_size * channel
        )

    @CpxBase.require_base
    def read_pqi(self, channel: int | None = None) -> dict | list[dict]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels"""
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

        return channels_pqi[channel]

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Accepted values are
        0: Load supply monitoring inactive
        1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
        2: Load supply monitoring active
        """
        uid = 20022

        if not 0 <= value <= 2:
            raise ValueError("Value {value} must be between 0 and 2")

        self.base.write_parameter(self.position, uid, 0, value)

    @CpxBase.require_base
    def configure_target_cycle_time(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Target cycle time in ms for the given channels. If no channel is specified,
        target cycle time is applied to all channels. Possible cycle time values:
        -  0: as fast as possible (default)
        - 16: 1.6 ms
        - 32: 3.2 ms
        - 48: 4.8 ms
        - 68: 8.0 ms
        - 73: 10.0 ms
        - 78: 12.0 ms
        - 88: 16.0 ms
        - 98: 20.0 ms
        - 133: 40.0 ms
        - 158: 80.0 ms
        - 183: 120.0 ms
        """
        uid = 20049

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = [0, 16, 32, 48, 68, 73, 78, 88, 98, 133, 158, 183]

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, value)

    @CpxBase.require_base
    def configure_device_lost_diagnostics(
        self, value: bool, channel: int | list | None = None
    ) -> None:
        """Activation of diagnostics for IO-Link device lost (default: True) for
        given channel. If no channel is provided, value will be written to all channels.
        """

        uid = 20050

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, int(value))

    @CpxBase.require_base
    def configure_port_mode(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Port mode. Available values:
        - 0: DEACTIVATED (factory setting)
        - 1: IOL_MANUAL
        - 2: IOL_AUTOSTART
        - 3: DI_CQ
        - 97: PREOPERATE (Only supported in combination with IO-Link V1.1 devices)
        """

        uid = 20071

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = [0, 1, 2, 3, 97]

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, value)

    @CpxBase.require_base
    def configure_review_and_backup(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Review and backup. Available values:
        - 0: no test (factory setting)
        - 1: device compatible V1.0
        - 2: device compatible V1.1
        - 3: device compatible V1.1 Data storage Backup+ Restore
        - 4: device compatible V1.1 Data storage Restore
        Changes only become effective when the port mode is changed (ID 20071).
        """

        uid = 20072

        if channel is None:
            channel = [0, 1, 2, 3]

        if not 0 <= value <= 4:
            raise ValueError("Value {value} must be between 0 and 4")

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, value)

    @CpxBase.require_base
    def configure_target_vendor_id(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Target Vendor ID
        Changes only become effective when the port mode is changed (ID 20071)."""

        uid = 20073

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, value)

    @CpxBase.require_base
    def configure_setpoint_device_id(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Setpoint device ID
        Changes only become effective when the port mode is changed (ID 20071)."""

        uid = 20080

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, uid, channel_item, value)

    @CpxBase.require_base
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels
        Returns a dict of parameters for every channel.
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

        for i in range(4):
            port_status_information = port_status_dict.get(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 20074, i),
                    data_type="uint8",
                )
            )

            revision_id = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20075, i),
                data_type="uint8",
            )

            transmission_rate = transmission_rate_dict.get(
                CpxBase.decode_int(
                    self.base.read_parameter(self.position, 20076, i),
                    data_type="uint8",
                )
            )

            actual_cycle_time = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20077, i),
                data_type="uint16",
            )

            actual_vendor_id = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20078, i),
                data_type="uint16",
            )

            actual_device_id = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20079, i),
                data_type="uint32",
            )

            input_data_length = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20108, i),
                data_type="uint8",
            )

            output_data_length = CpxBase.decode_int(
                self.base.read_parameter(self.position, 20109, i),
                data_type="uint8",
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

        return channel_params

    @CpxBase.require_base
    def read_isdu(self, channel: int, index: int, subindex: int) -> list[int]:
        """Read isdu (device parameter) from defined channel
        Raises CpxRequestError when read failed"""

        # select module, starts with 1
        self.base.write_reg_data(self.position + 1, *cpx_ap_registers.ISDU_MODULE_NO)
        # select channel, starts with 1
        self.base.write_reg_data(channel + 1, *cpx_ap_registers.ISDU_CHANNEL)
        # select index
        self.base.write_reg_data(index, *cpx_ap_registers.ISDU_INDEX)
        # select subindex
        self.base.write_reg_data(subindex, *cpx_ap_registers.ISDU_SUBINDEX)
        # select length of data in bytes, always zero when reading
        self.base.write_reg_data(0, *cpx_ap_registers.ISDU_LENGTH)
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        self.base.write_reg_data(100, *cpx_ap_registers.ISDU_COMMAND)

        stat = 1
        cnt = 0
        while stat > 0 or cnt > 1000:
            stat = self.base.read_reg_data(*cpx_ap_registers.ISDU_STATUS)[0]
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data read failed")

        return self.base.read_reg_data(*cpx_ap_registers.ISDU_DATA)

    @CpxBase.require_base
    def write_isdu(
        self, data: list[int], channel: int, index: int, subindex: int
    ) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed"""

        # select module, starts with 1
        self.base.write_reg_data(self.position + 1, *cpx_ap_registers.ISDU_MODULE_NO)
        # select channel, starts with 1
        self.base.write_reg_data(channel + 1, *cpx_ap_registers.ISDU_CHANNEL)
        # select index
        self.base.write_reg_data(index, *cpx_ap_registers.ISDU_INDEX)
        # select subindex
        self.base.write_reg_data(subindex, *cpx_ap_registers.ISDU_SUBINDEX)
        # select length of data in bytes, always zero when reading
        self.base.write_reg_data(len(data) * 2, *cpx_ap_registers.ISDU_LENGTH)
        # write data to data register
        self.base.write_reg_data(data, *cpx_ap_registers.ISDU_DATA)
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        self.base.write_reg_data(101, *cpx_ap_registers.ISDU_COMMAND)

        stat = 1
        cnt = 0
        while stat > 0 or cnt > 1000:
            stat = self.base.read_reg_data(*cpx_ap_registers.ISDU_STATUS)[0]
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data write failed")
