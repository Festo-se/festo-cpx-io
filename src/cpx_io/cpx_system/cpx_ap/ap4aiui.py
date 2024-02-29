"""CPX-AP-`*`-4AI-UI-`*` module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

import struct
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap.cpx_ap_enums import TempUnit, ChannelRange


class CpxAp4AiUI(CpxApModule):
    """Class for CPX-AP-`*`-4AI-`*` module"""

    module_codes = {
        8202: "CPX-AP-I-4AI-U-I-RTD-M12",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers

        :return: Values of all channels
        :rtype: list[int]
        """
        reg = self.base.read_reg_data(self.input_register, length=4)
        values = list(struct.unpack("<" + "h" * (len(reg) // 2), reg))
        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

    @CpxBase.require_base
    def read_channel(self, channel: int) -> int:
        """read back the value of one channel

        :param channel: Channel number, starting with 0
        :type channel: int
        :return: Value of the channel
        :rtype: int
        """
        return self.read_channels()[channel]

    @CpxBase.require_base
    def configure_channel_temp_unit(self, channel: int, value: TempUnit | int) -> None:
        """set the channel temperature unit.
          * 0: Celsius (default)
          * 1: Farenheit
          * 2: Kelvin

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel unit. Use TempUnit from cpx_ap_enums or see datasheet.
        :type value: TempUnit | int
        """

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        if isinstance(value, TempUnit):
            value = value.value

        if value not in range(3):
            raise ValueError(f"Value {value} must be between 0 and 2")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.TEMPERATURE_UNIT, value, channel
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} temperature unit to {value}"
        )

    @CpxBase.require_base
    def configure_channel_range(self, channel: int, value: ChannelRange | int) -> None:
        """set the signal range and type of one channel

          * 0: None
          * 1: -10...+10 V
          * 2: -5...+5 V
          * 3: 0...10 V
          * 4: 1...5 V
          * 5: 0...20 mA
          * 6: 4...20 mA
          * 7: 0...500 R
          * 8: PT100
          * 9: NI100

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel range. Use ChannelRange from cpx_ap_enums or see datasheet.
        :type value: ChannelRange | int
        """

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        if isinstance(value, ChannelRange):
            value = value.value

        if value not in range(10):
            raise ValueError(f"Value {value} must be between 0 and 9")

        self.base.write_parameter(
            self.position,
            cpx_ap_parameters.CHANNEL_INPUT_MODE,
            value,
            channel,
        )

        Logging.logger.info(f"{self.name}: Setting channel {channel} range to {value}")

    @CpxBase.require_base
    def configure_channel_limits(
        self, channel: int, upper: int = None, lower: int = None
    ) -> None:
        """
        Set the channel upper and lower limits (Factory setting -> upper: 32767, lower: -32768)
        This will immediately set linear scaling to true
        because otherwise the limits are not stored.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param upper: Channel upper limit in range -32768 ... 32767
        :type upper: int
        :param lower: Channel lower limit in range -32768 ... 32767
        :type lower: int
        """

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        self.configure_linear_scaling(channel, True)

        if isinstance(lower, int):
            if not -32768 <= lower <= 32767:
                raise ValueError(
                    f"Values for low {lower} must be between -32768 and 32767"
                )
        if isinstance(upper, int):
            if not -32768 <= upper <= 32767:
                raise ValueError(
                    f"Values for high {upper} must be between -32768 and 32767"
                )

        if lower is None and isinstance(upper, int):
            self.base.write_parameter(
                self.position, cpx_ap_parameters.UPPER_THRESHOLD_VALUE, upper, channel
            )
        elif upper is None and isinstance(lower, int):
            self.base.write_parameter(
                self.position,
                cpx_ap_parameters.LOWER_THRESHOLD_VALUE,
                lower,
                channel,
            )
        elif isinstance(upper, int) and isinstance(lower, int):
            self.base.write_parameter(
                self.position, cpx_ap_parameters.UPPER_THRESHOLD_VALUE, upper, channel
            )
            self.base.write_parameter(
                self.position, cpx_ap_parameters.LOWER_THRESHOLD_VALUE, lower, channel
            )
        else:
            raise ValueError("Value must be given for upper, lower or both")

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} limit to upper: {upper}, lower: {lower}"
        )

    @CpxBase.require_base
    def configure_hysteresis_limit_monitoring(self, channel: int, value: int) -> None:
        """Hysteresis for measured value monitoring (Factory setting: 100)
        Value must be uint16

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel hysteresis limit in range 0 ... 65535
        :type value: int
        """

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"Value {value} must be between 0 and 65535 (uint16)")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.DIAGNOSIS_HYSTERESIS, value, channel
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} hysteresis limit to {value}"
        )

    @CpxBase.require_base
    def configure_channel_smoothing(self, channel: int, value: int) -> None:
        """set the signal smoothing of one channel. Smoothing is over 2^n values where n is
        'value'. Factory setting: 5 (2^5 = 32 values)

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel smoothing potency in range of 0 ... 15
        :type value: int
        """

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        if value not in range(16):
            raise ValueError(f"'{value}' is not an option")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.SMOOTH_FACTOR, value, channel
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} smoothing to {value}"
        )

    @CpxBase.require_base
    def configure_linear_scaling(self, channel: int, value: bool) -> None:
        """Set linear scaling (Factory setting "False")

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel linear scaling activated (True) or deactivated (False)
        :type value: bool
        """
        if not isinstance(value, bool):
            raise TypeError(f"State {value} must be of type bool (True or False)")

        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be between 0 and 3")

        self.base.write_parameter(
            self.position, cpx_ap_parameters.LINEAR_SCALING_ENABLE, int(value), channel
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} linear scaling to {value}"
        )
