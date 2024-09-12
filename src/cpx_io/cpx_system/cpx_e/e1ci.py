"""CPX-E-1CI module implementation"""

# pylint: disable=duplicate-code
# intended: modules have similar functions

from dataclasses import dataclass

from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import value_range_check
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_e.cpx_e_enums import (
    DigInDebounceTime,
    IntegrationTime,
    SignalType,
    SignalEvaluation,
    LatchingEvent,
)


class CpxE1Ci(CpxModule):
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
        _: None  # spacer for not-used bit
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

        self.base.next_output_register = self.system_entry_registers.outputs + 1
        self.base.next_input_register = self.system_entry_registers.inputs + 8

    @CpxBase.require_base
    def read_value(self) -> int:
        """Read the counter value or speed (if process data "speed_measurement" is set)

        :return: counter value or speed
        :rtype: int"""
        reg = self.base.read_reg_data(self.system_entry_registers.inputs, length=2)
        value = int.from_bytes(reg, byteorder="little")

        Logging.logger.info(f"{self.name}: Read counter/speed value: {value}")
        return value

    @CpxBase.require_base
    def read_latching_value(self) -> int:
        """Read the latching value

        :return: latching value
        :rtype: int"""
        reg = self.base.read_reg_data(self.system_entry_registers.inputs + 2, length=2)
        value = int.from_bytes(reg, byteorder="little")

        Logging.logger.info(f"{self.name}: Read latching value: {value}")
        return value

    @CpxBase.require_base
    def read_status_word(self) -> StatusWord:
        """Read the status word

        :return: status word
        :rtype: StatusWord"""
        reg = self.base.read_reg_data(self.system_entry_registers.inputs + 4)

        status_word = self.StatusWord.from_bytes(reg)

        Logging.logger.info(f"{self.name}: Read status word: {status_word}")
        return status_word

    @CpxBase.require_base
    def read_process_data(self) -> ProcessData:
        """Read back the process data

        :return: process data
        :rtype: ProcessData"""
        # echo output data bit 0 ... 15 are in system_entry_registers.inputs + 6
        reg = self.base.read_reg_data(self.system_entry_registers.inputs + 6)

        process_data = self.ProcessData.from_bytes(reg[:1])  # take only first byte

        Logging.logger.info(f"{self.name}: Read process data: {process_data}")
        return process_data

    @CpxBase.require_base
    def write_process_data(self, **kwargs) -> None:
        """Write the process data.

        Available keywordarguments are:
         * enable_setting_di2: enable setting counter value via input I2 (1=enabled)
         * enable_setting_zero: enable setting counter value via zero pulse (1=enabled)
         * set_counter: setting the counter to the load value (1=set)
         * block_counter: switch counter to inactive (1=block)
         * overrun_cl_confirm: confirm overrun of upper/lower count limit (1=acknowledge overrun)
         * speed_measurement: speed measurement instead of counter values (1=active)
         * confirm_latching:  confirm latching event (1=acknowledge latching event)
         * block_latching: switch latching to inactive (1=block)
        """
        process_data = self.read_process_data()
        pd_updated_dict = {**process_data.__dict__, **kwargs}

        data = [
            pd_updated_dict.get("enable_setting_di2"),
            pd_updated_dict.get("enable_setting_zero"),
            pd_updated_dict.get("set_counter"),
            pd_updated_dict.get("block_counter"),
            pd_updated_dict.get("overrun_cl_confirm"),
            pd_updated_dict.get("speed_measurement"),
            pd_updated_dict.get("confirm_latching"),
            pd_updated_dict.get("block_latching"),
        ]
        reg_data = boollist_to_bytes(data)
        self.base.write_reg_data(reg_data, self.system_entry_registers.outputs)

        Logging.logger.info(f"{self.name}: Write process data {kwargs}")

    @CpxBase.require_base
    def read_status(self) -> list[bool]:
        """Read module status register. Further information see module datasheet

        :return: status information (see datasheet)
        :rtype: list[bool]"""
        data = self.base.read_reg_data(self.system_entry_registers.inputs + 7)

        ret = bytes_to_boollist(data)
        Logging.logger.info(f"{self.name}: Read status {ret}")
        return ret

    @CpxBase.require_base
    def configure_signal_type(self, value: SignalType | int) -> None:
        """The parameter “Signal type/encoder type” defines the encoder supply and connection
        type of the encoder.

          * 0: Encoder 5 Vdc differential (default)
          * 1: Encoder 5 Vdc single ended
          * 2: Encoder 24 Vdc single ended

        :param value: Signal type. Use SignalType from cpx_e_enums or see datasheet.
        :type value: SignalType | int
        """
        if isinstance(value, SignalType):
            value = value.value

        value_range_check(value, 3)

        function_number = 4828 + 64 * self.position + 6
        reg = self.base.read_function_number(function_number)
        value_to_write = (reg & 0xFC) | value
        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Set signal type to {value}")

    @CpxBase.require_base
    def configure_signal_evaluation(self, value: SignalEvaluation | int) -> None:
        """The “Signal evaluation” parameter defines the encoder type and evaluation

         * 0: Incremental encoder with single evaluation
         * 1: Incremental encoder with double evaluation
         * 2: Incremental encoder with quadruple evaluation (default)
         * 3: Pulse generator with or without direction signal

        :param value: Signal evaluation. Use SignalEvaluation from cpx_e_enums or see datasheet.
        :type value: SignalEvaluation | int
        """
        if isinstance(value, SignalEvaluation):
            value = value.value

        value_range_check(value, 4)

        function_number = 4828 + 64 * self.position + 7
        reg = self.base.read_function_number(function_number)
        value_to_write = (reg & 0xFC) | value
        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: Set signal evaluation to {value}")

    @CpxBase.require_base
    def configure_monitoring_of_cable_brake(self, value: bool) -> None:
        """The “Monitoring of cable break” parameter defines whether a diagnostic message
        should be output when a cable break of the encoder cable is detected.

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

        value_range_check(value, 65536)

        regs = [value & 0xFF, value >> 8]
        self.base.write_function_number(function_number, regs[0])
        self.base.write_function_number(function_number + 1, regs[1])

        Logging.logger.info(f"{self.name}: set pulses per zero pulse to {value}")

    @CpxBase.require_base
    def configure_latching_signal(self, value: bool) -> None:
        """The “Latching signal” parameter defines whether the digital input I0 or the
        zero pulse (track 0) is used as signal source to trigger the “Latching” function.

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
    def configure_latching_event(self, value: LatchingEvent | int) -> None:
        """The “Latching event” parameter defines whether the “Latching” function is
        triggered on a rising and/or falling edge.

          * 1: Latching on rising edge (default)
          * 2: Latching on falling edge
          * 3: Latching on rising and falling edge

        :param value: Latching event parameter. Use LatchingEvent from cpx_e_enums or see datasheet
        :type value: LatchingEvent | int
        """

        if isinstance(value, LatchingEvent):
            value = value.value

        value_range_check(value, 1, 4)

        function_number = 4828 + 64 * self.position + 14
        reg = self.base.read_function_number(function_number)
        value_to_write = (reg & 0xFC) | value
        self.base.write_function_number(function_number, value_to_write)

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

        value_range_check(value, 2**32)

        self.base.write_function_number(function_number + 0, (value >> 0) & 0xFF)
        self.base.write_function_number(function_number + 1, (value >> 8) & 0xFF)
        self.base.write_function_number(function_number + 2, (value >> 16) & 0xFF)
        self.base.write_function_number(function_number + 3, (value >> 24) & 0xFF)

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

        value_range_check(value, 2**32)

        self.base.write_function_number(function_number + 0, (value >> 0) & 0xFF)
        self.base.write_function_number(function_number + 1, (value >> 8) & 0xFF)
        self.base.write_function_number(function_number + 2, (value >> 16) & 0xFF)
        self.base.write_function_number(function_number + 3, (value >> 24) & 0xFF)

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

        value_range_check(value, 2**32)

        self.base.write_function_number(function_number + 0, (value >> 0) & 0xFF)
        self.base.write_function_number(function_number + 1, (value >> 8) & 0xFF)
        self.base.write_function_number(function_number + 2, (value >> 16) & 0xFF)
        self.base.write_function_number(function_number + 3, (value >> 24) & 0xFF)

        Logging.logger.info(f"{self.name}: set load value to {value}")

    @CpxBase.require_base
    def configure_debounce_time_for_digital_inputs(
        self, value: DigInDebounceTime | int
    ) -> None:
        """The parameter “Debounce time for digital inputs” defines the total debounce time
        for all digital inputs I0 ... I3

          * 0: 20 us (default)
          * 1: 100 us
          * 2: 3 ms

        :param value: debounce time option. Use DigInDebounceTime from cpx_e_enums or see datasheet
        :type value: DigInDebounceTime | int
        """
        if isinstance(value, DigInDebounceTime):
            value = value.value

        value_range_check(value, 3)

        function_number = 4828 + 64 * self.position + 28
        reg = self.base.read_function_number(function_number)
        value_to_write = (reg & 0xFC) | value
        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: set debounce time to {value}")

    @CpxBase.require_base
    def configure_integration_time_for_speed_measurement(
        self, value: IntegrationTime | int
    ) -> None:
        """The parameter “Integration time for speed measurement” defines the length of the
        measurement cycles for determining the measured value in the “Speed measurement” function

         * 0: 1 ms
         * 1: 10 ms (default)
         * 2: 100 ms

        :param value: integration time. Use IntegrationTime from cpx_e_enums or see datasheet
        :type value: IntegrationTime | int
        """
        if isinstance(value, IntegrationTime):
            value = value.value

        value_range_check(value, 3)

        function_number = 4828 + 64 * self.position + 29
        reg = self.base.read_function_number(function_number)
        value_to_write = (reg & 0xFC) | value
        self.base.write_function_number(function_number, value_to_write)

        Logging.logger.info(f"{self.name}: set debounce time to {value}")
