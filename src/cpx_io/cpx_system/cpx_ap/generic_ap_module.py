"""Generic AP module implementation from APDD"""

import struct
import inspect
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
import cpx_io.cpx_system.cpx_ap.ap_enums as ap_enums
from cpx_io.cpx_system.cpx_ap import ap_registers
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
        self.fieldbus_parameters = None

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        if self.product_category == ProductCategory.IO_LINK:
            self.fieldbus_parameters = self.read_fieldbus_parameters()

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {self.module_type})"

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters

        :return: All AP parameters
        :rtype: dict
        """
        params = super().read_ap_parameter()

        if self.product_category == ProductCategory.IO_LINK:
            io_link_variant = self.base.read_parameter(
                self.position, self.parameters[20090]
            )

            activation_operating_voltage = self.base.read_parameter(
                self.position, self.parameters[20097]
            )

            params.io_link_variant = io_link_variant
            params.operating_supply = activation_operating_voltage
        return params

    @CpxBase.require_base
    def read_channels(self):
        # check if supported
        supported_product_categories = [
            ProductCategory.ANALOG.value,
            ProductCategory.DIGITAL.value,
            ProductCategory.IO_LINK.value,
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

        # IO-Link special read
        if self.product_category == ProductCategory.IO_LINK.value:
            module_input_size = div_ceil(self.information.input_size, 2) - 2

            reg = self.base.read_reg_data(self.input_register, length=module_input_size)

            # 4 channels per module but channel_size should be in bytes while module_input_size
            # is in 16bit registers
            channel_size = (module_input_size) // 4 * 2

            channels = [
                reg[: channel_size * 1],
                reg[channel_size * 1 : channel_size * 2],
                reg[channel_size * 2 : channel_size * 3],
                reg[channel_size * 3 :],
            ]
            Logging.logger.info(f"{self.name}: Reading channels: {channels}")
            return channels

        # All other modules
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
    def read_channel(
        self, channel: int, outputs_only: bool = False, full_size: bool = False
    ) -> bool:
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

        # IO-Link special read
        if self.product_category == ProductCategory.IO_LINK.value:

            if full_size:
                return self.read_channels()[channel]

            return self.read_channels()[channel][
                : self.fieldbus_parameters[channel]["Input data length"]
            ]

        # Other modules:
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
        # IO-Link special (comment)
        # IO-Link does not support multiple channel writes as it seems to be unnessesary

        # Other modules
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
            ProductCategory.IO_LINK.value,
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

        # IO-Link special
        if self.product_category == ProductCategory.IO_LINK.value:
            module_output_size = div_ceil(self.information.output_size, 2)
            channel_size = (module_output_size) // 4

            self.base.write_reg_data(
                value, self.output_register + channel_size * channel
            )
            Logging.logger.info(f"{self.name}: Setting channel {channel} to {value}")
            return

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

        # TODO: this should be self.parameters.get(20021) so it returns None if parameter does not exist
        parameter = self.parameters[20021]

        # TODO: then this can be "if parameter is None:"
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

    @CpxBase.require_base
    def read_pqi(self, channel: int = None) -> dict | list[dict]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels

        :param channel: Channel number, starting with 0, optional
        :type channel: int
        :return: PQI information as dict for one channel or as list of dicts for more channels
        :rtype: dict | list[dict] depending on param channel
        """
        if self.product_category is not ProductCategory.IO_LINK.value:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        data45 = self.base.read_reg_data(self.input_register + 16)[0]
        data67 = self.base.read_reg_data(self.input_register + 17)[0]
        data = [
            data45 & 0xFF,
            (data45 & 0xFF00) >> 8,
            data67 & 0xFF,
            (data67 & 0xFF00) >> 8,
        ]

        channels_pqi = []

        for data_item in data:
            port_qualifier = (
                "input data is valid"
                if (data_item & 0b10000000) >> 7
                else "input data is invalid"
            )
            device_error = (
                "there is at least one error or warning on the device or port"
                if (data_item & 0b01000000) >> 6
                else "there are no errors or warnings on the device or port"
            )
            dev_com = (
                "device is in status PREOPERATE or OPERATE"
                if (data_item & 0b00100000) >> 5
                else "device is not connected or not yet in operation"
            )

            channels_pqi.append(
                {
                    "Port Qualifier": port_qualifier,
                    "Device Error": device_error,
                    "DevCOM": dev_com,
                }
            )
        if channel is None:
            return channels_pqi

        Logging.logger.info(f"{self.name}: Reading PQI of channel(s) {channel}")
        return channels_pqi[channel]

    @CpxBase.require_base
    def configure_target_cycle_time(
        self, value: ap_enums.CycleTime | int, channel: int | list[int] = None
    ) -> None:
        """Target cycle time in ms for the given channels. If no channel is specified,
        target cycle time is applied to all channels.

          *  0: as fast as possible (default)
          * 16: 1.6 ms
          * 32: 3.2 ms
          * 48: 4.8 ms
          * 68: 8.0 ms
          * 73: 10.0 ms
          * 78: 12.0 ms
          * 88: 16.0 ms
          * 98: 20.0 ms
          * 133: 40.0 ms
          * 158: 80.0 ms
          * 183: 120.0 ms

        :param value: target cycle time. Use CycleTime from cpx_ap_enums or see datasheet.
        :type value: CycleTime | int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20049]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "0 ms",
            16: "1.6 ms",
            32: "3.2 ms",
            48: "4.8 ms",
            68: "8.0 ms",
            73: "10.0 ms",
            78: "12.0 ms",
            88: "16.0 ms",
            98: "20.0 ms",
            133: "40.0 ms",
            158: "80.0 ms",
            183: "120.0 ms",
        }

        if isinstance(value, ap_enums.CycleTime):
            value = value.value

        if value not in allowed_values:
            raise ValueError(
                f"Value {value} not valid, must be one of {allowed_values}"
            )

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(
                self.position,
                parameter,
                value,
                channel_item,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} target "
            f"cycle time to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_device_lost_diagnostics(
        self, value: bool, channel: int | list[int] = None
    ) -> None:
        """Activation of diagnostics for IO-Link device lost (default: True) for
        given channel. If no channel is provided, value will be written to all channels.

        :param value: activate (True) or deactivate (False) diagnostics for given channel(s)
        :type value: bool
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20050]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(
                self.position,
                parameter,
                value,
                channel_item,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} device lost diagnostics to {value}"
        )

    @CpxBase.require_base
    def configure_port_mode(
        self, value: ap_enums.PortMode | int, channel: int | list[int] = None
    ) -> None:
        """configure the port mode

          * 0: DEACTIVATED (factory setting)
          * 1: IOL_MANUAL
          * 2: IOL_AUTOSTART
          * 3: DI_CQ
          * 97: PREOPERATE (Only supported in combination with IO-Link V1.1 devices)

        :param value: port mode. Use PortMode from cpx_ap_enums or see datasheet
        :type value: PortMode | int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20071]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if channel is None:
            # TODO: get info from self
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "DEACTIVATED",
            1: "IOL_MANUAL",
            2: "IOL_AUTOSTART",
            3: "DI_CQ",
            97: "PREOPERATE",
        }

        if isinstance(value, ap_enums.PortMode):
            value = value.value

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(self.position, parameter, value, channel_item)

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} port mode to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_review_and_backup(
        self, value: ap_enums.ReviewBackup | int, channel: int | list[int] = None
    ) -> None:
        """Review and backup.

          * 0: no test (factory setting)
          * 1: device compatible V1.0
          * 2: device compatible V1.1
          * 3: device compatible V1.1 Data storage Backup + Restore
          * 4: device compatible V1.1 Data storage Restore
        Changes only become effective when the port mode is changed with "configure_port_mode()".

        :param value: review and backup option (see datasheet)
        :type value: ReviewBackup | int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20072]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if isinstance(value, ap_enums.ReviewBackup):
            value = value.value

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = {
            0: "no test",
            1: "device compatible V1.0",
            2: "device compatible V1.1",
            3: "device compatible V1.1 Data storage Backup + Restore",
            4: "device compatible V1.1 Data storage Restore",
        }

        if value not in allowed_values:
            raise ValueError("Value {value} must be between 0 and 4")

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(
                self.position,
                parameter,
                value,
                channel_item,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} review and backup "
            f"to {allowed_values[value]}"
        )

    @CpxBase.require_base
    def configure_target_vendor_id(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Target Vendor ID
        Changes only become effective when the port mode is changed (ID 20071).

        :param value: target vendor id
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20073]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(
                self.position,
                parameter,
                value,
                channel_item,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} vendor id to {value}"
        )

    @CpxBase.require_base
    def configure_setpoint_device_id(
        self, value: int, channel: int | list[int] = None
    ) -> None:
        """Setpoint device ID
        Changes only become effective when the port mode is changed (ID 20071).

        :param value: setpoint device id
        :type value: int
        :param channel: Channel number, starting with 0 or list of channels e.g. [0, 2], optional
        :type channel: int | list[int]
        """
        parameter = self.parameters[20080]

        if parameter.parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for channel_item in channel:
            self.base.write_parameter(
                self.position,
                parameter,
                value,
                channel_item,
            )

        Logging.logger.info(
            f"{self.name}: Setting channel(s) {channel} device id to {value}"
        )

    @CpxBase.require_base
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels.

        :return: a dict of parameters for every channel.
        :rtype: list[dict]
        """
        if self.product_category is not ProductCategory.IO_LINK.value:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        param_port_status_info = self.parameters[20074]
        param_revision_id = self.parameters[20075]
        param_transmission_rate = self.parameters[20076]
        param_actual_cycle_time = self.parameters[20077]
        param_actual_vendor_id = self.parameters[20078]
        param_actual_device_id = self.parameters[20079]
        param_iolink_input_data_length = self.parameters[20108]
        param_iolink_output_data_length = self.parameters[20109]

        channel_params = []

        port_status_dict = {
            0: "NO_DEVICE",
            1: "DEACTIVATED",
            2: "PORT_DIAG",
            3: "PREOPERATE",
            4: "OPERATE",
            5: "DI_CQ",
            6: "DO_CQ",
            254: "PORT_POWER_OFF",
            255: "NOT_AVAILABLE",
        }
        transmission_rate_dict = {0: "not detected", 1: "COM1", 2: "COM2", 3: "COM3"}

        for channel_item in range(4):
            port_status_information = port_status_dict.get(
                self.base.read_parameter(
                    self.position, param_port_status_info, channel_item
                ),
            )

            revision_id = self.base.read_parameter(
                self.position, param_revision_id, channel_item
            )

            transmission_rate = transmission_rate_dict.get(
                self.base.read_parameter(
                    self.position, param_transmission_rate, channel_item
                ),
            )

            actual_cycle_time = self.base.read_parameter(
                self.position, param_actual_cycle_time, channel_item
            )

            actual_vendor_id = self.base.read_parameter(
                self.position, param_actual_vendor_id, channel_item
            )

            actual_device_id = self.base.read_parameter(
                self.position, param_actual_device_id, channel_item
            )

            input_data_length = self.base.read_parameter(
                self.position, param_iolink_input_data_length, channel_item
            )

            output_data_length = self.base.read_parameter(
                self.position,
                param_iolink_output_data_length,
                channel_item,
            )

            channel_params.append(
                {
                    "Port status information": port_status_information,
                    "Revision ID": revision_id,
                    "Transmission rate": transmission_rate,
                    "Actual cycle time [in 100 us]": actual_cycle_time,
                    "Actual vendor ID": actual_vendor_id,
                    "Actual device ID": actual_device_id,
                    "Input data length": input_data_length,
                    "Output data length": output_data_length,
                }
            )

        Logging.logger.info(
            f"{self.name}: Reading fieldbus parameters for all channels: {channel_params}"
        )
        # update the instance
        self.fieldbus_parameters = channel_params
        return channel_params

    @CpxBase.require_base
    def read_isdu(self, channel: int, index: int, subindex: int) -> bytes:
        """Read isdu (device parameter) from defined channel
        Raises CpxRequestError when read failed

        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        :return: device parameter (index/subindex) for given channel
        :rtype: bytes
        """
        module_index = (self.position + 1).to_bytes(2, "little")
        channel = (channel + 1).to_bytes(2, "little")
        index = index.to_bytes(2, "little")
        subindex = subindex.to_bytes(2, "little")
        length = (0).to_bytes(2, "little")  # always zero when reading
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = (100).to_bytes(2, "little")

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, ap_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(channel, ap_registers.ISDU_CHANNEL.register_address)
        # select index
        self.base.write_reg_data(index, ap_registers.ISDU_INDEX.register_address)
        # select subindex
        self.base.write_reg_data(subindex, ap_registers.ISDU_SUBINDEX.register_address)
        # select length of data in bytes
        self.base.write_reg_data(length, ap_registers.ISDU_LENGTH.register_address)
        # command
        self.base.write_reg_data(command, ap_registers.ISDU_COMMAND.register_address)

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 5000:
            stat = int.from_bytes(
                self.base.read_reg_data(*ap_registers.ISDU_STATUS),
                byteorder="little",
            )

            cnt += 1
        if cnt >= 5000:
            raise CpxRequestError("ISDU data read failed")

        ret = self.base.read_reg_data(*ap_registers.ISDU_DATA)
        Logging.logger.info(f"{self.name}: Reading ISDU for channel {channel}: {ret}")

        return ret

    @CpxBase.require_base
    def write_isdu(self, data: bytes, channel: int, index: int, subindex: int) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed

        :param data: Data as 16bit register values in list
        :type data: list[int]
        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        """
        module_index = (self.position + 1).to_bytes(2, "little")
        channel = (channel + 1).to_bytes(2, "little")
        index = (index).to_bytes(2, "little")
        subindex = (subindex).to_bytes(2, "little")
        length = (len(data) * 2).to_bytes(2, "little")
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = (101).to_bytes(2, "little")

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, ap_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(channel, ap_registers.ISDU_CHANNEL.register_address)
        # select index
        self.base.write_reg_data(index, ap_registers.ISDU_INDEX.register_address)
        # select subindex
        self.base.write_reg_data(subindex, ap_registers.ISDU_SUBINDEX.register_address)
        # select length of data in bytes
        self.base.write_reg_data(length, ap_registers.ISDU_LENGTH.register_address)
        # write data to data register
        self.base.write_reg_data(data, ap_registers.ISDU_DATA.register_address)
        # command
        self.base.write_reg_data(command, ap_registers.ISDU_COMMAND.register_address)

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 1000:
            stat = int.from_bytes(
                self.base.read_reg_data(*ap_registers.ISDU_STATUS),
                byteorder="little",
            )
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data write failed")

        Logging.logger.info(
            f"{self.name}: Write ISDU {data} to channel {channel} ({index},{subindex})"
        )
