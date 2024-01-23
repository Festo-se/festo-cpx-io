"""CPX-E-1CI module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from dataclasses import dataclass

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_e.cpx_e_module import CpxEModule
from cpx_io.utils.boollist import int_to_boollist
from cpx_io.utils.logging import Logging


class CpxE1Ci(CpxEModule):
    """Class for CPX-E-1CI counter module"""

    # pylint: disable=too-many-public-methods

    @dataclass
    class StatusWord(CpxBase.BitwiseReg16):
        """Statusword dataclass"""

        # pylint: disable=too-many-instance-attributes
        # 16 required

        di0: bool
        di1: bool
        di2: bool
        di3: bool
        _: None
        latchin_missed: bool
        latching_set: bool
        latching_blocked: bool
        lower_cl_exceeded: bool
        upper_cl_exceeded: bool
        counting_direction: bool
        counter_blocked: bool
        counter_set: bool
        enable_di2: bool
        enable_zero: bool
        speed_measurement: bool

    @dataclass
    class ProcessData(CpxBase.BitwiseReg8):
        """Processdata dataclass"""

        # pylint: disable=too-many-instance-attributes
        # 8 required

        enable_setting_di2: bool
        enable_setting_zero: bool
        set_counter: bool
        block_counter: bool
        overrun_cl_confirm: bool
        speed_measurement: bool
        confirm_latching: bool
        block_latching: bool

    def configure(self, *args):
        super().configure(*args)

        self.base.next_output_register = self.output_register + 1
        self.base.next_input_register = self.input_register + 8

    @CpxBase.require_base
    def read_value(self) -> int:
        """Read the counter value or speed (if process data "speed_measurement" is set)

        :return: counter value or speed
        :rtype: int"""
        reg = self.base.read_reg_data(self.input_register, length=2)
        value = CpxBase.decode_int(reg, data_type="uint32")

        Logging.logger.info(f"{self.name}: Read counter/speed value: {value}")
        return value

    @CpxBase.require_base
    def read_latching_value(self) -> int:
        """Read the latching value

        :return: latching value
        :rtype: int"""
        reg = self.base.read_reg_data(self.input_register + 2, length=2)
        value = CpxBase.decode_int(reg, data_type="uint32")

        Logging.logger.info(f"{self.name}: Read latching value: {value}")
        return value

    @CpxBase.require_base
    def read_status_word(self) -> StatusWord:
        """Read the status word

        :return: status word
        :rtype: StatusWord"""
        reg = self.base.read_reg_data(self.input_register + 4)[0]

        sw = self.StatusWord

        ret = sw.from_int(reg)
        Logging.logger.info(f"{self.name}: Read status word: {ret}")
        return ret

    @CpxBase.require_base
    def read_process_data(self) -> ProcessData:
        """Read back the process data

        :return: process data
        :rtype: ProcessData"""
        # echo output data bit 0 ... 15 are in input_register + 6
        reg = self.base.read_reg_data(self.input_register + 6)[0]

        pd = self.ProcessData

        ret = pd.from_int(reg)
        Logging.logger.info(f"{self.name}: Read process data: {ret}")
        return ret

    @CpxBase.require_base
    def write_process_data(self, **kwargs) -> None:
        """Write the process data.

        Available keywordarguments are:
        * enable_setting_di2: enable setting counter value via input I2 (1=enabled)
        * enable_setting_zero: enable setting counter value via zero pulse (1=enabled)
        * set_counter: setting the counter to the load value (1=set)
        * block_counter: switch counter to inactive (1=block)
        * overrun_cl_confirm: confirm overrun of upper and lower count limit (1=acknowledge overrun)
        * speed_measurement: speed measurement instead of counter values (1=active)
        * confirm_latching:  confirm latching event (1=acknowledge latching event)
        * block_latching: switch latching to inactive (1=block)
        """
        process_data = self.read_process_data()
        pd_updated_dict = {**process_data.__dict__, **kwargs}

        data = (
            (int(pd_updated_dict.get("enable_setting_di2")) << 0)
            | (int(pd_updated_dict.get("enable_setting_zero")) << 1)
            | (int(pd_updated_dict.get("set_counter")) << 2)
            | (int(pd_updated_dict.get("block_counter")) << 3)
            | (int(pd_updated_dict.get("overrun_cl_confirm")) << 4)
            | (int(pd_updated_dict.get("speed_measurement")) << 5)
            | (int(pd_updated_dict.get("confirm_latching")) << 6)
            | (int(pd_updated_dict.get("block_latching")) << 7)
        )
        reg_data = CpxBase.decode_int([data])
        self.base.write_reg_data(reg_data, self.output_register)

        Logging.logger.info(f"{self.name}: Write process data {kwargs}")

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """Read module status register. Further information see module datasheet

        :return: status information (see datasheet)
        :rtype: list[bool]"""
        data = self.base.read_reg_data(self.input_register + 7)[0]

        ret = int_to_boollist(data, num_bytes=2)
        Logging.logger.info(f"{self.name}: Read status {ret}")
        return ret

    @CpxBase.require_base
    def configure_signal_type(self, value: int) -> None:
        """The parameter “Signal type/encoder type” defines the encoder supply and connection
        type of the encoder.

        Accepted values:
          * 0: Encoder 5 Vdc differential (default)
          * 1: Encoder 5 Vdc single ended
          * 2: Encoder 24 Vdc single ended
          * 3: Invalid setting

        :param value: Signal type (see datasheet)
        :type value: int
        """
        if value in range(4):
            function_number = 4828 + 64 * self.position + 6
            reg = self.base.read_function_number(function_number)
            value_to_write = (reg & 0xFC) | value
            self.base.write_function_number(function_number, value_to_write)
        else:
            raise ValueError(f"value {value} must be in range 0 ... 3")

        Logging.logger.info(f"{self.name}: Set signal type to {value}")

    @CpxBase.require_base
    def configure_signal_evaluation(self, value: int) -> None:
        """The “Signal evaluation” parameter defines the encoder type and evaluation

        Accepted values:
        * 0: Incremental encoder with single evaluation
        * 1: Incremental encoder with double evaluation
        * 2: Incremental encoder with quadruple evaluation (default)
        * 3: Pulse generator with or without direction signal

        :param value: Signal evaluation (see datasheet)
        :type value: int
        """
        if value in range(4):
            function_number = 4828 + 64 * self.position + 7
            reg = self.base.read_function_number(function_number)
            value_to_write = (reg & 0xFC) | value
            self.base.write_function_number(function_number, value_to_write)
        else:
            raise ValueError(f"value {value} must be in range 0 ... 3")

        Logging.logger.info(f"{self.name}: Set signal evaluation to {value}")

    @CpxBase.require_base
    def configure_monitoring_of_cable_brake(self, value: bool) -> None:
        """The “Monitoring of cable break” parameter defines whether a diagnostic message
        should be output when a cable break of the encoder cable is detected.

        Available options:
          * False: No diagnostic message (default)
          * True: Diagnostic message active

        The “Monitoring of cable break” parameter is only relevant for encoder 5 V DC
        (differential) with tracks A and B offset in phase.

        :param value: True if diagnostic message should be active
        :type value: bool
        """

        function_number = 4828 + 64 * self.position + 8

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFE) | int(value)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(f"{self.name}: Set cable brake monitoring to {value}")

    @CpxBase.require_base
    def configure_monitoring_of_tracking_error(self, value: bool) -> None:
        """The “Monitoring of tracking error” parameter defines whether a diagnostic message
        should be output when a tracking error is detected.

        Available options:
          * False: No diagnostic message (default)
          * True: Diagnostic message active

        The “Monitoring of tracking error” parameter is only relevant for encoders with tracks
        A and B offset in phase.

        :param value: True if diagnostic message should be active
        :type value: bool
        """

        function_number = 4828 + 64 * self.position + 9

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFE) | int(value)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(f"{self.name}: Set tracking error monitoring to {value}")

    @CpxBase.require_base
    def configure_monitoring_of_zero_pulse(self, value: bool) -> None:
        """The “Monitoring of zero pulse” parameter defines whether a diagnostic message should be
        output when a zero pulse error is detected.

        Available options:
          * False: No diagnostic message (default)
          * True: Diagnostic message active

        The “Monitoring of zero pulse” parameter is only relevant for encoders with zero track
        (track 0). With this diagnostic function enabled, the number of pulses per zero pulse
        must be set correctly using the “Pulses per zero pulse” parameter.

        :param value: True if diagnostic message should be active
        :type value: bool
        """

        function_number = 4828 + 64 * self.position + 10

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFE) | int(value)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(f"{self.name}: Set zero pulse monitoring to {value}")

    @CpxBase.require_base
    def configure_pulses_per_zero_pulse(self, value: int) -> None:
        """The “Pulses per zero pulse” parameter defines the number of pulses on track A or
        track B between 2 pulses of track 0. Value must be between 0 and 65535 The “Pulses
        per zero pulse” parameter is only relevant for encoders with zero track (track 0)
        and is required for zero pulse monitoring via the “Monitoring of zero pulse” parameter

        :param value: number of pulses on tracks between 2 pulses of track 0
        :type value: int
        """

        function_number = 4828 + 64 * self.position + 11

        if value in range(65536):
            regs = [value & 0xFF, value >> 8]
            self.base.write_function_number(function_number, regs[0])
            self.base.write_function_number(function_number + 1, regs[1])

        else:
            raise ValueError(f"Value {value} must be in range 0 ... 65535")

        Logging.logger.info(f"{self.name}: set pulses per zero pulse to {value}")

    @CpxBase.require_base
    def configure_latching_signal(self, value: bool) -> None:
        """The “Latching signal” parameter defines whether the digital input I0 or the
        zero pulse (track 0) is used as signal source to trigger the “Latching” function.

        Available options:
          * False: Evaluate input I0 (default)
          * True: Evaluate zero pulse

        :param value: Sets the input for the latching signal
        :type value: bool
        """

        function_number = 4828 + 64 * self.position + 13

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFE) | int(value)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(f"{self.name}: set latching signal to {value}")

    @CpxBase.require_base
    def configure_latching_event(self, value: int) -> None:
        """The “Latching event” parameter defines whether the “Latching” function is
        triggered on a rising and/or falling edge.

        Available options:
          * 0: Invalid setting
          * 1: Latching on rising edge (default)
          * 2: Latching on falling edge
          * 3: Latching on rising and falling edge

        :param value: Latching event parameter
        :type value: int
        """
        if value in range(4):
            function_number = 4828 + 64 * self.position + 14
            reg = self.base.read_function_number(function_number)
            value_to_write = (reg & 0xFC) | value
            self.base.write_function_number(function_number, value_to_write)
        else:
            raise ValueError(f"Value {value} must be in range 0 ... 3")

        Logging.logger.info(f"{self.name}: set latching event to {value}")

    @CpxBase.require_base
    def configure_latching_response(self, value: bool) -> None:
        """The “Latching response” parameter defines whether, if there is a latching event,
        the current counter value is continuous (False, default) or is set to the load value (True).

        :param value: Latching response parameter
        :type value: bool
        """

        function_number = 4828 + 64 * self.position + 15

        reg = self.base.read_function_number(function_number)

        reg_to_write = (reg & 0xFE) | int(value)

        self.base.write_function_number(function_number, reg_to_write)

        Logging.logger.info(f"{self.name}: set latching response to {value}")

    @CpxBase.require_base
    def configure_upper_counter_limit(self, value: int) -> None:
        """The “Upper count limit” parameter defines the upper count limit in the value range
        0 ... 4,294,967,295 (2^32 - 1). If the value set for the upper count limit is lower than
        the current counter value, the counter value is reduced to the set count limit.
        The value for the upper count limit must be larger than the value for the lower count limit.
        Invalid values will result in an error (error number 2)

        :param value: Upper count limit
        :type value: int
        """

        function_number = 4828 + 64 * self.position + 16

        if value in range(2**32):
            regs = CpxBase.encode_int(value, data_type="uint32")

            self.base.write_function_number(function_number + 0, regs[1] & 0xFF)
            self.base.write_function_number(function_number + 1, regs[1] >> 8)
            self.base.write_function_number(function_number + 2, regs[0] & 0xFF)
            self.base.write_function_number(function_number + 3, regs[0] >> 8)

        else:
            raise ValueError(f"Value {value} must be in range 0 ... (2^32 - 1)")

        Logging.logger.info(f"{self.name}: set upper counter limit to {value}")

    @CpxBase.require_base
    def configure_lower_counter_limit(self, value: int) -> None:
        """The “Lower count limit” parameter defines the lower count limit in the value range
        0 ... 4,294,967,295 (2^32 - 1). If the value set for the lower count limit is higher than
        the current counter value, the counter value is increased to the set count limit.
        The value for the lower count limit must be smaller than the value for the upper count
        limit. Invalid values will result in an error (error number 29).

        :param value: Lower count limit
        :type value: int
        """

        function_number = 4828 + 64 * self.position + 20

        if value in range(2**32):
            regs = CpxBase.encode_int(value, data_type="uint32")

            self.base.write_function_number(function_number + 0, regs[1] & 0xFF)
            self.base.write_function_number(function_number + 1, regs[1] >> 8)
            self.base.write_function_number(function_number + 2, regs[0] & 0xFF)
            self.base.write_function_number(function_number + 3, regs[0] >> 8)

        else:
            raise ValueError(f"Value {value} must be in range 0 ... 2^32")

        Logging.logger.info(f"{self.name}: set lower counter limit to {value}")

    @CpxBase.require_base
    def configure_load_value(self, value: int) -> None:
        """The “Load value” parameter defines the value in the value range 0 ... 4,294,967,295
        (2^32 - 1) that is adopted as the counter value when the “Set counter” function is
        enabled or during latching with the parameter setting “Latching response = load value”

        :param value: Load value
        :type value: int
        """

        function_number = 4828 + 64 * self.position + 24

        if value in range(2**32):
            regs = CpxBase.encode_int(value, data_type="uint32")
            # divide in 8 bit registers
            self.base.write_function_number(function_number + 0, regs[1] & 0xFF)
            self.base.write_function_number(function_number + 1, regs[1] >> 8)
            self.base.write_function_number(function_number + 2, regs[0] & 0xFF)
            self.base.write_function_number(function_number + 3, regs[0] >> 8)

        else:
            raise ValueError(f"Value {value} must be in range 0 ... 2^32")

        Logging.logger.info(f"{self.name}: set load value to {value}")

    @CpxBase.require_base
    def configure_debounce_time_for_digital_inputs(self, value: int) -> None:
        """The parameter “Debounce time for digital inputs” defines the total debounce time
        for all digital inputs I0 ... I3

        Available options are
          * 0: 20 us (default)
          * 1: 100 us
          * 2: 3 ms
          * 3: Invalid setting

        :param value: debounce time option
        :type value: int
        """

        if value in range(4):
            function_number = 4828 + 64 * self.position + 28
            reg = self.base.read_function_number(function_number)
            value_to_write = (reg & 0xFC) | value
            self.base.write_function_number(function_number, value_to_write)
        else:
            raise ValueError(f"Value {value} must be in range 0 ... 3")

        value_str = ["20 us", "100 us", "3 ms", "Invalid setting"]
        Logging.logger.info(f"{self.name}: set debounce time to {value_str[value]}")

    @CpxBase.require_base
    def configure_integration_time_for_speed_measurement(self, value: int) -> None:
        """The parameter “Integration time for speed measurement” defines the length of the
        measurement cycles for determining the measured value in the “Speed measurement” function
         * 0: 1 ms
         * 1: 10 ms (default)
         * 2: 100 ms
         * 3: Invalid setting

        :param value: integration time parameter
        :type value: int
        """

        if value in range(4):
            function_number = 4828 + 64 * self.position + 29
            reg = self.base.read_function_number(function_number)
            value_to_write = (reg & 0xFC) | value
            self.base.write_function_number(function_number, value_to_write)
        else:
            raise ValueError(f"Value {value} must be in range 0 ... 3")

        value_str = ["1 ms", "10 ms", "100 ms", "Invalid setting"]
        Logging.logger.info(f"{self.name}: set debounce time to {value_str[value]}")
