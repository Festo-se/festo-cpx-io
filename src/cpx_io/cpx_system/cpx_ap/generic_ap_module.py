"""Generic AP module implementation from APDD"""

import struct
import inspect
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
import cpx_io.cpx_system.cpx_ap.cpx_ap_enums as ap_enums
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import (
    div_ceil,
    channel_range_check,
    value_range_check,
    convert_uint32_to_octett,
    convert_to_mac_string,
)
from cpx_io.utils.logging import Logging


@dataclass
class Channel:
    """Channel dataclass"""

    bits: int
    channel_id: int
    data_type: str
    description: str
    direction: str
    name: str
    profile_list: list


@dataclass
class ChannelGroup:
    """ChannelGroup dataclass"""

    channel_group_id: int
    channels: dict
    name: str
    parameter_group_ids: list


class ChannelGroupBuilder:
    """ChannelGroupBuilder"""

    def build_channel_group(self, channel_group_dict):
        return ChannelGroup(
            channel_group_dict.get("ChannelGroupId"),
            channel_group_dict.get("Channels"),
            channel_group_dict.get("Name"),
            channel_group_dict.get("ParameterGroupIds"),
        )


class ChannelBuilder:
    """ChannelBuilder"""

    def build_channel(self, channel_dict):
        return Channel(
            channel_dict.get("Bits"),
            channel_dict.get("ChannelId"),
            channel_dict.get("DataType"),
            channel_dict.get("Description"),
            channel_dict.get("Direction"),
            channel_dict.get("Name"),
            channel_dict.get("ProfileList"),
        )


@dataclass
class SystemParameters:
    """SystemParameters"""

    # pylint: disable=too-many-instance-attributes
    dhcp_enable: bool = None
    ip_address: str = None
    subnet_mask: str = None
    gateway_address: str = None
    active_ip_address: str = None
    active_subnet_mask: str = None
    active_gateway_address: str = None
    mac_address: str = None
    setup_monitoring_load_supply: int = None


