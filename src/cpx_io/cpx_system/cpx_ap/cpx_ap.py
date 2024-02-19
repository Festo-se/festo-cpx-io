"""CPX-AP module implementations"""

import struct
from typing import Any
from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError

from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.cpx_ap import cpx_ap_parameters
from cpx_io.cpx_system.cpx_ap.cpx_ap_module_definitions import CPX_AP_MODULE_ID_LIST
from cpx_io.cpx_system.cpx_ap.parameter_packing import parameter_pack, parameter_unpack
from cpx_io.utils.helpers import div_ceil
from cpx_io.utils.logging import Logging


class CpxAp(CpxBase):
    """CPX-AP base class"""

    @dataclass
    class ModuleInformation:
        """Information of AP Module"""

        # pylint: disable=too-many-instance-attributes
        module_code: int = None
        module_class: int = None
        communication_profiles: int = None
        input_size: int = None
        input_channels: int = None
        output_size: int = None
        output_channels: int = None
        hw_version: int = None
        fw_version: str = None
        serial_number: str = None
        product_key: str = None
        order_text: str = None

    @dataclass
    class Diagnostics(CpxBase.BitwiseReg8):
        """Diagnostic information"""

        # pylint: disable=too-many-instance-attributes
        degree_of_severity_information: bool
        degree_of_severity_maintenance: bool
        degree_of_severity_warning: bool
        degree_of_severity_error: bool
        _4: None  # spacer for not-used bit
        _5: None  # spacer for not-used bit
        module_present: bool
        _7: None  # spacer for not-used bit

    def __init__(self, timeout: float = 0.1, **kwargs):
        """Constructor of the CpxAp class.

        :param timeout: Modbus timeout (in s) that should be configured on the slave
        :type timeout: float
        """
        super().__init__(**kwargs)

        self.next_output_register = None
        self.next_input_register = None

        self.set_timeout(int(timeout * 1000))

        module_count = self.read_module_count()
        for i in range(module_count):
            self.add_module(self.read_module_information(i))

    @property
    def modules(self):
        """getter function for private modules property"""
        return self._modules

    def set_timeout(self, timeout_ms: int) -> None:
        """Sets the modbus timeout to the provided value

        :param timeout_ms: Modbus timeout in ms (milli-seconds)
        :type timeout_ms: int
        """
        Logging.logger.info(f"Setting modbus timeout to {timeout_ms} ms")
        registers = timeout_ms.to_bytes(length=4, byteorder="little")
        self.write_reg_data(registers, cpx_ap_registers.TIMEOUT.register_address)

        # Check if it actually succeeded
        indata = int.from_bytes(
            self.read_reg_data(*cpx_ap_registers.TIMEOUT),
            byteorder="little",
            signed=False,
        )
        if indata != timeout_ms:
            Logging.logger.error("Setting of modbus timeout was not successful")

    def add_module(self, info: ModuleInformation) -> None:
        """Adds one module to the base. This is required to use the module.
        The module must be identified by the module code in info.

        :param info: ModuleInformation object containing the read-out info from the module
        :type info: ModuleInformation
        """
        module = next(
            (
                module_class()
                for module_class in CPX_AP_MODULE_ID_LIST
                if info.module_code in module_class.module_codes
            ),
            None,
        )

        if module is None:
            raise NotImplementedError(
                "This module is not yet implemented or not available"
            )

        module.update_information(info)
        module.configure(self, len(self._modules))
        self._modules.append(module)
        self.update_module_names()
        Logging.logger.debug(f"Added module {module.name} ({type(module).__name__})")
        return module

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer

        :return: Number of the total amount of connected modules
        :rtype: int
        """
        reg = self.read_reg_data(*cpx_ap_registers.MODULE_COUNT)
        value = int.from_bytes(reg, byteorder="little")
        Logging.logger.debug(f"Total module count: {value}")
        return value

    def _module_offset(self, modbus_command: tuple, module: int) -> int:
        register, length = modbus_command
        return ((register + 37 * module), length)

    def read_module_information(self, position: int) -> ModuleInformation:
        """Reads and returns detailed information for a specific IO module

        :param position: Module position index starting with 0
        :type position: int
        :return: ModuleInformation object containing all the module information from the module
        :rtype: ModuleInformation
        """

        info = self.ModuleInformation(
            module_code=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.MODULE_CODE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            module_class=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.MODULE_CLASS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            communication_profiles=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(
                        cpx_ap_registers.COMMUNICATION_PROFILE, position
                    )
                ),
                byteorder="little",
                signed=False,
            ),
            input_size=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.INPUT_SIZE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            input_channels=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.INPUT_CHANNELS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            output_size=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.OUTPUT_SIZE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            output_channels=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.OUTPUT_CHANNELS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            hw_version=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.HW_VERSION, position)
                ),
                byteorder="little",
                signed=False,
            ),
            fw_version=".".join(
                str(x)
                for x in struct.unpack(
                    "<HHH",
                    self.read_reg_data(
                        *self._module_offset(cpx_ap_registers.FW_VERSION, position)
                    ),
                )
            ),
            serial_number=hex(
                int.from_bytes(
                    self.read_reg_data(
                        *self._module_offset(cpx_ap_registers.SERIAL_NUMBER, position)
                    ),
                    byteorder="little",
                    signed=False,
                )
            ),
            product_key=(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.PRODUCT_KEY, position)
                )
                .decode("ascii")
                .strip("\x00")
            ),
            order_text=(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.ORDER_TEXT, position)
                )
                .decode("ascii")
                .strip("\x00")
            ),
        )
        Logging.logger.debug(f"Reading ModuleInformation: {info}")
        return info

    def read_diagnostic_status(self) -> list[Diagnostics]:
        """Read the diagnostic status and return a Diagnostics object for each module

        :ret value: Diagnostics status for every module
        :rtype: list[Diagnostics]
        """
        # overwrite the type UINT8[n] with the actual module count + 1 (see datasheet)
        ap_diagnosis_parameter = cpx_ap_parameters.ParameterMapItem(
            id=cpx_ap_parameters.AP_DIAGNOSIS_STATUS.id,
            dtype=f"UINT8[{self.read_module_count() + 1}]",
        )

        reg = self.read_parameter(0, ap_diagnosis_parameter)
        return [self.Diagnostics.from_int(r) for r in reg]

    def write_parameter(
        self,
        position: int,
        parameter: cpx_ap_parameters.ParameterMapItem,
        data: list[int] | int | bool,
        instance: int = 0,
    ) -> None:
        """Write parameters via module position, param_id, instance (=channel) and data to write
        Data must be a list of (signed) 16 bit values or one 16 bit (signed) value or bool
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param parameter: AP Parameter
        :type parameter: ParameterMapItem
        :param data: list of 16 bit signed integers, one signed 16 bit integer or bool to write
        :type data: list | int | bool
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        """
        raw = parameter_pack(parameter, data)
        self._write_parameter_raw(position, parameter.id, instance, raw)

    def _write_parameter_raw(
        self, position: int, param_id: int, instance: int, data: bytes
    ) -> None:
        """Read parameters via module position, param_id, instance (=channel)
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :param data: data as bytes object
        :type data: bytes
        """

        param_reg = cpx_ap_registers.PARAMETERS.register_address
        # module indexing starts with 1 (see datasheet)
        module_index = (position + 1).to_bytes(2, byteorder="little")
        param_id = param_id.to_bytes(2, byteorder="little")
        instance = instance.to_bytes(2, byteorder="little")
        # length in 16 bit registers
        length = (len(data) // 2).to_bytes(2, byteorder="little")
        command = (2).to_bytes(2, byteorder="little")  # 1=read, 2=write

        # Strangely this sending has to be repeated several times,
        # actually it is tried up to 10 times.
        for i in range(10):
            # prepare the command
            self.write_reg_data(module_index + param_id + instance + length, param_reg)
            # write data to register
            self.write_reg_data(data, param_reg + 10)
            # execute the command
            self.write_reg_data(command, param_reg + 3)

            exe_code = 0
            while exe_code < 16:
                exe_code = int.from_bytes(
                    self.read_reg_data(param_reg + 3), byteorder="little"
                )
                # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
                if exe_code == 4:
                    raise CpxRequestError

            # Validation check according to datasheet
            read_registers = self.read_reg_data(param_reg + 10, len(data) // 2)

            if read_registers == data:
                break

        if i >= 9:
            raise CpxRequestError(
                "Parameter might not have been written correctly after 10 tries"
            )
        Logging.logger.debug(f"Wrote data {data} to module position: {position - 1}")

    def read_parameter(
        self,
        position: int,
        parameter: cpx_ap_parameters.ParameterMapItem,
        instance: int = 0,
    ) -> Any:
        """Read parameter

        :param position: Module position index starting with 0
        :type position: int
        :param parameter: AP Parameter
        :type parameter: ParameterMapItem
        :param instance: (optional) Parameter Instance (typically the channel, see datasheet)
        :type instance: int
        :return: Parameter value
        :rtype: Any
        """
        raw = self._read_parameter_raw(position, parameter.id, instance)
        data = parameter_unpack(parameter, raw)
        return data

    def _read_parameter_raw(self, position: int, param_id: int, instance: int) -> bytes:
        """Read parameters via module position, param_id, instance (=channel)
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :return: Parameter register values
        :rtype: bytes
        """

        param_reg = cpx_ap_registers.PARAMETERS.register_address
        # module indexing starts with 1 (see datasheet)
        module_index = (position + 1).to_bytes(2, byteorder="little")
        param_id = param_id.to_bytes(2, byteorder="little")
        instance = instance.to_bytes(2, byteorder="little")
        command = (1).to_bytes(2, byteorder="little")  # 1=read, 2=write

        # prepare and execute the read command
        self.write_reg_data(module_index + param_id + instance + command, param_reg)

        # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
        exe_code = 0
        while exe_code < 16:
            exe_code = int.from_bytes(
                self.read_reg_data(param_reg + 3), byteorder="little"
            )
            if exe_code == 4:
                raise CpxRequestError

        # get datalength in bytes from register 10004
        data_length = div_ceil(
            int.from_bytes(self.read_reg_data(param_reg + 4), byteorder="little"),
            2,
        )

        return self.read_reg_data(param_reg + 10, data_length)
