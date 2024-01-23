"""CPX-AP-`*`-16DI-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.utils.boollist import int_to_boollist
from cpx_io.utils.logging import Logging


class CpxAp16Di(CpxApModule):
    """Class for CPX-AP-`*`-16DI-`*` module"""

    module_codes = {
        12289: "CPX-AP-A-16DI-D-M12-5P",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values

        :return: Values of all channels
        :rtype: list[bool]
        """
        data = self.base.read_reg_data(self.input_register)[0]
        ret = int_to_boollist(data, 2)
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
    def configure_debounce_time(self, value: int) -> None:
        """
        The "Input debounce time" parameter defines when an edge change of the sensor signal
        shall be assumed as a logical input signal. In this way, unwanted signal edge changes
        can be suppressed during switching operations (bouncing of the input signal).
        Accepted values are
        - 0: 0.1 ms
        - 1: 3 ms (default)
        - 2: 10 ms
        - 3: 20 ms

        :param value: Debounce time for all channels in range 0..3 (see datasheet)
        :type value: int
        """
        uid = 20014

        if not 0 <= value <= 3:
            raise ValueError("Value {value} must be between 0 and 3")

        self.base.write_parameter(self.position, uid, 0, value)

        value_str = ["0.1 ms", "3 ms", "10 ms", "20 ms"]
        Logging.logger.info(f"{self.name}: Setting debounce time to {value_str[value]}")
