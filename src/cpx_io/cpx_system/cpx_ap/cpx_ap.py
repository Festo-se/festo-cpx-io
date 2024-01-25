"""CPX-AP module implementations"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.utils.helpers import div_ceil

from cpx_io.cpx_system.cpx_ap import cpx_ap_registers
from cpx_io.cpx_system.cpx_ap.cpx_ap_module_definitions import CPX_AP_MODULE_ID_LIST
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

    def __init__(self, timeout: float = 0.1, **kwargs):
        """Constructor of the CpxAp class.

        :param timeout: Modbus timeout (in s) that should be configured on the slave
        :type timeout: float
        """
        super().__init__(**kwargs)

        self.next_output_register = None
        self.next_input_register = None
        self._modules = []
        self._module_names = []

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
        registers = self.encode_int(timeout_ms, data_type="uint32")
        self.write_reg_data(registers, *cpx_ap_registers.TIMEOUT)
        # Check if it actually succeeded
        indata = self.decode_int(
            self.read_reg_data(*cpx_ap_registers.TIMEOUT)[::-1], data_type="uint32"
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

    def update_module_names(self):
        """Updates the module name list and attributes accordingly"""
        for name in self._module_names:
            delattr(self, name)

        self._module_names = [module.name for module in self._modules]
        for name, module in zip(self._module_names, self._modules):
            setattr(self, name, module)

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer

        :return: Number of the total amount of connected modules
        :rtype: int
        """
        ret = self.read_reg_data(*cpx_ap_registers.MODULE_COUNT)[0]
        Logging.logger.debug(f"Total module count: {ret}")
        return ret

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
            module_code=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.MODULE_CODE, position)
                ),
                data_type="int32",
            ),
            module_class=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.MODULE_CLASS, position)
                ),
                data_type="uint8",
            ),
            communication_profiles=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(
                        cpx_ap_registers.COMMUNICATION_PROFILE, position
                    )
                ),
                data_type="uint16",
            ),
            input_size=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.INPUT_SIZE, position)
                ),
                data_type="uint16",
            ),
            input_channels=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.INPUT_CHANNELS, position)
                ),
                data_type="uint16",
            ),
            output_size=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.OUTPUT_SIZE, position)
                ),
                data_type="uint16",
            ),
            output_channels=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.OUTPUT_CHANNELS, position)
                ),
                data_type="uint16",
            ),
            hw_version=CpxBase.decode_int(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.HW_VERSION, position)
                ),
                data_type="uint8",
            ),
            fw_version=".".join(
                str(x)
                for x in self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.FW_VERSION, position)
                )
            ),
            serial_number=CpxBase.decode_hex(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.SERIAL_NUMBER, position)
                )
            ),
            product_key=CpxBase.decode_string(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.PRODUCT_KEY, position)
                )
            ),
            order_text=CpxBase.decode_string(
                self.read_reg_data(
                    *self._module_offset(cpx_ap_registers.ORDER_TEXT, position)
                )
            ),
        )
        Logging.logger.debug(f"Reading ModuleInformation: {info}")
        return info

    def write_parameter(
        self, position: int, param_id: int, instance: int, data: list | int | bool
    ) -> None:
        """Write parameters via module position, param_id, instance (=channel) and data to write
        Data must be a list of (signed) 16 bit values or one 16 bit (signed) value or bool
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :param data: list of 16 bit signed integers, one signed 16 bit integer or bool to write
        :type data: list | int | bool
        """
        if isinstance(data, list):
            registers = [CpxBase.encode_int(d)[0] for d in data]

        elif isinstance(data, int):
            registers = [CpxBase.encode_int(data)[0]]
            data = [data]  # needed for validation check

        elif isinstance(data, bool):
            registers = [CpxBase.encode_int(data, data_type="bool")[0]]
            data = [int(data)]  # needed for validation check

        else:
            raise ValueError("Data must be of type list, int or bool")

        param_reg = cpx_ap_registers.PARAMETERS.register_address

        # Strangely this sending has to be repeated several times,
        # actually it is tried up to 10 times.
        # This seems to work but it's not good
        for i in range(10):
            self.write_reg_data(position + 1, param_reg)
            self.write_reg_data(param_id, param_reg + 1)
            self.write_reg_data(instance, param_reg + 2)
            self.write_reg_data(len(registers), param_reg + 3)

            self.write_reg_data(registers, param_reg + 10, len(registers))

            self.write_reg_data(2, param_reg + 3)  # 1=read, 2=write

            exe_code = 0
            while exe_code < 16:
                exe_code = self.read_reg_data(param_reg + 3)[0]
                # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
                if exe_code == 4:
                    raise CpxRequestError

            # Validation check according to datasheet
            data_length = div_ceil(self.read_reg_data(param_reg + 4)[0], 2)
            ret = self.read_reg_data(param_reg + 10, data_length)
            ret = [CpxBase.decode_int([x], data_type="int16") for x in ret]

            if all(r == d for r, d in zip(ret, data)):
                break

        if i >= 9:
            raise CpxRequestError(
                "Parameter might not have been written correctly after 10 tries"
            )
        Logging.logger.debug(f"Wrote data {data} to module position: {position}")

    def read_parameter(self, position: int, param_id: int, instance: int) -> list[int]:
        """Read parameters via module position, param_id, instance (=channel)
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :return: Parameter data as list of int
        :rtype: list[int]
        """

        param_reg = cpx_ap_registers.PARAMETERS.register_address

        self.write_reg_data(
            position + 1, param_reg
        )  # module index starts with 1 on first module ("position" starts with 0)
        self.write_reg_data(param_id, param_reg + 1)
        self.write_reg_data(instance, param_reg + 2)

        self.write_reg_data(1, param_reg + 3)  # 1=read, 2=write

        exe_code = 0
        while exe_code < 16:
            exe_code = self.read_reg_data(param_reg + 3)[
                0
            ]  # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
            if exe_code == 4:
                raise CpxRequestError

        # data_length from register 10004 is bytewise. 2 bytes = 1 register.
        data_length = div_ceil(self.read_reg_data(param_reg + 4)[0], 2)

        data = self.read_reg_data(param_reg + 10, data_length)

        Logging.logger.debug(f"Read data {data} from module position: {position}")
        return data