class GenericApModule(CpxApModule):

    def __init__(
        self,
        name,
        module_type,
        product_category,
        input_channels,
        output_channels,
        supported_parameter_ids,
        parameters,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.module_type = module_type
        self.product_category = product_category
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.supported_parameter_ids = supported_parameter_ids
        self.parameters = parameters

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {self.module_type})"

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_channels(self):
        # check if supported
        supported_product_categories = [
            ProductCategory.ANALOG.value,
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )

        # if available, read inputs
        values = []
        if self.input_channels:
            data = self.base.read_reg_data(
                self.input_register, length=div_ceil(self.information.input_size, 2)
            )
            if all(c.data_type == "BOOL" for c in self.input_channels):
                values.extend(bytes_to_boollist(data)[: len(self.input_channels)])
            elif all(c.data_type == "INT16" for c in self.input_channels):
                values.extend(struct.unpack("<" + "h" * (len(data) // 2), data))
            else:
                raise NotImplementedError(
                    f"Input data type {self.input_channels[0].data_type} are not supported or "
                    "types are not the same for each channel"
                )

        # if available, read outputs
        if self.output_channels:
            data = self.base.read_reg_data(
                self.output_register, length=div_ceil(self.information.output_size, 2)
            )
            if all(c.data_type == "BOOL" for c in self.output_channels):
                values.extend(bytes_to_boollist(data)[: len(self.output_channels)])
            else:
                raise NotImplementedError(
                    f"Output data type {self.output_channels[0].data_type} are not supported or "
                    "types are not the same for each channel"
                )

        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

    @CpxBase.require_base
    def read_channel(self, channel: int, outputs_only=False) -> bool:
        """read back the value of one channel
        For mixed IN/OUTput modules the optional parameter 'outputs_only' defines
        if the outputs are numbered WITH (after) the inputs ("False", default), so the range
        of output channels is <number of input channels>..<number of input and output channels>
        If "True", the outputs are numbered from 0..<number of output channels>, the inputs
        cannot be accessed this way.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param outputs_only: Outputs should be numbered independend from inputs, optional
        :type outputs_only: bool
        :return: Value of the channel
        :rtype: bool
        """
        if self.input_channels and outputs_only:
            channel += len(self.input_channels)

        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list) -> None:
        """write all channels with a list of values

        :param data: list of values for each output channel
        :type data: list
        """
        # check if supported
        supported_product_categories = [
            ProductCategory.ANALOG.value,
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )

        if self.output_channels:
            if len(data) != len(self.output_channels):
                raise ValueError(
                    f"Data must be list of {len(self.output_channels)} elements"
                )

            if all(c.data_type == "BOOL" for c in self.output_channels) and all(
                isinstance(d, bool) for d in data
            ):
                reg = boollist_to_bytes(data)
            else:
                raise NotImplementedError(
                    f"Output data type {self.output_channels[0].data_type} are not supported or "
                    "types are not the same for each channel"
                )

            self.base.write_reg_data(reg, self.output_register)
            Logging.logger.info(f"{self.name}: Setting channels to {data}")

        else:
            raise NotImplementedError(
                f"Module {self.information.order_text} at index {self.position} "
                "has no outputs to write to"
            )

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool | int | bytes) -> None:
        """set one channel value

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: bool
        """
        # check if supported
        supported_product_categories = [
            ProductCategory.ANALOG.value,
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )

        if self.output_channels:
            channel_range_check(channel, len(self.output_channels))

            if all(c.data_type == "BOOL" for c in self.output_channels) and isinstance(
                value, bool
            ):
                data = bytes_to_boollist(self.base.read_reg_data(self.output_register))
                data[channel] = value
                reg = boollist_to_bytes(data)
                self.base.write_reg_data(reg, self.output_register)

            else:
                raise NotImplementedError(
                    f"{self.output_channels.data_type} is not supported or type(value) "
                    f"is not compatible"
                )
            Logging.logger.info(f"{self.name}: Setting channel {channel} to {value}")

        else:
            raise NotImplementedError(
                f"Module {self.information.ordercode} has no outputs to write to"
            )

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        # check if supported
        supported_product_categories = [
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )

        if self.output_channels:
            if self.output_channels[channel].data_type == "BOOL":
                self.write_channel(channel, True)
            else:
                raise TypeError(
                    f"{self} has has incompatible datatype "
                    f"{self.output_channels[channel].data_type} (should be 'BOOL')"
                )

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        # check if supported
        supported_product_categories = [
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )

        if self.output_channels:
            if self.output_channels[channel].data_type == "BOOL":
                self.write_channel(channel, False)
            else:
                raise TypeError(
                    f"{self} has has incompatible datatype "
                    f"{self.output_channels[channel].data_type} (should be 'BOOL')"
                )

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        # check if supported
        supported_product_categories = [
            ProductCategory.DIGITAL.value,
            ProductCategory.MPA_L.value,
            ProductCategory.MPA_S.value,
            ProductCategory.VTSA.value,
            ProductCategory.VTUG.value,
            ProductCategory.VTUX.value,
            ProductCategory.VTOM.value,
        ]
        if self.product_category not in supported_product_categories:
            raise NotImplementedError(
                f"{self} has no function " f"<{inspect.currentframe().f_code.co_name}>"
            )
        if self.output_channels:
            if self.output_channels[channel].data_type == "BOOL":
                # get the relevant value from the register and write the inverse
                value = self.read_channel(channel)
                self.write_channel(channel, not value)
            else:
                raise TypeError(
                    f"{self} has has incompatible datatype "
                    f"{self.output_channels[channel].data_type} (should be 'BOOL')"
                )

    # TODO: Maybe better to rename the configure functions to the actual parameter name
    # because there might be similar functions for different modules that will be
    # difficult to differentiate

    # TODO: Delete all the parametermap stuff and data folder ...

    @CpxBase.require_base
    def configure_channel_temp_unit(
        self, channel: int, value: ap_enums.TempUnit | int
    ) -> None:
        """set the channel temperature unit.
          * 0: Celsius (default)
          * 1: Farenheit
          * 2: Kelvin

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel unit. Use TempUnit from cpx_ap_enums or see datasheet.
        :type value: TempUnit | int
        """
        parameter = self.parameters[20032]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        if isinstance(value, ap_enums.TempUnit):
            value = value.value

        value_range_check(value, 3)

        self.base.write_parameter(
            self.position,
            parameter,
            value,
            channel,
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} temperature unit to {value}"
        )

    @CpxBase.require_base
    def configure_channel_range(
        self, channel: int, value: ap_enums.ChannelRange | int
    ) -> None:
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
        parameter = self.parameters[20043]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        if isinstance(value, ap_enums.ChannelRange):
            value = value.value

        value_range_check(value, 10)

        self.base.write_parameter(
            self.position,
            parameter,
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
        parameter_upper = self.parameters[20044]
        parameter_lower = self.parameters[20045]

        if any(
            p not in self.supported_parameter_ids
            for p in [parameter_upper.parameter_id, parameter_lower.parameter_id]
        ):
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        self.configure_linear_scaling(channel, True)
        # TODO: Add min/max limits from parameter instead of hardcoding
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
                self.position,
                parameter_upper,
                upper,
                channel,
            )
        elif upper is None and isinstance(lower, int):
            self.base.write_parameter(
                self.position,
                parameter_lower,
                lower,
                channel,
            )
        elif isinstance(upper, int) and isinstance(lower, int):
            self.base.write_parameter(
                self.position,
                parameter_upper,
                upper,
                channel,
            )
            self.base.write_parameter(
                self.position,
                parameter_lower,
                lower,
                channel,
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
        parameter = self.parameters[20046]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        value_range_check(value, 65536)

        self.base.write_parameter(
            self.position,
            parameter,
            value,
            channel,
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
        parameter = self.parameters[20107]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        value_range_check(value, 16)

        self.base.write_parameter(
            self.position,
            parameter,
            value,
            channel,
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
        parameter = self.parameters[20111]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if not isinstance(value, bool):
            raise TypeError(f"State {value} must be of type bool (True or False)")

        channel_range_check(channel, len(self.input_channels))

        self.base.write_parameter(
            self.position,
            parameter,
            value,
            channel,
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} linear scaling to {value}"
        )

    @CpxBase.require_base
    def configure_debounce_time(self, value: ap_enums.DebounceTime | int) -> None:
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
        parameter = self.parameters[20014]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if isinstance(value, ap_enums.DebounceTime):
            value = value.value

        value_range_check(value, len(self.input_channels))

        self.base.write_parameter(
            self.position,
            parameter,
            value,
        )

        Logging.logger.info(f"{self.name}: Setting debounce time to {value}")

    @CpxBase.require_base
    def configure_monitoring_load_supply(
        self, value: ap_enums.LoadSupply | int
    ) -> None:
        """Configures the monitoring load supply for all channels.

          * 0: Load supply monitoring inactive
          * 1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
          * 2: Load supply monitoring active

        :param value: Monitoring load supply for all channels. Use LoadSupply from cpx_ap_enums
        or see datasheet.
        :type value: LoadSupply | int
        """
        parameter = self.parameters[20022]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if isinstance(value, ap_enums.LoadSupply):
            value = value.value

        value_range_check(value, 3)

        self.base.write_parameter(
            self.position,
            parameter,
            value,
        )

        Logging.logger.info(f"{self.name}: Setting Load supply monitoring to {value}")

    @CpxBase.require_base
    def configure_behaviour_in_fail_state(
        self, value: ap_enums.FailState | int
    ) -> None:
        """Configures the behaviour in fail state for all channels.

          * 0: Reset Outputs (default)
          * 1: Hold last state

        :param value: Setting for behaviour in fail state for all channels. Use FailState
        from cpx_ap_enums or see datasheet.
        :type value: FailState | int
        """
        parameter = self.parameters[20052]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if isinstance(value, ap_enums.FailState):
            value = value.value

        value_range_check(value, 2)

        self.base.write_parameter(
            self.position,
            parameter,
            value,
        )

        Logging.logger.info(f"{self.name}: Setting fail state behaviour to {value}")

    @CpxBase.require_base
    def read_system_parameters(self) -> SystemParameters:
        """Read parameters from EP module

        :return: Parameters object containing all r/w parameters
        :rtype: Parameters
        """
        params = SystemParameters(
            dhcp_enable=self.base.read_parameter(self.position, self.parameters[12000]),
            ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12001])
            ),
            subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12002]),
            ),
            gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12003])
            ),
            active_ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12004])
            ),
            active_subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12005])
            ),
            active_gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameters[12006])
            ),
            mac_address=convert_to_mac_string(
                self.base.read_parameter(self.position, self.parameters[12007])
            ),
            setup_monitoring_load_supply=self.base.read_parameter(
                self.position, self.parameters[20022]
            )
            & 0xFF,
        )
        Logging.logger.info(f"{self.name}: Reading parameters: {params}")
        return params

    @CpxBase.require_base
    def configure_diagnosis_for_defect_valve(self, value: bool) -> None:
        """Enable (True, default) or disable (False) diagnosis for defect valve.

        :param value: Value to write to the module (True to enable diagnosis)
        :type value: bool
        """
        parameter = self.parameters[20021]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        self.base.write_parameter(
            self.position,
            parameter,
            value,
        )

        Logging.logger.info(
            f"{self.name}: Setting diagnosis for defect valve to {value}"
        )
