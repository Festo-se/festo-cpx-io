"""VABX-A-P-EL-E12-AP* module implementation"""

from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.utils.logging import Logging


class VabxAP(CpxApModule):
    """Class for VABX-A-P-EL-E12-AP* module"""

    module_codes = {
        8232: "VABX-A-P-EL-E12-API",
        8233: "VABX-A-P-EL-E12-APA",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values.
        Returns a list of all 32 coils

        :return: Values of all channels
        :rtype: list[bool]
        """

        data0, data1 = self.base.read_reg_data(self.output_register, length=2)
        data = (data1 << 16) + data0

        ret = [d == "1" for d in bin(data)[2:].zfill(32)[::-1]]
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
        if len(data) != 32:
            raise ValueError("Data must be list of 32 elements")
        # Make binary from list of bools
        binary_string = "".join("1" if value else "0" for value in reversed(data))
        # Convert the binary string to an integer
        integer_data = int(binary_string, 2)

        data0 = integer_data & 0xFFFF
        data1 = integer_data >> 16
        self.base.write_reg_data(data0, self.output_register)
        self.base.write_reg_data(data1, self.output_register + 1)

        Logging.logger.info(f"{self.name}: Setting channels to {data}")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: bool
        """
        if channel not in range(33):
            raise ValueError("Channel must be in range 0...32")

        # read current values
        data0, data1 = self.base.read_reg_data(self.output_register, length=2)
        data = (data1 << 16) + data0

        mask = 1 << channel  # Compute mask, an integer with just bit 'channel' set.
        data &= ~mask  # Clear the bit indicated by the mask
        if value:
            data |= mask  # If x was True, set the bit indicated by the mask.

        data0 = data & 0xFFFF
        data1 = data >> 16
        self.base.write_reg_data(data0, self.output_register)
        self.base.write_reg_data(data1, self.output_register + 1)

        Logging.logger.info(f"{self.name}: Setting channel {channel} to {value}")

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        data = (
            self.base.read_reg_data(self.output_register)[0] & 1 << channel
        ) >> channel
        if data == 1:
            self.clear_channel(channel)
        elif data == 0:
            self.set_channel(channel)
        else:
            raise ValueError

    @CpxBase.require_base
    def configure_diagnosis_for_defect_valve(self, value: bool) -> None:
        """Enable (True, default) or disable (False) diagnosis for defect valve.

        :param value: Value to write to the module (True to enable diagnosis)
        :type value: bool
        """
        uid = 20021

        self.base.write_parameter(self.position, uid, 0, int(value))
        Logging.logger.info(
            f"{self.name}: Setting diagnosis for defect valve to {value}"
        )

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Configures the monitoring load supply.

        Accepted values are
          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Setting of monitoring of load supply in range 0..3 (see datasheet)
        :type value: int
        """
        uid = 20022

        if not 0 <= value <= 2:
            raise ValueError("Value {value} must be between 0 and 2")

        self.base.write_parameter(self.position, uid, 0, value)

        value_str = [
            "inactive",
            "active, diagnosis suppressed in case of switch-off",
            "active",
        ]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")

    @CpxBase.require_base
    def configure_behaviour_in_fail_state(self, value: int) -> None:
        """Configures the behaviour in fail state.

        Accepted values are
          * 0: Reset Outputs (default)
          * 1: Hold last state

        :param value: Setting for behaviour in fail state in range 0..3 (see datasheet)
        :type value: int
        """
        uid = 20052

        if not 0 <= value <= 1:
            raise ValueError("Value {value} must be between 0 and 1")

        self.base.write_parameter(self.position, uid, 0, value)

        value_str = ["Reset Outputs", "Hold last state"]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")
