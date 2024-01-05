"""CPX-AP-*-4AI-UI module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule


class CpxAp4AiUI(CpxApModule):
    """Class for CPX-AP-*-4AI-* module"""

    module_codes = {
        8202: "CPX-AP-I-4AI-U-I-RTD-M12",
    }

    def __getitem__(self, key):
        return self.read_channel(key)

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers"""
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        return [CpxBase.decode_int([i], data_type="int16") for i in raw_data]

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def configure_channel_temp_unit(self, channel: int, unit: str) -> None:
        """
        set the channel temperature unit ("C": Celsius (default), "F": Fahrenheit, "K": Kelvin)
        """
        uid = 20032
        value = {
            "C": 0,
            "F": 1,
            "K": 2,
        }
        if unit not in value:
            raise ValueError(f"'{unit}' is not an option. Choose from {value.keys()}")

        self.base.write_parameter(self.position, uid, channel, value[unit])

    @CpxBase.require_base
    def configure_channel_range(self, channel: int, signalrange: str) -> None:
        """set the signal range and type of one channel"""
        reg_id = 20043
        value = {
            "None": 0,
            "-10-+10V": 1,
            "-5-+5V": 2,
            "0-10V": 3,
            "1-5V": 4,
            "0-20mA": 5,
            "4-20mA": 6,
            "0-500R": 7,
            "PT100": 8,
            "NI100": 9,
        }
        if signalrange not in value:
            raise ValueError(
                f"'{signalrange}' is not an option. Choose from {value.keys()}"
            )

        self.base.write_parameter(self.position, reg_id, channel, value[signalrange])

    @CpxBase.require_base
    def configure_channel_limits(
        self, channel: int, upper: int | None = None, lower: int | None = None
    ) -> None:
        """
        Set the channel upper and lower limits (Factory setting -> upper: 32767, lower: -32768)
        This will immediately set linear scaling to true
        because otherwise the limits are not stored.
        """

        self.configure_linear_scaling(channel, True)

        upper_id = 20044
        lower_id = 20045

        if isinstance(lower, int):
            if not -32768 <= lower <= 32767:
                raise ValueError(
                    "Values for low {low} must be between -32768 and 32767"
                )
        if isinstance(upper, int):
            if not -32768 <= upper <= 32767:
                raise ValueError(
                    "Values for high {high} must be between -32768 and 32767"
                )

        if lower is None and isinstance(upper, int):
            self.base.write_parameter(self.position, upper_id, channel, upper)
        elif upper is None and isinstance(lower, int):
            self.base.write_parameter(self.position, lower_id, channel, lower)
        elif isinstance(upper, int) and isinstance(lower, int):
            self.base.write_parameter(self.position, upper_id, channel, upper)
            self.base.write_parameter(self.position, lower_id, channel, lower)
        else:
            raise ValueError("Value must be given for upper, lower or both")

    @CpxBase.require_base
    def configure_hysteresis_limit_monitoring(self, channel: int, value: int) -> None:
        """Hysteresis for measured value monitoring (Factory setting: 100)
        Value must be uint16
        """
        uid = 20046
        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"Value {value} must be between 0 and 65535 (uint16)")

        self.base.write_parameter(self.position, uid, channel, value)

    @CpxBase.require_base
    def configure_channel_smoothing(self, channel: int, smoothing_power: int) -> None:
        """set the signal smoothing of one channel. Smoothing is over 2^n values where n is
        smoothing_power. Factory setting: 5 (2^5 = 32 values)
        """
        uid = 20107
        if smoothing_power > 15:
            raise ValueError(f"'{smoothing_power}' is not an option")

        self.base.write_parameter(self.position, uid, channel, smoothing_power)

    @CpxBase.require_base
    def configure_linear_scaling(self, channel: int, state: bool) -> None:
        """Set linear scaling (Factory setting "False")"""
        uid = 20111

        self.base.write_parameter(self.position, uid, channel, int(state))
