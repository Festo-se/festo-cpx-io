"""Generic AP module implementation from APDD"""

import struct
import copy
import inspect
import time
from typing import Any, Union
from collections import namedtuple
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_supported_datatypes import (
    SUPPORTED_IOL_DATATYPES,
    SUPPORTED_ISDU_DATATYPES,
)
from cpx_io.cpx_system.cpx_ap.ap_supported_functions import (
    DIAGNOSIS_FUNCTIONS,
    INPUT_FUNCTIONS,
    OUTPUT_FUNCTIONS,
    PARAMETER_FUNCTIONS,
    SUPPORTED_PRODUCT_FUNCTIONS_DICT,
)
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import Channel
from cpx_io.cpx_system.cpx_ap.dataclasses.module_diagnosis import ModuleDiagnosis
from cpx_io.cpx_system.cpx_ap.dataclasses.system_parameters import SystemParameters
from cpx_io.cpx_system.cpx_ap.dataclasses.channels import Channels
from cpx_io.cpx_system.cpx_ap import ap_modbus_registers
from cpx_io.utils.helpers import (
    div_ceil,
    channel_range_check,
    instance_range_check,
    convert_uint32_to_octett,
    convert_to_mac_string,
)
from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation


class ApModule(CpxModule):
    """Generic AP module class. This includes all functions that are shared
    among the modules. To get an overview of your system and the supported
    functions of the individual modules, see the system documentation of the
    CpxAp object"""

    # pylint: disable=too-many-public-methods, too-many-lines, too-many-instance-attributes
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    # intended. Module offers many functions for user comfort

    def __init__(
        self,
        apdd_information: ApddInformation,
        channels: tuple,
        parameter_list: list,
        diagnosis_list: list,
        variant_list: list,
        variant_switch_parameter: int | None,
    ):
        super().__init__(name=apdd_information.name)
        self.information = None
        self.name = apdd_information.name
        self.apdd_information = apdd_information
        self.variant_list = variant_list
        self.variant_switch_parameter = variant_switch_parameter

        self.channels = Channels(
            inputs=channels[0] + channels[2],
            outputs=channels[1] + channels[2],
            inouts=channels[2],
        )
        if len(self.channels.outputs) > 0:
            biggest_byte_offset_channel = max(
                self.channels.outputs, key=lambda x: x.bit_offset
            )
            self.output_byte_size = div_ceil(
                biggest_byte_offset_channel.bit_offset
                + biggest_byte_offset_channel.bits,
                8,
            )
            if self.output_byte_size % 2 == 1:
                self.output_byte_size += 1
        ModuleDicts = namedtuple("ModuleDicts", ["parameters", "diagnosis"])
        self.module_dicts = ModuleDicts(
            parameters={p.parameter_id: p for p in parameter_list},
            diagnosis={
                int(d.diagnosis_id.lstrip("0x"), base=16): d for d in diagnosis_list
            },
        )

        self.fieldbus_parameters = None

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {self.apdd_information.module_type})"

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    @staticmethod
    def _check_instances(parameter, instances) -> list:
        """Check if instances are correct and return corrected instances or raise Error."""

        start = parameter.parameter_instances.get("FirstIndex")
        end = parameter.parameter_instances.get("NumberOfInstances")

        # instance defined by one integer
        if isinstance(instances, int):
            instance_range_check(instances, start, end)
            return [instances]

        # instances defined by list
        if isinstance(instances, list):
            for i in instances:
                instance_range_check(i, start, end)
            return instances

        # instances not defined but start/end is valid
        if not instances and isinstance(start, int) and isinstance(end, int):
            return list(range(start, end))

        # instances not defined and no information returns default instance 0
        return [0]

    def is_function_supported(self, func_name):
        """Returns False if function is not supported"""

        function_is_supported = True
        # check if function is known at all
        if not SUPPORTED_PRODUCT_FUNCTIONS_DICT.get(func_name):
            function_is_supported = False

        # check if function is supported for the product category
        elif self.apdd_information.product_category not in [
            v.value for v in SUPPORTED_PRODUCT_FUNCTIONS_DICT.get(func_name)
        ]:
            function_is_supported = False

        # check if outputs are available if it's an output function
        elif func_name in OUTPUT_FUNCTIONS and not self.channels.outputs:
            function_is_supported = False

        # check if inputs or outputs are available if it's an input function
        elif func_name in INPUT_FUNCTIONS and not (
            self.channels.inputs or self.channels.outputs
        ):
            function_is_supported = False

        # check if there are parameters if it's a parameter function
        elif func_name in PARAMETER_FUNCTIONS and not self.module_dicts.parameters:
            function_is_supported = False

        # check if there are diagnosis information if it's a diagnosis function
        elif func_name in DIAGNOSIS_FUNCTIONS and not self.module_dicts.diagnosis:
            function_is_supported = False

        return function_is_supported

    def _check_function_supported(self, func_name):
        if not self.is_function_supported(func_name):
            raise NotImplementedError(f"{self} has no function <{func_name}>")

    def _configure(self, base: CpxBase, position: int) -> None:
        """This function is used by CpxBase to setup the system."""
        super()._configure(base=base, position=position)

        self.system_entry_registers.diagnosis = self.base.next_diagnosis_register

        self.base.next_output_register += div_ceil(self.information.output_size, 2)
        self.base.next_input_register += div_ceil(self.information.input_size, 2)
        self.base.next_diagnosis_register += 6  # always 6 registers per module

        # IO-Link special parameter
        if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
            self.fieldbus_parameters = self.read_fieldbus_parameters()

    @staticmethod
    def _convert_datum_to_bytes(channel: Channel, datum) -> bytes:
        """Convert a datum of a single channel (e.g. in a case of an array) into bytes"""
        if channel.byte_swap_needed:
            byteorder = "little"
        else:
            byteorder = "big"
        if channel.data_type == "BOOL":
            return (int(datum) << (channel.bit_offset % 8)).to_bytes(
                1, byteorder=byteorder
            )
        if channel.data_type == "INT8":
            return datum.to_bytes(1, byteorder=byteorder, signed=True)
        if channel.data_type == "UINT8":
            return datum.to_bytes(1, byteorder=byteorder)
        if channel.data_type == "INT16":
            return datum.to_bytes(2, byteorder=byteorder, signed=True)
        if channel.data_type == "UINT16":
            return datum.to_bytes(2, byteorder=byteorder)
        raise NotImplementedError(
            f"Output data type {channel.data_type} is not implemented"
        )

    @staticmethod
    def _convert_channel_data_to_bytes(channel: Channel, new_data, prev_data) -> None:
        """Convert the new_data with the given channel information to a byte(s)
        and insert them into the prev_data at the given channel bit_offset position
        """
        current_offset = channel.bit_offset
        start_index = current_offset // 8
        if channel.array_size:
            current_channel = copy.deepcopy(channel)
            for i in range(channel.array_size):
                start_index = (
                    current_offset + i * (channel.bits // channel.array_size)
                ) // 8
                current_channel.bit_offset = channel.bit_offset + i * (
                    channel.bits // channel.array_size
                )
                values = ApModule._convert_datum_to_bytes(current_channel, new_data[i])
                if channel.data_type == "BOOL":
                    # mask out bit for bools only
                    prev_data[start_index] = values[0] | (
                        prev_data[start_index] & ~(1 << current_channel.bit_offset)
                    )
                else:
                    for offset, val in enumerate(values):
                        prev_data[start_index + offset] = val
        else:
            if isinstance(new_data, (list, tuple, dict)):
                raise TypeError(
                    f"Type {type(new_data)} is not supported for channel type {channel.data_type}"
                )
            values = ApModule._convert_datum_to_bytes(channel, new_data)
            if channel.data_type == "BOOL":
                # mask out bit for bools only
                prev_data[start_index] = values[0] | (
                    prev_data[start_index] & ~(1 << (channel.bit_offset % 8))
                )
            else:
                for offset, val in enumerate(values):
                    prev_data[start_index + offset] = val

    @staticmethod
    def _extract_channel_datum_from_bytes(channel: Channel, reg_data: bytes) -> Any:
        """Interpret a single value for a given channel in the given bytes"""
        if channel.data_type == "BOOL":
            return (reg_data[0] >> (channel.bit_offset % 8)) & 1 == 1
        byteorder = "<" if channel.byte_swap_needed else ">"
        if channel.data_type == "INT8":
            decode_string = byteorder + "b"
        elif channel.data_type == "UINT8":
            decode_string = byteorder + "B"
        elif channel.data_type == "INT16":
            decode_string = byteorder + "h"
        elif channel.data_type == "UINT16":
            decode_string = byteorder + "H"
        else:
            raise NotImplementedError(f"Data type {channel.data_type} is not supported")
        return struct.unpack(decode_string, reg_data)[0]

    @staticmethod
    def _extract_channel_list_data_from_bytes(
        channel_description: list[Channel], reg_data: bytes
    ) -> list:
        """Interpret the bytes as the channels in the channel_description"""
        result = []
        for channel in channel_description:
            if channel.data_type not in ("BOOL", "UINT8", "INT8", "UINT16", "INT16"):
                raise NotImplementedError(
                    f"Data type {channel.data_type} is not implemented"
                )
            pos = channel.bit_offset // 8
            if channel.data_type in ("UINT8", "INT8", "BOOL"):
                entry_size = 1
            else:
                assert channel.data_type in ("UINT16", "INT16")
                entry_size = 2
            if channel.array_size:
                array = []
                cloned_channel = copy.deepcopy(channel)
                for i in range(0, channel.array_size):
                    if channel.data_type == "BOOL":
                        # in an array the channel bit offset stays constant
                        cloned_channel.bit_offset = channel.bit_offset + i
                        pos = cloned_channel.bit_offset // 8
                        array.append(
                            ApModule._extract_channel_datum_from_bytes(
                                cloned_channel, reg_data[pos : pos + entry_size]
                            )
                        )
                    else:
                        array.append(
                            ApModule._extract_channel_datum_from_bytes(
                                channel,
                                reg_data[
                                    pos + i * entry_size : pos + (i + 1) * entry_size
                                ],
                            )
                        )
                result.append(array)
            else:
                result.append(
                    ApModule._extract_channel_datum_from_bytes(
                        channel, reg_data[pos : pos + entry_size]
                    )
                )
        return result

    @CpxBase.require_base
    def read_output_channels(self) -> list:
        """Read only output channels from module and interpret them as the module intends.

        For mixed IN/OUTput modules the outputs are numbered from 0..<number of output channels>,
        the inputs cannot be accessed this way.

        :return: List of values of the channels
        :rtype: list
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        byte_output_size = div_ceil(self.information.output_size, 2)
        values = []

        if self.channels.outputs:
            data = self.base.read_reg_data(
                self.system_entry_registers.outputs, byte_output_size
            )

            values = ApModule._extract_channel_list_data_from_bytes(
                self.channels.outputs, data
            )

        Logging.logger.info(f"{self.name}: Reading output channels: {values}")
        return values

    @CpxBase.require_base
    def read_channels(self) -> list:
        """Read all channels from module and interpret them as the module intends.

        :return: List of values of the channels
        :rtype: list
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        byte_input_size = div_ceil(self.information.input_size, 2)
        values = []

        if self.channels.inputs:
            data = self.base.read_reg_data(
                self.system_entry_registers.inputs, byte_input_size
            )

            if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
                # IO-Link splits into byte_channel_size chunks. Assumes all channels are the same
                byte_channel_size = self.channels.inouts[0].array_size
                # for IO-Link only the channels.inouts are relevant, cut to the correct size
                data = data[: len(self.channels.inouts * byte_channel_size)]

                channels = [
                    data[i : i + byte_channel_size]
                    for i in range(0, len(data), byte_channel_size)
                ]

                # cut to actual IO-Link device size if available
                channel_data = [
                    (
                        (c[: self.fieldbus_parameters[i]["Input data length"]])
                        if self.fieldbus_parameters[i]["Input data length"] > 0
                        else None
                    )
                    for i, c in enumerate(channels)
                ]

                Logging.logger.info(
                    f"{self.name}: Reading IO-Link channels: {channel_data}"
                )
                return channel_data

            values = ApModule._extract_channel_list_data_from_bytes(
                self.channels.inputs, data
            )

        Logging.logger.info(f"{self.name}: Reading input channels: {values}")

        if self.channels.outputs:
            values += self.read_output_channels()
        return values

    @CpxBase.require_base
    def read_output_channel(self, channel: int) -> Any:
        """Read back the value of one output channel.

        For mixed IN/OUTput modules the outputs are numbered from 0..<number of output channels>,
        the inputs cannot be accessed this way.

        :param channel: Channel number, starting with 0
        :type channel: int
        :return: Value of the channel
        :rtype: bool
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        channel_range_check(channel, len(self.channels.outputs))
        return self.read_output_channels()[channel]

    @CpxBase.require_base
    def read_channel(self, channel: int) -> Any:
        """Read back the value of one channel.

        :param channel: Channel number, starting with 0
        :type channel: int
        :return: Value of the channel
        :rtype: bool
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        channel_count = (
            len([c for c in self.channels.inputs if c.direction == "in"])
            + len([c for c in self.channels.outputs if c.direction == "out"])
            + len(self.channels.inouts)
        )

        channel_range_check(channel, channel_count)

        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[Any]) -> None:
        """Write all channels with a list of values. Length of the list must fit the output
        size of the module. Get the size first by reading the channels and using len().

        :param data: list of values for each output channel. The type of the list elements must
            fit to the module type
        :type data: list
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        if len(data) != len(self.channels.outputs):
            raise ValueError(
                f"Data must be list of {len(self.channels.outputs)} elements"
            )

        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
            self.__handle_io_link_on_write_channels(data)
        else:
            prev_data = bytearray(self.output_byte_size)
            for idx, channel in enumerate(self.channels.outputs):
                ApModule._convert_channel_data_to_bytes(channel, data[idx], prev_data)
            self.base.write_reg_data(prev_data, self.system_entry_registers.outputs)

    def __handle_io_link_on_write_channels(self, data):
        """Handles a write_channels of a list with bytes"""

        if not all(isinstance(d, bytes) for d in data):
            raise TypeError(f"{self.name}: datatype for IO-Link channels must be bytes")

        byte_channel_size = self.channels.inouts[0].array_size
        if any(len(d) != byte_channel_size for d in data):
            raise ValueError(
                f"Your current IO-Link datalength {byte_channel_size} does "
                f"not match the provided bytes length."
            )

        all_register_data = b"".join(data)
        self.base.write_reg_data(all_register_data, self.system_entry_registers.outputs)
        Logging.logger.info(f"{self.name}: Setting IO-LINK channels to {data}")

    @CpxBase.require_base
    def write_channel(self, channel: int, value: Any) -> None:
        """Set one channel value. Value must be the correct type, typecheck is done by the function
        Get the correct type by reading out the channel first and using type() on the value.

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: Any
        """
        # pylint: disable=too-many-branches
        # intentional, lots of checks are done to guide the user
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        channel_range_check(channel, len(self.channels.outputs))

        # IO-Link special
        if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
            if not all(
                c.data_type in SUPPORTED_IOL_DATATYPES
                for c in self.channels.inputs
                + self.channels.outputs
                + self.channels.inouts
            ):
                raise TypeError("Datatypes are not supported for IO-Link modules")

            byte_channel_size = self.channels.inouts[0].array_size

            if len(value) != byte_channel_size:
                Logging.logger.info(
                    f"Length of value {value} does not match master channel size"
                    f" of {byte_channel_size} bytes. Shorter values must be padded left!"
                )

            # add missing bytes for full modbus register
            if len(value) % 2:
                value += b"\x00"
            # add missing bytes for full master length
            if len(value) < byte_channel_size:
                value += b"\x00" * (byte_channel_size - len(value))

            self.base.write_reg_data(
                value,
                self.system_entry_registers.outputs + byte_channel_size // 2 * channel,
            )
            Logging.logger.info(
                f"{self.name}: Setting IO-Link channel {channel} to {value}"
            )
        else:
            output_index = self.channels.outputs[channel].bit_offset // 16
            # add one to the size if the output_index was rounded down
            size = (
                div_ceil(
                    self.channels.outputs[channel].bit_offset
                    + self.channels.outputs[channel].bits,
                    16,
                )
                * 2
            ) - output_index * 2
            prev_data = bytearray(self.output_byte_size)
            old_data = self.base.read_reg_data(
                self.system_entry_registers.outputs + output_index, size
            )
            for i in range(size):
                prev_data[i + output_index] = old_data[i]
            ApModule._convert_channel_data_to_bytes(
                self.channels.outputs[channel], value, prev_data
            )
            # only write necessary register
            self.base.write_reg_data(
                prev_data[output_index * 2 : output_index * 2 + size],
                self.system_entry_registers.outputs + output_index,
            )

    # Special functions for digital channels
    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """Set one channel to logic high level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        ch = self.channels.outputs[channel]
        if getattr(ch, "data_type", None) != "BOOL":
            raise NotImplementedError(
                f"set_channel is only supported for BOOL channels, but channel {channel} is "
                f"{ch.data_type}"
            )
        self.write_channel(channel, True)

    @CpxBase.require_base
    def reset_channel(self, channel: int) -> None:
        """Set one channel to logic low level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        ch = self.channels.outputs[channel]
        if getattr(ch, "data_type", None) != "BOOL":
            raise NotImplementedError(
                f"reset_channel is only supported for BOOL channels, but channel {channel} is "
                f"{ch.data_type}"
            )
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """Set one channel the inverted of current logic level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        ch = self.channels.outputs[channel]
        if getattr(ch, "data_type", None) != "BOOL":
            raise NotImplementedError(
                f"toggle_channel is only supported for BOOL channels, but channel {channel} is "
                f"{ch.data_type}"
            )
        value = self.read_output_channel(channel)
        self.write_channel(channel, not value)

    @CpxBase.require_base
    def write_module_parameter(
        self,
        parameter: Union[str, int],
        value: Union[int, bool, str],
        instances: Union[int, list] = None,
    ) -> None:
        """Write module parameter if available.

        :param parameter: Parameter name or ID
        :type parameter: str | int
        :param value: Value to write to the parameter, type depending on parameter
        :type value: int | bool | str
        :param instances: (optional) Index or list of instances of the parameter.
            If None, all instances will be written
        :type instance: int | list"""

        self._check_function_supported(inspect.currentframe().f_code.co_name)
        parameter_input = parameter
        # PARAMETER HANDLING
        if isinstance(parameter, int):
            parameter = self.module_dicts.parameters.get(parameter)
        elif isinstance(parameter, str):
            parameter_list = [
                p for p in self.module_dicts.parameters.values() if p.name == parameter
            ]
            parameter = parameter_list[0] if len(parameter_list) == 1 else None

        if parameter is None:
            raise NotImplementedError(f"{self} has no parameter {parameter_input}")

        if not parameter.is_writable:
            raise AttributeError(f"Parameter {parameter} is not writable")

        # INSTANCE HANDLING
        instances = self._check_instances(parameter, instances)

        # VALUE HANDLING
        if isinstance(value, str) and parameter.enums:
            value_str = value
            value = parameter.enums.enum_values.get(value)
            # overwrite the parameter datatype from enum
            parameter.data_type = parameter.enums.data_type

            if value is None:
                raise TypeError(
                    f"'{value_str}' is not supported for '{parameter.name}'. "
                    f"Valid strings are: {list(parameter.enums.enum_values.keys())}"
                )

        if isinstance(instances, list):
            for i in instances:
                self.base.write_parameter(
                    self.position,
                    parameter,
                    value,
                    i,
                )

        Logging.logger.info(
            f"{self.name}: Setting {parameter.name}, instances {instances} to {value}"
        )

    def get_parameter_from_identifier(self, parameter_identifier: Union[int, str]):
        """helper function to get parameter object from identifier"""
        if isinstance(parameter_identifier, int):
            if parameter_identifier in self.module_dicts.parameters:
                return self.module_dicts.parameters.get(parameter_identifier)
        if isinstance(parameter_identifier, str):
            # iterate over available parameters and extract the one with the correct name
            for p in self.module_dicts.parameters.values():
                if p.name == parameter_identifier:
                    return p

        raise NotImplementedError(f"{self} has no parameter {parameter_identifier}")

    @CpxBase.require_base
    def read_module_parameter(
        self,
        parameter: Union[str, int],
        instances: Union[int, list] = None,
    ) -> Any:
        """Read module parameter if available. Access either by ID (faster) or by Name.

        :param parameter: Parameter name or ID
        :type parameter: str | int
        :param instances: (optional) Index or list of instances of the parameter.
            If None, all instances will be written
        :type instance: int | list
        :return: Value of the parameter. Type depends on the parameter
        :rtype: Any"""
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        # PARAMETER HANDLING
        parameter = self.get_parameter_from_identifier(parameter)
        if parameter.enums:  # overwrite the parameter datatype from enum
            parameter.data_type = parameter.enums.data_type

        # INSTANCE HANDLING
        instances = self._check_instances(parameter, instances)

        # VALUE HANDLING
        values = []
        for i in instances:
            values.append(
                self.base.read_parameter(
                    self.position,
                    parameter,
                    i,
                )
            )

        if len(instances) == 1:
            values = values[0]

        Logging.logger.info(
            f"{self.name}: Read {values} from instances {instances} of parameter {parameter.name}"
        )
        return values

    @CpxBase.require_base
    def read_module_parameter_enum_str(
        self,
        parameter: Union[str, int],
        instances: Union[int, list] = None,
    ) -> Any:
        """Read enum name of module parameter if available. Access either by ID (faster) or by Name.

        :param parameter: Parameter name or ID
        :type parameter: str | int
        :param instances: (optional) Index or list of instances of the parameter.
            If None, all instances will be written
        :type instance: int | list
        :return: Name of the enum value.
        :rtype: str"""
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        # VALUE HANDLING
        values = self.read_module_parameter(parameter, instances)

        # PARAMETER HANDLING
        parameter = self.get_parameter_from_identifier(parameter)

        if not parameter.enums:
            Logging.logger.info(f"{parameter} has no enums. Returning values instead.")
            return values

        enum_id_to_name_dict = {v: k for k, v in parameter.enums.enum_values.items()}

        if isinstance(values, int):
            if values not in enum_id_to_name_dict:
                raise ValueError(
                    f"ENUM id {values} is not known (available: {enum_id_to_name_dict})"
                )
            return enum_id_to_name_dict[values]

        if isinstance(values, list):
            return [
                enum_id_to_name_dict[v] for v in values if v in enum_id_to_name_dict
            ]

        raise ValueError(
            f"Parameter {parameter} could not be read from instances {instances}"
        )

    @CpxBase.require_base
    def read_diagnosis_code(self) -> int:
        """Read the diagnosis code from the module

        :ret value: Diagnosis code
        :rtype: tuple"""
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        reg = self.base.read_reg_data(
            self.system_entry_registers.diagnosis + 4, length=2
        )
        return int.from_bytes(reg, byteorder="little")

    @CpxBase.require_base
    def read_present_state(self) -> bool:
        """Read the present state from the module

        :ret value: Present state
        :rtype: bool"""
        reg = self.base.read_reg_data(
            self.system_entry_registers.diagnosis + 1, length=1
        )
        return bool(int.from_bytes(reg, byteorder="little") >> 8)

    @CpxBase.require_base
    def read_diagnosis_information(self) -> ModuleDiagnosis:
        """Read the diagnosis information from the module. Contains:
         * diagnosis_id
         * name
         * description
         * guideline

        :ret value: Diagnosis information
        :rtype: ModuleDiagnosis or None if no diagnosis is active"""
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        diagnosis_code = self.read_diagnosis_code()
        return self.module_dicts.diagnosis.get(diagnosis_code)

    # Busmodule special functions
    @CpxBase.require_base
    def read_system_parameters(self) -> SystemParameters:
        """Read parameters from EP module.

        :return: Parameters object containing all r/w parameters
        :rtype: Parameters
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        params = SystemParameters(
            dhcp_enable=self.base.read_parameter(
                self.position, self.module_dicts.parameters.get(12000)
            ),
            ip_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12001)
                )
            ),
            subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12002)
                ),
            ),
            gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12003)
                )
            ),
            active_ip_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12004)
                )
            ),
            active_subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12005)
                )
            ),
            active_gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12006)
                )
            ),
            mac_address=convert_to_mac_string(
                self.base.read_parameter(
                    self.position, self.module_dicts.parameters.get(12007)
                )
            ),
            setup_monitoring_load_supply=self.base.read_parameter(
                self.position, self.module_dicts.parameters.get(20022)
            )
            & 0xFF,
        )
        Logging.logger.info(f"{self.name}: Reading parameters: {params}")
        return params

    # IO-Link special functions
    @CpxBase.require_base
    def read_pqi(self, channel: int = None) -> Union[dict, list[dict]]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels.

        :param channel: Channel number, starting with 0, optional
        :type channel: int
        :return: PQI information as dict for one channel or as list of dicts for more channels
        :rtype: dict | list[dict] depending on param channel
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        data45 = self.base.read_reg_data(self.system_entry_registers.inputs + 16)[0]
        data67 = self.base.read_reg_data(self.system_entry_registers.inputs + 17)[0]
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

        Logging.logger.info(f"{self.name}: Reading PQI of channel(s) {channel}")

        if channel is None:
            return channels_pqi
        return channels_pqi[channel]

    @CpxBase.require_base
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels.

        :return: a dict of parameters for every channel.
        :rtype: list[dict]
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        params = {
            "port_status_info": self.module_dicts.parameters.get(20074),
            "revision_id": self.module_dicts.parameters.get(20075),
            "transmission_rate": self.module_dicts.parameters.get(20076),
            "actual_cycle_time": self.module_dicts.parameters.get(20077),
            "actual_vendor_id": self.module_dicts.parameters.get(20078),
            "actual_device_id": self.module_dicts.parameters.get(20079),
            "iolink_input_data_length": self.module_dicts.parameters.get(20108),
            "iolink_output_data_length": self.module_dicts.parameters.get(20109),
        }
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
                    self.position, params.get("port_status_info"), channel_item
                ),
            )
            revision_id = self.base.read_parameter(
                self.position, params.get("revision_id"), channel_item
            )
            transmission_rate = transmission_rate_dict.get(
                self.base.read_parameter(
                    self.position, params.get("transmission_rate"), channel_item
                ),
            )
            actual_cycle_time = self.base.read_parameter(
                self.position, params.get("actual_cycle_time"), channel_item
            )
            actual_vendor_id = self.base.read_parameter(
                self.position, params.get("actual_vendor_id"), channel_item
            )
            actual_device_id = self.base.read_parameter(
                self.position, params.get("actual_device_id"), channel_item
            )
            input_data_length = self.base.read_parameter(
                self.position, params.get("iolink_input_data_length"), channel_item
            )
            output_data_length = self.base.read_parameter(
                self.position,
                params.get("iolink_output_data_length"),
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

    def cast_channel_argument_to_list(
        self, channels: Union[list[int], int]
    ) -> list[int]:
        """Checks if the given channel argument is a list and casts it to a list if not.
        Else the list stays as it is.
        Returns a list containing the channels.

        :param channels: list of channels or single channel number
        :type: channels
        """

        if not isinstance(channels, list):
            channels = [channels]

        return channels

    @CpxBase.require_base
    def read_isdu(
        self,
        channels: Union[list[int], int],
        index: int,
        subindex: int = 0,
        data_type: str = "raw",
    ) -> any:
        """Read isdu (device parameter) from defined channel.
        Raises CpxRequestError when read failed.

        :param channels: list of channels or single channel number(s)
            which should be read, starting with 0
        :type channels: list[int] | int
        :param index: io-link parameter index
        :type index: int
        :param subindex: (optional) io-link parameter subindex, defaults to 0
        :type subindex: int
        :param data_type: (optional) datatype for correct interpretation.
            Check ap_supported_datatypes.SUPPORTED_ISDU_DATATYPES for a list of
            supported datatypes
        :type data_type: str
        :return: list of values or single value depending on the datatype for each channel
        :rtype: list[any] | any
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        results = []

        index = index.to_bytes(2, "little")
        subindex = subindex.to_bytes(2, "little")

        channels = self.cast_channel_argument_to_list(channels=channels)

        for channel in channels:
            module_index = (self.position + 1).to_bytes(2, "little")
            channel = (channel + 1).to_bytes(2, "little")
            length = (0).to_bytes(2, "little")  # always zero when reading

            # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
            # it's easiest if we stay on 100 and byteorder "big"
            command = (100).to_bytes(2, "little")

            # checking the availability in the SUPPORTED_ISDU_DATATYPES is not required but
            # keeps the two files synchronized during development
            if data_type not in SUPPORTED_ISDU_DATATYPES:
                raise TypeError(
                    f"Datatype '{data_type}' is not supported by read_isdu()"
                )

            # select module, starts with 1
            self.base.write_reg_data(
                module_index, ap_modbus_registers.ISDU_MODULE_NO.register_address
            )
            # select channel, starts with 1
            self.base.write_reg_data(
                channel, ap_modbus_registers.ISDU_CHANNEL.register_address
            )
            # select index
            self.base.write_reg_data(
                index, ap_modbus_registers.ISDU_INDEX.register_address
            )
            # select subindex
            self.base.write_reg_data(
                subindex, ap_modbus_registers.ISDU_SUBINDEX.register_address
            )
            # select length of data in bytes
            self.base.write_reg_data(
                length, ap_modbus_registers.ISDU_LENGTH.register_address
            )
            # command
            self.base.write_reg_data(
                command, ap_modbus_registers.ISDU_COMMAND.register_address
            )

            stat, cnt = 1, 0
            while stat > 0 and cnt < 1000:
                stat = int.from_bytes(
                    self.base.read_reg_data(*ap_modbus_registers.ISDU_STATUS),
                    byteorder="little",
                )
                cnt += 1
            if cnt >= 1000:
                raise CpxRequestError("ISDU data read failed")

            # read back the actual length from the length register
            actual_length = int.from_bytes(
                self.base.read_reg_data(
                    ap_modbus_registers.ISDU_LENGTH.register_address
                ),
                byteorder="little",
            )

            ret = self.base.read_reg_data(
                ap_modbus_registers.ISDU_DATA.register_address, actual_length
            )
            Logging.logger.info(
                f"{self.name}: Reading ISDU for channel {channel}: {ret}"
            )

            if data_type == "raw":
                results.append(ret[:actual_length])
            elif data_type == "str":
                results.append(ret.decode("ascii").split("\x00", 1)[0])
            elif data_type == "uint":
                ret = ret[:actual_length]
                results.append(int.from_bytes(ret, byteorder="big"))
            elif data_type in ["sint", "int"]:
                ret = ret[:actual_length]
                results.append(int.from_bytes(ret, byteorder="big", signed=True))
            elif data_type == "bool":
                ret = ret[:actual_length]
                results.append(bool.from_bytes(ret, byteorder="big"))
            elif data_type == "float":
                ret = ret[:actual_length]
                results.append(struct.unpack("!f", ret)[0])
            else:
                # this is unnecessary but required for consistent return statements
                raise TypeError(
                    f"Datatype '{data_type}' is not supported by read_isdu()"
                )

        if len(results) == 1:
            return results[0]

        return results

    @CpxBase.require_base
    def write_isdu(
        self,
        data: Union[bytes, str, int, bool],
        channels: Union[list[int], int],
        index: int,
        subindex: int = 0,
    ) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed.

        :param data: Data to write.
        :type data: bytes|str|int|bool
        :param channels: list of channel numbers or single channel number
                         which should be written, starting with 0
        :type channels: list[int] | int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        index = (index).to_bytes(2, "little")
        subindex = (subindex).to_bytes(2, "little")

        channels = self.cast_channel_argument_to_list(channels=channels)

        for channel in channels:
            module_index = (self.position + 1).to_bytes(2, "little")
            channel = (channel + 1).to_bytes(2, "little")

            if isinstance(data, bytes):
                length = (len(data)).to_bytes(2, "little")
                command = (101).to_bytes(2, "little")  # write without byteswap

            elif isinstance(data, str):
                length = (len(data)).to_bytes(2, "little")
                command = (101).to_bytes(2, "little")  # write without byteswap
                data = data.encode(encoding="ascii")

            elif isinstance(data, bool):
                length = (1).to_bytes(2, "little")
                command = (101).to_bytes(2, "little")  # write without byteswap
                data = data.to_bytes(1, byteorder="big")

            elif isinstance(data, int):
                # calculate bytelength of integer
                length_int = (data.bit_length() + 7) // 8
                if length_int == 0:
                    length_int = 1
                length = length_int.to_bytes(2, "little")
                command = (101).to_bytes(2, "little")  # write without byteswap

                # negative data needs to be filled with 0xff on uneven bytes
                if data < 0 and length_int % 2:
                    data = data.to_bytes(
                        length_int + 1, byteorder="big", signed=data < 0
                    )
                else:
                    data = data.to_bytes(length_int, byteorder="big", signed=data < 0)

            elif isinstance(data, float):
                data = struct.pack("!f", data)
                command = (101).to_bytes(2, "little")  # write without byteswap
                length = len(data).to_bytes(2, "little")

            else:
                raise TypeError(
                    f"Datatype '{type(data)}' is not supported by write_isdu()"
                )

            # select module, starts with 1
            self.base.write_reg_data(
                module_index, ap_modbus_registers.ISDU_MODULE_NO.register_address
            )
            # select channel, starts with 1
            self.base.write_reg_data(
                channel, ap_modbus_registers.ISDU_CHANNEL.register_address
            )
            # select index
            self.base.write_reg_data(
                index, ap_modbus_registers.ISDU_INDEX.register_address
            )
            # select subindex
            self.base.write_reg_data(
                subindex, ap_modbus_registers.ISDU_SUBINDEX.register_address
            )
            # select length of data in bytes
            self.base.write_reg_data(
                length, ap_modbus_registers.ISDU_LENGTH.register_address
            )
            # write data to data register
            self.base.write_reg_data(
                data, ap_modbus_registers.ISDU_DATA.register_address
            )
            # command
            self.base.write_reg_data(
                command, ap_modbus_registers.ISDU_COMMAND.register_address
            )

        stat, cnt = 1, 0
        while stat > 0 and cnt < 1000:
            stat = int.from_bytes(
                self.base.read_reg_data(*ap_modbus_registers.ISDU_STATUS),
                byteorder="little",
            )
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError(
                "ISDU data write failed\nThis can happen if the device denies "
                "access to the requested isdu parameter with the given data"
            )

        Logging.logger.info(
            f"{self.name}: Write ISDU {data} to channels {channels} ({index},{subindex})"
        )

    @CpxBase.require_base
    def change_variant(self, variant: int | str) -> None:
        """Change the module variant if supported.

        :param variant: Variant number or name to change to
        :type variant: int | str
        """
        if len(self.variant_list) <= 1 or self.variant_switch_parameter is None:
            raise NotImplementedError(f"{self} has no variants to change")

        variant_ids = [
            v.variant_identification["ModuleCode"] for v in self.variant_list
        ]
        variant_id = None
        if isinstance(variant, str):
            for v in self.variant_list:
                if v.name == variant:
                    variant_id = v.variant_identification["ModuleCode"]
                    break
        else:
            variant_id = variant
        if variant_id is None or variant_id not in variant_ids:
            raise ValueError(
                f"Variant {variant_id} is not supported. Supported variants are: "
                f"{[(v.name, v.variant_identification['ModuleCode']) for v in self.variant_list]}"
            )

        self.base.write_parameter(
            self.position,
            self.variant_switch_parameter,
            variant_id,
            0,
        )

        with self.base.interface_lock:
            # if the module code changed, wait for lost device
            if variant_id != self.apdd_information.module_code:
                is_present = self.read_present_state()
                timeout = time.time() + 30
                while is_present and time.time() < timeout:
                    is_present = self.read_present_state()
                    time.sleep(0.1)
                # reset connection
                self.base.reconnect()
                is_present = self.read_present_state()
                timeout = time.time() + 30
                while not is_present and time.time() < timeout:
                    self.base.reconnect()
                    is_present = self.read_present_state()
                    time.sleep(0.1)
        Logging.logger.info(f"{self.name}: Changing variant to {variant_id}")
