"""CPX-AP-`*`-8DO-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.logging import Logging


class CpxAp8Do(CpxApModule):
    """Class for CPX-AP-`*`-8DO-`*` module"""

    module_codes = {
        12293: "CPX-AP-A-8DO-M12-5P",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values.

        :return: Values of all channels
        :rtype: list[bool]
        """
        data = self.base.read_reg_data(self.output_register)
        values = bytes_to_boollist(data)[:8]
        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

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
        if len(data) != 8:
            raise ValueError("Data must be list of eight elements")
        reg = boollist_to_bytes(data)
        self.base.write_reg_data(reg, self.output_register)

        Logging.logger.info(f"{self.name}: Setting channels to {data}")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: bool
        """
        # read current value, invert the channel value
        data = bytes_to_boollist(self.base.read_reg_data(self.output_register))
        data[channel] = value
        reg = boollist_to_bytes(data)
        self.base.write_reg_data(reg, self.output_register)

        Logging.logger.info(f"{self.name}: Setting channel {channel} to {value}")

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level

        :param channel: Channel number, starting with 0
        :type channel: int"""
        # get the relevant value from the register and write the inverse
        value = self.read_channel(channel)
        self.write_channel(channel, not value)

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
            raise ValueError("Value {value} must be between 0 and 2")

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
    def configure_behaviour_in_fail_state(self, value: int) -> None:
        """configure the behaviour in fail state

        Accepted values are
          * 0: Reset Outputs (default)
          * 1: Hold last state

        :param value: Setting for behaviour in fail state in range 0..3 (see datasheet)
        :type value: int
        """

        if not 0 <= value <= 1:
            raise ValueError("Value {value} must be between 0 and 1")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.FAIL_STATE_BEHAVIOUR, value
        )

        value_str = ["Reset Outputs", "Hold last state"]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")
