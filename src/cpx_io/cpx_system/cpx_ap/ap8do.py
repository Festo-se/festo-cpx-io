"""CPX-AP-`*`-8DO-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import LoadSupply, FailState


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
    def configure_monitoring_load_supply(self, value: LoadSupply | int) -> None:
        """Configures the monitoring load supply for all channels.

          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Monitoring load supply for all channels. Use LoadSupply from cpx_ap_enums
        or see datasheet.
        :type value: LoadSupply | int
        """

        if isinstance(value, LoadSupply):
            value = value.value

        value_range_check(value, 3)

        self.base.write_parameter(
            self.position, ParameterNameMap()["LoadSupplyDiagSetup"], value
        )

        Logging.logger.info(f"{self.name}: Setting Load supply monitoring to {value}")

    @CpxBase.require_base
    def configure_behaviour_in_fail_state(self, value: FailState | int) -> None:
        """Configures the behaviour in fail state for all channels.

          * 0: Reset Outputs (default)
          * 1: Hold last state

        :param value: Setting for behaviour in fail state for all channels. Use FailState
        from cpx_ap_enums or see datasheet.
        :type value: FailState | int
        """

        if isinstance(value, FailState):
            value = value.value

        value_range_check(value, 2)

        self.base.write_parameter(
            self.position, ParameterNameMap()["FailStateBehaviour"], value
        )

        Logging.logger.info(f"{self.name}: Setting fail state behaviour to {value}")
