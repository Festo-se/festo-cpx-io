"""CPX-AP-4DI4DO module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.utils.boollist import int_to_boollist, boollist_to_int
from cpx_io.utils.logging import Logging


class CpxAp4Di4Do(CpxApModule):
    """Class for CPX-AP-*-4DI4DO-* module"""

    module_codes = {
        8196: "CPX-AP-I-4DI4DO-M8-3P",
        8197: "CPX-AP-I-4DI4DO-M12-5P",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values.
        Returns a list of 8 elements where the first 4 elements are the input channels 0..3
        and the last 4 elements are the output channels 0..3

        :return: Values of all channels
        :rtype: list[bool]
        """
        data = self.base.read_reg_data(self.input_register)[0] & 0xF
        data |= (self.base.read_reg_data(self.output_register)[0] & 0xF) << 4
        ret = int_to_boollist(data, 1)
        Logging.logger.info(f"{self.name}: Reading channels: {ret}")
        return ret

    @CpxBase.require_base
    def read_channel(self, channel: int, output_numbering=False) -> bool:
        """read back the value of one channel
        Optional parameter 'output_numbering' defines
        if the outputs are numbered with the inputs ("False", default),
        so the range of output channels is 4..7 (as 0..3 are the input channels).
        If "True", the outputs are numbered from 0..3, the inputs cannot be accessed this way.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param output_numbering: Set 'True' if outputs should be numbered from 0 ... 3, optional
        :type output_numbering: bool
        :return: Value of the channel
        :rtype: bool
        """
        if output_numbering:
            channel += 4

        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values

        :param data: list of bool values containing exactly 4 elements for each output channel
        :type data: list[bool]
        """
        if len(data) != 4:
            raise ValueError("Data must be list of four elements")
        integer_data = boollist_to_int(data)
        self.base.write_reg_data(integer_data, self.output_register)

        Logging.logger.info(f"{self.name}: Setting channels to {data}")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: bool
        """
        data = self.base.read_reg_data(self.output_register)[0]  # read current value
        mask = 1 << channel  # Compute mask, an integer with just bit 'channel' set.
        data &= ~mask  # Clear the bit indicated by the mask
        if value:
            data |= mask  # If x was True, set the bit indicated by the mask.

        self.base.write_reg_data(data, self.output_register)

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
    def configure_debounce_time(self, value: int) -> None:
        """The "Input debounce time" parameter defines when an edge change of the sensor signal
        shall be assumed as a logical input signal. In this way, unwanted signal edge changes
        can be suppressed during switching operations (bouncing of the input signal).
        Accepted values are
        * 0: 0.1 ms
        * 1: 3 ms (default)
        * 2: 10 ms
        * 3: 20 ms

        :param value: Debounce time for all channels in range 0..3 (see datasheet)
        :type value: int
        """

        uid = 20014

        if not 0 <= value <= 3:
            raise ValueError(f"Value {value} must be between 0 and 3")

        self.base.write_parameter(self.position, uid, 0, value)

        time_str = ["0.1 ms", "3 ms", "10 ms", "20 ms"]
        Logging.logger.info(f"{self.name}: Setting debounce time to {time_str[value]}")

    @CpxBase.require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Configures the monitoring load supply. Accepted values are
        * 0: Load supply monitoring inactive
        * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
        * 2: Load supply monitoring active

        :param value: Setting of monitoring of load supply in range 0..3 (see datasheet)
        :type value: int
        """
        uid = 20022

        if not 0 <= value <= 2:
            raise ValueError(f"Value {value} must be between 0 and 2")

        self.base.write_parameter(self.position, uid, 0, value)

        value_str = [
            "inactive",
            "active, diagnosis suppressed in case of switch-off",
            "active",
        ]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")

    @CpxBase.require_base
    def configure_behaviour_in_fail_state(self, value: int) -> None:
        """Configures the behaviour in fail state. Accepted values are
        0: Reset Outputs (default)
        1: Hold last state

        :param value: Setting for behaviour in fail state in range 0..3 (see datasheet)
        :type value: int
        """
        uid = 20052

        if not 0 <= value <= 1:
            raise ValueError(f"Value {value} must be between 0 and 2")

        self.base.write_parameter(self.position, uid, 0, value)

        value_str = ["Reset Outputs", "Hold last state"]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")
