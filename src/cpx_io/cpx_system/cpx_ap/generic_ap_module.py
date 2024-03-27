"""Generic AP module implementation from APDD"""

import struct
import inspect
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap
import cpx_io.cpx_system.cpx_ap.cpx_ap_enums as ap_enums
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import div_ceil, channel_range_check, value_range_check
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


class GenericApModule(CpxApModule):

    def __init__(
        self,
        name,
        module_type,
        product_category,
        input_channels,
        output_channels,
        supported_parameter_ids,
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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

    # TODO: This is very unique for xDIxDO modules with the output numbering. Maybe this needs to be omitted
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
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

    @CpxBase.require_base
    def configure_channel_range(
        self, channel: int, value: ap_enums.ChannelRange | int
    ) -> None:
        """set the signal range and type of one channel

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel range. Use ChannelRange from cpx_ap_enums or see datasheet.
        :type value: ChannelRange | int
        """

        parameter_id = ParameterNameMap()["ChannelInputMode"].parameter_id

        if parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        channel_range_check(channel, len(self.input_channels))

        if isinstance(value, ap_enums.ChannelRange):
            value = value.value

        value_range_check(value, 10)

        self.base.write_parameter(
            self.position,
            ParameterNameMap()["ChannelInputMode"],
            value,
            channel,
        )

        Logging.logger.info(f"{self.name}: Setting channel {channel} range to {value}")

    @CpxBase.require_base
    def configure_linear_scaling(self, channel: int, value: bool) -> None:
        """Set linear scaling (Factory setting "False")

        :param channel: Channel number, starting with 0
        :type channel: int
        :param value: Channel linear scaling activated (True) or deactivated (False)
        :type value: bool
        """
        # check if supported
        parameter_id = ParameterNameMap()["ChannelInputMode"].parameter_id

        if parameter_id not in self.supported_parameter_ids:
            raise NotImplementedError(
                f"{self} has no function <{inspect.currentframe().f_code.co_name}>"
            )

        if not isinstance(value, bool):
            raise TypeError(f"State {value} must be of type bool (True or False)")

        channel_range_check(channel, 4)

        self.base.write_parameter(
            self.position,
            ParameterNameMap()["LinearScalingEnable"],
            int(value),
            channel,
        )

        Logging.logger.info(
            f"{self.name}: Setting channel {channel} linear scaling to {value}"
        )
