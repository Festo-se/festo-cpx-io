"""CPX-E-4AI-UI module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule
from cpx_io.utils.boollist import int_to_boollist


class CpxE4AiUI(CpxEModule):
    """Class for CPX-E-4AI-UI module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base.next_input_register

        self.base.next_input_register = self.input_register + 5

        Logging.logger.debug(
            f"Configured {self} with input register {self.input_register}"
        )

    @CpxBase.require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers"""
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        data = [CpxBase.decode_int([x]) for x in raw_data]
        return data

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """read module status register. Further information see module datasheet"""
        data = self.base.read_reg_data(self.input_register + 4)[0]
        return int_to_boollist(data, 2)

    @CpxBase.require_base
    def read_channel(self, channel: int) -> int:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def configure_diagnostics(self, short_circuit=None, param_error=None):
        """
        The "Diagnostics of sensor supply short circuit" defines whether
        the diagnostics of the sensor supply in regard to short circuit or
        overload should be activated ("True", default) or deactivated ("False").
        The parameter "Diagnostics of parameterisation error" defines
        if the diagnostics for the
        subsequently listed parameters must be activated ("True", default) or deactivated ("False)
        with regard to unapproved settings:
         * Hysteresis < 0
         * Signal range (sensor type)
         * Lower limit > upper limit
        When the diagnostics are activated,
        the error will be sent to the bus module and displayed on the module by the error LED.
        """
        function_number = 4828 + 64 * self.position + 0
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if short_circuit is None:
            short_circuit = bool((reg & 0x01) >> 0)
        if param_error is None:
            param_error = bool((reg & 0x80) >> 7)

        value_to_write = (
            (reg & 0x7E) | (int(short_circuit) << 0) | (int(param_error) << 7)
        )

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_power_reset(self, value: bool) -> None:
        """
        The "Behaviour after SCO" parameter defines whether
        the voltage remains switched off ("False") or
        automatically switches on ("True, default") again
        after a short circuit or overload of the sensor supply.
        In the case of the "Leave power switched off" setting,
        the CPX-E automation system must be switched off and on to restore the power.
        """
        function_number = 4828 + 64 * self.position + 1
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_data_format(self, value: bool) -> None:
        """The parameter "Data format" defines the “Sign + 15 bit” or “linear scaling”.
        * False (default): Sign + 15 bit
        * True: Linear scaled
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x01
        else:
            value_to_write = reg & 0xFE

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_sensor_supply(self, value: bool) -> None:
        """
        The parameter "Sensor supply" defines if the sensor supply must be switched off ("False")
        or switched on ("True", default).
        The sensor supply can also be switched off and switched on during operation.
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x20
        else:
            value_to_write = reg & 0xDF

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_diagnostics_overload(self, value: bool) -> None:
        """
        The parameter "Diagnostics of overload at analogue inputs" defines
        if the diagnostics for the current inputs
        must be activated ("True", default) or deactivated ("False") with regard to overload.
        When the diagnostics are activated,
        the error at an input current of >30 mA will be sent to the bus module and
        displayed with the error LED on the module.
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x40
        else:
            value_to_write = reg & 0xBF

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_behaviour_overload(self, value: bool) -> None:
        """
        The parameter "Behaviour after overload at analogue inputs" defines if
        the power remains switched off ("False") after an overload at the inputs or
        if it should be switched on again ("True", default) automatically.
        In the case of the "Leave power switched off" setting,
        the automation system CPX-E must be switched off and on to restore the power.
        """
        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)

        # Fill in the unchanged values from the register
        if value:
            value_to_write = reg | 0x80
        else:
            value_to_write = reg & 0x7F

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_hysteresis_limit_monitoring(
        self, lower: int | None = None, upper: int | None = None
    ) -> None:
        """
        The parameter "Hysteresis of limit monitoring" defines
        the hysteresis value of the limit monitoring for all channels.
        The set hysteresis value must not be larger
        than the difference between the upper and lower limit values.
        The defined value is not checked for validity and
        incorrect parameterisations will be applied.
        """
        if lower:
            if lower < 0 or lower > 32767:
                raise ValueError("Values for low {low} must be between 0 and 32767")
        if upper:
            if upper < 0 or upper > 32767:
                raise ValueError("Values for high {high} must be between 0 and 32767")

        function_number_lower = 4828 + 64 * self.position + 7
        function_number_upper = 4828 + 64 * self.position + 8

        if lower is None and isinstance(upper, int):
            self.base.write_function_number(function_number_upper, upper)
        elif upper is None and isinstance(lower, int):
            self.base.write_function_number(function_number_lower, lower)
        elif isinstance(upper, int) and isinstance(lower, int):
            self.base.write_function_number(function_number_upper, upper)
            self.base.write_function_number(function_number_lower, lower)
        else:
            raise ValueError("Value must be given for upper, lower or both")

    @CpxBase.require_base
    def configure_channel_diagnostics_limits(
        self, channel: int, lower: bool | None = None, upper: bool | None = None
    ) -> None:
        """The parameter " Diagnostics of lower/upper limit" defines if the diagnostics for the input signals must be
        activated or deactivated with regard to compliance with the defined lower limits.
        When the diagnostics are activated, the error will be sent to the bus module and displayed on the
        module by the error LED."""

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 9 + channel

        reg = self.base.read_function_number(function_number)

        # if not given, use the values of the register
        if lower is None:
            lower = reg & 0b1
        if upper is None:
            upper = (reg & 0b10) >> 1

        reg_to_write = (reg & 0xFC) | (int(upper) << 1) | int(lower)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_wire_break(
        self, channel: int, value: bool
    ) -> None:
        """The parameter "Wire break diagnostics" defines whether the diagnostics for the input signals must be
        activated or deactivated with regard to a shortfall of the input current.
        When the diagnostics are activated, the error at an input current of <1.2 mA will be sent to the bus
        module and displayed with the error LED on the module.
        The parameter is only effective with a defined signal range of 4 … 20 mA"""

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 9 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFB) | (int(value) << 2)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_underflow_overflow(
        self, channel: int, value: bool
    ) -> None:
        """The parameter " Underflow/overflow diagnostics" defines whether the diagnostics of the input signals should be activated or deactivated with regard to compliance with the defined signal ranges.
        When the diagnostics are activated, the error will be sent to the bus module and displayed on the
        module by the error LED."""

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 9 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xF7) | (int(value) << 3)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_diagnostics_parameter_error(
        self, channel: int, value: bool
    ) -> None:
        """The parameter "Parameter error diagnostics" defines if the diagnostics for the subsequently listed
        parameters must be activated or deactivated with regard to unapproved settings:
        - Signal range
        - Lower limit
        - Upper limit
        When the diagnostics are activated, the error will be sent to the bus module and displayed on the
        module by the error LED"""

        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number = 4828 + 64 * self.position + 9 + channel

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0x7F) | (int(value) << 7)

        self.base.write_function_number(function_number, reg_to_write)

    @CpxBase.require_base
    def configure_channel_range(self, channel: int, signalrange: str) -> None:
        """The parameter "Signal range" defines the signal range of the channels 0 … 3
        independently of each other"""

        bitmask = {
            "None": 0b0000,
            "0-10V": 0b0001,
            "-10-+10V": 0b0010,
            "-5-+5V": 0b0011,
            "1-5V": 0b0100,
            "0-20mA": 0b0101,
            "4-20mA": 0b0110,
            "-20-+20mA": 0b0111,
            "0-10VoU": 0b1000,
            "0-20mAoU": 0b1001,
            "4-20mAoU": 0b1010,
        }
        if signalrange not in bitmask:
            raise ValueError(
                f"'{signalrange}' is not an option. Choose from {bitmask.keys()}"
            )

        function_number = 4828 + 64 * self.position

        reg_01 = self.base.read_function_number(function_number + 13)
        reg_23 = self.base.read_function_number(function_number + 14)

        if channel == 0:
            function_number += 13
            value_to_write = (reg_01 & 0xF0) | bitmask[signalrange]
        elif channel == 1:
            function_number += 13
            value_to_write = (reg_01 & 0x0F) | bitmask[signalrange] << 4
        elif channel == 2:
            function_number += 14
            value_to_write = (reg_23 & 0xF0) | bitmask[signalrange]
        elif channel == 3:
            function_number += 14
            value_to_write = (reg_23 & 0x0F) | bitmask[signalrange] << 4
        else:
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_channel_smoothing(self, channel: int, smoothing_power: int) -> None:
        """The parameter "Smoothing factor" defines the measured value smoothing for
        the channels 0 … 3 independent from each other.
        The measured value smoothing can be used to suppress interference."""

        if smoothing_power > 15:
            raise ValueError(f"'{smoothing_power}' is not an option")

        bitmask = smoothing_power

        function_number = 4828 + 64 * self.position

        reg_01 = self.base.read_function_number(function_number + 15)
        reg_23 = self.base.read_function_number(function_number + 16)

        if channel == 0:
            function_number += 15
            value_to_write = (reg_01 & 0xF0) | bitmask
        elif channel == 1:
            function_number += 15
            value_to_write = (reg_01 & 0x0F) | bitmask << 4
        elif channel == 2:
            function_number += 16
            value_to_write = (reg_23 & 0xF0) | bitmask
        elif channel == 3:
            function_number += 16
            value_to_write = (reg_23 & 0x0F) | bitmask << 4
        else:
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        self.base.write_function_number(function_number, value_to_write)

    @CpxBase.require_base
    def configure_channel_limits(
        self, channel: int, upper: int | None = None, lower: int | None = None
    ) -> None:
        """
        The parameters "Lower limit" and "Upper limit" define the lower or upper limit of the channels 0 … 3
        independent from each other.
        When the input value falls short of or exceeds the parameterised limits, an error will be displayed
        provided that the relevant parameter Diagnostics of lower/upper limit is activated
        The limit values are checked for validity during parameterisation. Invalid parameterisations are not
        accepted and the module uses the last valid parameterisations.
        The upper limit value must always be greater than the lower limit value. The permitted limits depend
        on the parameterised data format.
        With the data format "linear scaled", the limits function as scaling end values
        """
        if channel not in range(4):
            raise ValueError(f"Channel '{channel}' is not in range 0...3")

        function_number_lower = 4828 + 64 * self.position + 17 + channel * 2
        function_number_upper = 4828 + 64 * self.position + 25 + channel * 2

        if isinstance(lower, int):
            if (
                not -32767 <= lower <= 32767
            ):  # might be wrong. Values are according to datasheet
                raise ValueError(
                    "Values for low {low} must be between -32767 and 32767"
                )
        if isinstance(upper, int):
            if (
                not -32767 <= upper <= 32767
            ):  # might be wrong. Values are according to datasheet
                raise ValueError(
                    "Values for high {high} must be between -32767 and 32767"
                )

        if isinstance(lower, int):
            lower = CpxBase.encode_int(lower, data_type="int16")[0]
            value_lower_low_byte = lower & 0xFF
            value_lower_high_byte = (lower & 0xFF00) >> 8
        if isinstance(upper, int):
            value_upper_low_byte = upper & 0xFF
            value_upper_high_byte = (upper & 0xFF00) >> 8
            upper = CpxBase.encode_int(upper, data_type="int16")[0]

        if lower is None and isinstance(upper, int):
            self.base.write_function_number(function_number_upper, value_upper_low_byte)
            self.base.write_function_number(
                function_number_upper + 1, value_upper_high_byte
            )

        elif upper is None and isinstance(lower, int):
            self.base.write_function_number(function_number_lower, value_lower_low_byte)
            self.base.write_function_number(
                function_number_lower + 1, value_lower_high_byte
            )

        elif isinstance(upper, int) and isinstance(lower, int):
            self.base.write_function_number(function_number_lower, value_lower_low_byte)
            self.base.write_function_number(
                function_number_lower + 1, value_lower_high_byte
            )
            self.base.write_function_number(function_number_upper, value_upper_low_byte)
            self.base.write_function_number(
                function_number_upper + 1, value_upper_high_byte
            )

        else:
            raise ValueError("Value must be given for upper, lower or both")
