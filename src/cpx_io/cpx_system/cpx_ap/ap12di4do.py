"""CPX-AP-`*`-12DI4DO-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import (
    LoadSupply,
    FailState,
    DebounceTime,
)


class CpxAp12Di4Do(CpxApModule):
    """Class for CPX-AP-`*`-12DI4DO-`*` module"""

    module_codes = {
        12290: "CPX-AP-A-12DI4DO-M12-5P",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values.
        Returns a list of 16 elements where the first 12 elements are the input channels 0..11
        and the last 4 elements are the output channels 0..3

        :return: Values of all channels
        :rtype: list[bool]
        """
        inputs = bytes_to_boollist(self.base.read_reg_data(self.input_register))[:12]
        outputs = bytes_to_boollist(self.base.read_reg_data(self.output_register))[:4]
        values = inputs + outputs
        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

    @CpxBase.require_base
    def read_channel(self, channel: int, output_numbering=False) -> bool:
        """read back the value of one channel
        Optional parameter 'output_numbering' defines
        if the outputs are numbered with the inputs ("False", default),
        so the range of output channels is 12..15 (as 0..11 are the input channels).
        If "True", the outputs are numbered from 0..3, the inputs cannot be accessed this way.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param output_numbering: Set 'True' if outputs should be numbered from 0 ... 3, optional
        :type output_numbering: bool
        :return: Value of the channel
        :rtype: bool
        """
        if output_numbering:
            channel += 12

        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values

        :param data: list of bool values containing exactly 4 elements for each output channel
        :type data: list[bool]
        """
        if len(data) != 4:
            raise ValueError("Data must be list of four elements")
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
        # get the relevant value from the register and write the inverse
        value = self.read_channel(channel, output_numbering=True)
        self.write_channel(channel, not value)

    @CpxBase.require_base
    def configure_debounce_time(self, value: DebounceTime | int) -> None:
        """
        The "Input debounce time" parameter defines when an edge change of the sensor signal
        shall be assumed as a logical input signal. In this way, unwanted signal edge changes
        can be suppressed during switching operations (bouncing of the input signal).

          * 0: 0.1 ms
          * 1: 3 ms (default)
          * 2: 10 ms
          * 3: 20 ms

        :param value: Debounce time for all channels. Use DebounceTime from cpx_ap_enums or
        see datasheet.
        :type value: DebounceTime | int
        """

        if isinstance(value, DebounceTime):
            value = value.value

        value_range_check(value, 4)

        self.base.write_parameter(
            self.position, cpx_ap_parameters.INPUT_DEBOUNCE_TIME, value
        )

        Logging.logger.info(f"{self.name}: Setting debounce time to {value}")

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
            self.position, cpx_ap_parameters.LOAD_SUPPLY_DIAG_SETUP, value
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
            self.position, cpx_ap_parameters.FAIL_STATE_BEHAVIOUR, value
        )

        Logging.logger.info(f"{self.name}: Setting fail state behaviour to {value}")
