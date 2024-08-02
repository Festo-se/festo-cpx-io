"""Generic AP module implementation from APDD"""

import struct
import inspect
from typing import Any
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap import ap_modbus_registers
from cpx_io.utils.boollist import bytes_to_boollist, boollist_to_bytes
from cpx_io.utils.helpers import (
    div_ceil,
    channel_range_check,
    instance_range_check,
    convert_uint32_to_octett,
    convert_to_mac_string,
)
from cpx_io.utils.logging import Logging


class ApModule(CpxModule):
    """Generic AP module class. This includes all functions that are shared
    among the modules. To get an overview of your system and the supported
    functions of the individual modules, see the system documentation of the
    CpxAp object"""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-lines
    # pylint: disable=too-many-arguments
    # Should be devided in sub classes instead!

    # List of all implemented datatypes
    SUPPORTED_DATATYPES = ["UINT16", "INT16", "BOOL"]
    SUPPORTED_IOL_DATATYPES = ["UINT8"]

    PRODUCT_CATEGORY_MAPPING = {
        "read_channels": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "read_channel": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "write_channels": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "write_channel": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "set_channel": [
            ProductCategory.DIGITAL,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "clear_channel": [
            ProductCategory.DIGITAL,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "toggle_channel": [
            ProductCategory.DIGITAL,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
        ],
        "write_module_parameter": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
            ProductCategory.INTERFACE,
        ],
        "read_module_parameter": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
            ProductCategory.INTERFACE,
        ],
        "read_diagnosis_code": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
            ProductCategory.INTERFACE,
        ],
        "read_diagnosis_information": [
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.VTOM,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
            ProductCategory.INTERFACE,
        ],
        "read_system_parameters": [ProductCategory.INTERFACE],
        "read_pqi": [ProductCategory.IO_LINK],
        "read_fieldbus_parameters": [ProductCategory.IO_LINK],
        "read_isdu": [ProductCategory.IO_LINK],
        "write_isdu": [ProductCategory.IO_LINK],
        "configure": [
            ProductCategory.INTERFACE,
            ProductCategory.ANALOG,
            ProductCategory.DIGITAL,
            ProductCategory.IO_LINK,
            ProductCategory.INFRASTRUCTURE,
            ProductCategory.MPA_L,
            ProductCategory.MPA_S,
            ProductCategory.VTSA,
            ProductCategory.VTUG,
            ProductCategory.VTUX,
            ProductCategory.VTOM,
        ],
    }
    INPUT_FUNCTIONS = ["read_channels", "read_channel"]
    OUTPUT_FUNCTIONS = [
        "write_channels",
        "write_channel",
        "set_channel",
        "clear_channel",
        "toggle_channel",
    ]
    PARAMETER_FUNCTIONS = ["write_module_parameter", "read_module_parameter"]
    DIAGNOSIS_FUNCTIONS = ["read_diagnosis_code", "read_diagnosis_information"]

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

    @dataclass
    class ApddInformation:
        """ApddInformation"""

        # pylint: disable=too-many-instance-attributes
        description: str
        name: str
        module_type: str
        configurator_code: str
        part_number: str
        module_class: str
        module_code: str
        order_text: str
        product_category: str
        product_family: str

    @dataclass
    class ModuleParameters:
        """AP Parameters of module"""

        # pylint: disable=too-many-instance-attributes
        fieldbus_serial_number: int
        product_key: str
        firmware_version: str
        module_code: int
        temp_asic: int
        logic_voltage: float
        load_voltage: float
        hw_version: int
        io_link_variant: str = "n.a."
        operating_supply: bool = False

    @dataclass
    class ModuleDiagnosis:
        """ModuleDiagnosis dataclass"""

        description: str
        diagnosis_id: str
        guideline: str
        name: str

    def __init__(
        self,
        apdd_information: dict = None,
        channels: tuple = None,
        parameter_list: list = None,
        diagnosis_list: list = None,
        name: str = None,
    ):
        super().__init__(name=name)
        self.information = None
        self.name = apdd_information.name
        self.apdd_information = apdd_information

        self.input_channels = channels[0] + channels[2]
        self.output_channels = channels[1] + channels[2]
        self.inout_channels = channels[2]

        self.diagnosis_register = None

        self.parameter_dict = {p.parameter_id: p for p in parameter_list}
        self.diagnosis_dict = {
            int(d.diagnosis_id.lstrip("0x"), base=16): d for d in diagnosis_list
        }

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
        if not self.PRODUCT_CATEGORY_MAPPING.get(func_name):
            function_is_supported = False

        # check if function is supported for the product category
        elif self.apdd_information.product_category not in [
            v.value for v in self.PRODUCT_CATEGORY_MAPPING.get(func_name)
        ]:
            function_is_supported = False

        # check if outputs are available if it's an output function
        elif func_name in self.OUTPUT_FUNCTIONS and not self.output_channels:
            function_is_supported = False

        # check if inputs or outputs are available if it's an input function
        elif func_name in self.INPUT_FUNCTIONS and not (
            self.input_channels or self.output_channels
        ):
            function_is_supported = False

        # check if there are parameters if it's a parameter function
        elif func_name in self.PARAMETER_FUNCTIONS and not self.parameter_dict:
            function_is_supported = False

        # check if there are diagnosis information if it's a diagnosis function
        elif func_name in self.DIAGNOSIS_FUNCTIONS and not self.diagnosis_dict:
            function_is_supported = False

        return function_is_supported

    def _check_function_supported(self, func_name):
        if not self.is_function_supported(func_name):
            raise NotImplementedError(f"{self} has no function <{func_name}>")

    def configure(self, base: CpxBase, position: int) -> None:
        """This function is used by CpxBase to setup the system. Do not use this function."""
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        super().configure(base=base, position=position)

        self.diagnosis_register = self.base.next_diagnosis_register

        self.base.next_output_register += div_ceil(self.information.output_size, 2)
        self.base.next_input_register += div_ceil(self.information.input_size, 2)
        self.base.next_diagnosis_register += 6  # always 6 registers per module

        # IO-Link special parameter
        if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
            self.fieldbus_parameters = self.read_fieldbus_parameters()

    @CpxBase.require_base
    def read_channels(self, outputs_only: bool = False) -> list:
        """Read all channels from module and interpret them as the module intends.

        For mixed IN/OUTput modules the optional parameter 'outputs_only' defines
        if the outputs are numbered WITH (after) the inputs ("False", default), so the range
        of output channels is <number of input channels>..<number of input and output channels>
        If "True", the outputs are numbered from 0..<number of output channels>, the inputs
        cannot be accessed this way.

        :param outputs_only: Outputs should be numbered independend from inputs, optional
        :type outputs_only: bool

        :return: List of values of the channels
        :rtype: list
        """

        self._check_function_supported(inspect.currentframe().f_code.co_name)

        byte_input_size = div_ceil(self.information.input_size, 2)
        byte_output_size = div_ceil(self.information.output_size, 2)

        values = []
        # if available, read inputs
        if self.input_channels and not outputs_only:
            data = self.base.read_reg_data(self.input_register, byte_input_size)

            if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
                # IO-Link splits into byte_channel_size chunks. Assumes all channels are the same
                byte_channel_size = self.inout_channels[0].array_size
                # for IO-Link only the inout_channels are relevant
                data = data[: len(self.inout_channels * byte_channel_size)]

                channels = [
                    data[i : i + byte_channel_size]
                    for i in range(0, len(data), byte_channel_size)
                ]
                Logging.logger.info(
                    f"{self.name}: Reading IO-Link channels: {channels}"
                )
                return channels

            # Remember to update the SUPPORTED_DATATYPES list when you add more types here
            if all(c.data_type == "BOOL" for c in self.input_channels):
                values.extend(bytes_to_boollist(data)[: len(self.input_channels)])
            elif all(c.data_type == "INT16" for c in self.input_channels):
                values.extend(struct.unpack("<" + "h" * (len(data) // 2), data))
            elif all(c.data_type == "UINT16" for c in self.input_channels):
                values.extend(struct.unpack("<" + "H" * (len(data) // 2), data))
            else:
                raise TypeError(
                    f"Input data type {self.input_channels[0].data_type} are not supported "
                    "or types are not the same for each channel"
                )

        # if available, read outputs
        if self.output_channels:
            data = self.base.read_reg_data(self.output_register, byte_output_size)

            # Remember to update the SUPPORTED_DATATYPES list when you add more types here
            if all(c.data_type == "BOOL" for c in self.output_channels):
                values.extend(bytes_to_boollist(data)[: len(self.output_channels)])
            elif all(c.data_type == "INT16" for c in self.output_channels):
                values.extend(struct.unpack("<" + "h" * (len(data) // 2), data))
            elif all(c.data_type == "UINT16" for c in self.output_channels):
                values.extend(struct.unpack("<" + "H" * (len(data) // 2), data))
            else:
                raise TypeError(
                    f"Output data type {self.output_channels[0].data_type} are not supported "
                    "or types are not the same for each channel"
                )

        Logging.logger.info(f"{self.name}: Reading channels: {values}")
        return values

    @CpxBase.require_base
    def read_channel(
        self, channel: int, outputs_only: bool = False, full_size: bool = False
    ) -> Any:
        """Read back the value of one channel.

        For mixed IN/OUTput modules the optional parameter 'outputs_only' defines
        if the outputs are numbered WITH (after) the inputs ("False", default), so the range
        of output channels is <number of input channels>..<number of input and output channels>
        If "True", the outputs are numbered from 0..<number of output channels>, the inputs
        cannot be accessed this way.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param outputs_only: Outputs should be numbered independend from inputs, optional
        :type outputs_only: bool
        :param full_size: IO-Link channes should be returned in full datalength and not
            limited to the slave information datalength
        :type full_size: bool
        :return: Value of the channel
        :rtype: bool
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        if outputs_only:
            channel_count = len(self.output_channels)
        else:
            channel_count = (
                len([c for c in self.input_channels if c.direction == "in"])
                + len([c for c in self.output_channels if c.direction == "out"])
                + len(self.inout_channels)
            )

        channel_range_check(channel, channel_count)

        if self.input_channels and outputs_only:
            channel += len(self.input_channels)

        # if datalength is given and full_size is not requested, shorten output
        if self.fieldbus_parameters and not full_size:
            return self.read_channels()[channel][
                : self.fieldbus_parameters[channel]["Input data length"]
            ]

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

        if len(data) != len(self.output_channels):
            raise ValueError(
                f"Data must be list of {len(self.output_channels)} elements"
            )

        # Handle bool
        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if all(c.data_type == "BOOL" for c in self.output_channels) and all(
            isinstance(d, bool) for d in data
        ):
            reg = boollist_to_bytes(data)
            self.base.write_reg_data(reg, self.output_register)
            Logging.logger.info(f"{self.name}: Setting bool channels to {data}")
            return

        # Handle int
        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if all(
            c.data_type in ["INT16", "UINT16"] for c in self.output_channels
        ) and all(isinstance(d, int) for d in data):
            for i, d in enumerate(data):
                self.write_channel(i, d)
            return

        raise TypeError(
            f"Output data type {self.output_channels[0].data_type} is not supported or "
            "types are not the same for each channel (which is also not supported)"
        )

    @CpxBase.require_base
    def write_channel(self, channel: int, value: Any) -> None:
        """Set one channel value. Value must be the correct type, typecheck is done by the function
        Get the correct type by reading out the channel first and using type() on the value.

        :param channel: Channel number, starting with 0
        :type channel: int
        :value: Value that should be written to the channel
        :type value: Any
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        channel_range_check(channel, len(self.output_channels))

        # IO-Link special
        if self.apdd_information.product_category == ProductCategory.IO_LINK.value:
            # This assumes all channels are the same.
            byte_channel_size = self.inout_channels[0].array_size

            self.base.write_reg_data(
                value, self.output_register + byte_channel_size // 2 * channel
            )
            Logging.logger.info(
                f"{self.name}: Setting IO-Link channel {channel} to {value}"
            )
            return

        # Handle bool
        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if all(c.data_type == "BOOL" for c in self.output_channels) and isinstance(
            value, bool
        ):
            data = self.read_channels(outputs_only=True)
            data[channel] = value
            reg_content = boollist_to_bytes(data)
            self.base.write_reg_data(reg_content, self.output_register)
            Logging.logger.info(
                f"{self.name}: Setting bool channel {channel} to {value}"
            )
            return

        # Handle int16
        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if self.output_channels[channel].data_type == "INT16" and isinstance(
            value, int
        ):
            reg = struct.pack("<h", value)
            self.base.write_reg_data(reg, self.output_register)
            Logging.logger.info(f"{self.name}: Setting int channel to {value}")
            return

        # Handle uint16
        # Remember to update the SUPPORTED_DATATYPES list when you add more types here
        if self.output_channels[channel].data_type == "UINT16" and isinstance(
            value, int
        ):
            reg = struct.pack("<H", value)
            self.base.write_reg_data(reg, self.output_register)
            Logging.logger.info(f"{self.name}: Setting uint channel to {value}")
            return

        raise TypeError(
            f"{self.output_channels[0].data_type} is not supported or type(value) "
            f"is not compatible"
        )

    # Special functions for digital channels
    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """Set one channel to logic high level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """Set one channel to logic low level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """Set one channel the inverted of current logic level.

        :param channel: Channel number, starting with 0
        :type channel: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        # get the relevant value from the register and write the inverse
        value = self.read_channel(channel, outputs_only=True)
        self.write_channel(channel, not value)

    # Parameter functions
    @CpxBase.require_base
    def write_module_parameter(
        self,
        parameter: str | int,
        value: int | bool | str,
        instances: int | list = None,
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
            parameter = self.parameter_dict.get(parameter)
        elif isinstance(parameter, str):
            # iterate over available parameters and extract the one with the correct name
            parameter_list = [
                p for p in self.parameter_dict.values() if p.name == parameter
            ]
            parameter = parameter_list[0] if len(parameter_list) == 1 else None

        if parameter is None:
            raise NotImplementedError(f"{self} has no parameter {parameter_input}")

        if not parameter.is_writable:
            raise AttributeError(f"Parameter {parameter} is not writable")

        # INSTANCE HANDLING
        instances = self._check_instances(parameter, instances)

        # VALUE HANDLING
        if isinstance(value, str):
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

    @CpxBase.require_base
    def read_module_parameter(
        self,
        parameter: str | int,
        instances: int | list = None,
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
        parameter_input = parameter
        # PARAMETER HANDLING
        if isinstance(parameter, int):
            parameter = self.parameter_dict.get(parameter)
        elif isinstance(parameter, str):
            # iterate over available parameters and extract the one with the correct name
            parameter_list = [
                p for p in self.parameter_dict.values() if p.name == parameter
            ]
            parameter = parameter_list[0] if len(parameter_list) == 1 else None

        if parameter is None:
            raise NotImplementedError(f"{self} has no parameter {parameter_input}")

        if parameter.enums:
            # overwrite the parameter datatype from enum
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

        # if parameter is ENUM, return the according string. Indexing 0 should always work here
        # because the check that value is available was done before

        if parameter.enums:
            enum_values = []
            for val in values:
                enum_values.append(
                    [k for k, v in parameter.enums.enum_values.items() if v == val][0]
                )
            values = enum_values

        if len(instances) == 1:
            values = values[0]

        Logging.logger.info(
            f"{self.name}: Read {values} from instances {instances} of parameter {parameter.name}"
        )
        return values

    @CpxBase.require_base
    def read_diagnosis_code(self) -> int:
        """Read the diagnosis code from the module

        :ret value: Diagnosis code
        :rtype: tuple"""
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        reg = self.base.read_reg_data(self.diagnosis_register + 4, length=2)
        return int.from_bytes(reg, byteorder="little")

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

        return self.diagnosis_dict.get(diagnosis_code)

    # Busmodule special functions
    @CpxBase.require_base
    def read_system_parameters(self) -> SystemParameters:
        """Read parameters from EP module.

        :return: Parameters object containing all r/w parameters
        :rtype: Parameters
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        params = self.SystemParameters(
            dhcp_enable=self.base.read_parameter(
                self.position, self.parameter_dict.get(12000)
            ),
            ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12001))
            ),
            subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12002)),
            ),
            gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12003))
            ),
            active_ip_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12004))
            ),
            active_subnet_mask=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12005))
            ),
            active_gateway_address=convert_uint32_to_octett(
                self.base.read_parameter(self.position, self.parameter_dict.get(12006))
            ),
            mac_address=convert_to_mac_string(
                self.base.read_parameter(self.position, self.parameter_dict.get(12007))
            ),
            setup_monitoring_load_supply=self.base.read_parameter(
                self.position, self.parameter_dict.get(20022)
            )
            & 0xFF,
        )
        Logging.logger.info(f"{self.name}: Reading parameters: {params}")
        return params

    # IO-Link special functions
    @CpxBase.require_base
    def read_pqi(self, channel: int = None) -> dict | list[dict]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels.

        :param channel: Channel number, starting with 0, optional
        :type channel: int
        :return: PQI information as dict for one channel or as list of dicts for more channels
        :rtype: dict | list[dict] depending on param channel
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

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
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels.

        :return: a dict of parameters for every channel.
        :rtype: list[dict]
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        params = {
            "port_status_info": self.parameter_dict.get(20074),
            "revision_id": self.parameter_dict.get(20075),
            "transmission_rate": self.parameter_dict.get(20076),
            "actual_cycle_time": self.parameter_dict.get(20077),
            "actual_vendor_id": self.parameter_dict.get(20078),
            "actual_device_id": self.parameter_dict.get(20079),
            "iolink_input_data_length": self.parameter_dict.get(20108),
            "iolink_output_data_length": self.parameter_dict.get(20109),
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

    @CpxBase.require_base
    def read_isdu(self, channel: int, index: int, subindex: int) -> bytes:
        """Read isdu (device parameter) from defined channel.
        Raises CpxRequestError when read failed.

        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        :return: device parameter (index/subindex) for given channel
        :rtype: bytes
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        module_index = (self.position + 1).to_bytes(2, "little")
        channel = (channel + 1).to_bytes(2, "little")
        index = index.to_bytes(2, "little")
        subindex = subindex.to_bytes(2, "little")
        length = (0).to_bytes(2, "little")  # always zero when reading
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = (100).to_bytes(2, "little")

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, ap_modbus_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(
            channel, ap_modbus_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data(index, ap_modbus_registers.ISDU_INDEX.register_address)
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

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 5000:
            stat = int.from_bytes(
                self.base.read_reg_data(*ap_modbus_registers.ISDU_STATUS),
                byteorder="little",
            )

            cnt += 1
        if cnt >= 5000:
            raise CpxRequestError("ISDU data read failed")

        ret = self.base.read_reg_data(*ap_modbus_registers.ISDU_DATA)
        Logging.logger.info(f"{self.name}: Reading ISDU for channel {channel}: {ret}")

        return ret

    @CpxBase.require_base
    def write_isdu(self, data: bytes, channel: int, index: int, subindex: int) -> None:
        """Write isdu (device parameter) to defined channel.
        Raises CpxRequestError when write failed.

        :param data: Data as 16bit register values in list
        :type data: list[int]
        :param channel: Channel number, starting with 0
        :type channel: int
        :param index: io-link parameter index
        :type index: int
        :param subindex: io-link parameter subindex
        :type subindex: int
        """
        self._check_function_supported(inspect.currentframe().f_code.co_name)

        module_index = (self.position + 1).to_bytes(2, "little")
        channel = (channel + 1).to_bytes(2, "little")
        index = (index).to_bytes(2, "little")
        subindex = (subindex).to_bytes(2, "little")
        length = (len(data) * 2).to_bytes(2, "little")
        # command: 50 Read(with byte swap), 51 write(with byte swap), 100 read, 101 write
        command = (101).to_bytes(2, "little")

        # select module, starts with 1
        self.base.write_reg_data(
            module_index, ap_modbus_registers.ISDU_MODULE_NO.register_address
        )
        # select channel, starts with 1
        self.base.write_reg_data(
            channel, ap_modbus_registers.ISDU_CHANNEL.register_address
        )
        # select index
        self.base.write_reg_data(index, ap_modbus_registers.ISDU_INDEX.register_address)
        # select subindex
        self.base.write_reg_data(
            subindex, ap_modbus_registers.ISDU_SUBINDEX.register_address
        )
        # select length of data in bytes
        self.base.write_reg_data(
            length, ap_modbus_registers.ISDU_LENGTH.register_address
        )
        # write data to data register
        self.base.write_reg_data(data, ap_modbus_registers.ISDU_DATA.register_address)
        # command
        self.base.write_reg_data(
            command, ap_modbus_registers.ISDU_COMMAND.register_address
        )

        stat = 1
        cnt = 0
        while stat > 0 and cnt < 1000:
            stat = int.from_bytes(
                self.base.read_reg_data(*ap_modbus_registers.ISDU_STATUS),
                byteorder="little",
            )
            cnt += 1
        if cnt >= 1000:
            raise CpxRequestError("ISDU data write failed")

        Logging.logger.info(
            f"{self.name}: Write ISDU {data} to channel {channel} ({index},{subindex})"
        )
