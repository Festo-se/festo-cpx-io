"""CPX-E module implementations"""

from cpx_io.utils.logging import Logging
from cpx_io.utils.helpers import module_list_from_typecode
from cpx_io.cpx_system.cpx_base import CpxBase, CpxInitError
from cpx_io.cpx_system.cpx_e import cpx_e_modbus_registers
from cpx_io.cpx_system.cpx_e.cpx_e_module_definitions import CPX_E_MODULE_ID_DICT
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.utils.boollist import bytes_to_boollist

# pylint: disable=duplicate-code
# intended: cpx_e and cpx_ap have similar, but not same functions


class CpxE(CpxBase):
    """CPX-E base class"""

    def __init__(self, modules: list = None, timeout: float = None, **kwargs):
        """Constructor of the CpxE class.

        :param modules: List of module instances e.g. [CpxEEp(), CpxE8Do(), CpxE16Di()]
        :type modules: list
        """
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13

        self.next_output_register = None
        self.next_input_register = None

        self.modules = modules

        if timeout is not None:
            self.set_timeout(int(timeout * 1000))
        else:
            Logging.logger.info(
                "Timeout is not specified. Not setting the timeout on target device."
            )

        Logging.logger.debug(f"Created {self}")

    def __repr__(self):
        return f"{type(self).__name__}: [{', '.join(str(x) for x in self.modules)}]"

    @property
    def modules(self):
        """getter function for private modules property"""
        return self._modules

    @modules.setter
    def modules(self, modules_value):
        """property setter for modules.
        Enables overwriting of modules list.
        """
        self._modules = []

        if modules_value is None:
            module_list = [CpxEEp()]
        elif isinstance(modules_value, list):
            module_list = modules_value
        elif isinstance(modules_value, str):
            Logging.logger.debug("Use typecode %s for module setup", modules_value)
            cpxe_typecode = self.unwrap_cpxe_typecode(modules_value)
            module_list = module_list_from_typecode(cpxe_typecode, CPX_E_MODULE_ID_DICT)
        else:
            raise CpxInitError

        for mod in module_list:
            self.add_module(mod)

    @staticmethod
    def unwrap_cpxe_typecode(typecode: str) -> str:
        """Takes care of the cpx-e typecode merging more than two of the same module
        type into a number. For example MMM will be merged to 3M while MM stays."""
        typecode_header = typecode[:7]
        typecode_config = typecode[7:]

        if typecode_header == "60E-EP-":
            result = ""
            i = 0
            while i < len(typecode_config):
                if typecode_config[i].isdigit():
                    num = ""
                    # look if there are following numbers
                    while i < len(typecode_config) and typecode_config[i].isdigit():
                        num += typecode_config[i]
                        i += 1
                    # if a number is found, look for the key in the dict
                    for key in CPX_E_MODULE_ID_DICT:
                        if typecode_config.startswith(key, i):
                            result += key * int(num)
                            # set i to the next index after the found key
                            i += len(key) - 1
                            break
                else:
                    result += typecode_config[i]
                i += 1
            return typecode_header + result

        raise TypeError(
            "Your CPX-E configuration must include the Ethernet/IP "
            "Busmodule to be compatible with this software"
        )

    def set_timeout(self, timeout_ms: int) -> None:
        """Sets the modbus timeout to the provided value

        :param timeout_ms: Modbus timeout in ms (milli-seconds)
        :type timeout_ms: int
        """

        if 0 < timeout_ms < 100:
            timeout_ms = 100
            Logging.logger.warning(
                f"Setting the timeout below 100 ms can lead to "
                f"exclusion from the system. To prevent this, "
                f"the timeout is limited to a minimum of {timeout_ms} ms"
            )
        Logging.logger.info(f"Setting modbus timeout to {timeout_ms} ms")
        value_to_write = timeout_ms.to_bytes(
            length=cpx_e_modbus_registers.TIMEOUT.length * 2, byteorder="little"
        )
        self.write_reg_data_with_single_cmds(
            value_to_write, cpx_e_modbus_registers.TIMEOUT.register_address
        )
        # Check if it actually succeeded
        indata = int.from_bytes(
            self.read_reg_data(*cpx_e_modbus_registers.TIMEOUT),
            byteorder="little",
            signed=False,
        )
        if indata != timeout_ms:
            Logging.logger.error("Setting of modbus timeout was not successful")

    def write_function_number(self, function_number: int, value: int) -> None:
        """Write parameters via function number

        :param function_number: Function number (see datasheet)
        :type function_number: int
        :param value: Value to write to function number
        :type value: int
        """
        value_bytes = value.to_bytes(2, byteorder="little")
        self.write_reg_data(
            value_bytes, cpx_e_modbus_registers.DATA_SYSTEM_TABLE_WRITE.register_address
        )
        # need to write 0 first because there might be an
        # old unknown configuration in the register
        self.write_reg_data(
            b"\x00\x00", cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address
        )

        write_data = (
            self._control_bit_value | self._write_bit_value | function_number
        ).to_bytes(2, byteorder="little")

        self.write_reg_data(
            write_data,
            cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = int.from_bytes(
                self.read_reg_data(*cpx_e_modbus_registers.PROCESS_DATA_INPUTS),
                byteorder="little",
            )
            its += 1

        if its >= 1000:
            raise ConnectionError()

        Logging.logger.debug(
            f"Wrote value {value} to function number {function_number}"
        )

    def read_function_number(self, function_number: int) -> int:
        """Read parameters via function number

        :param function_number: Function number (see datasheet)
        :type function_number: int
        :return: Value read from function number
        :rtype: int
        """
        # need to write 0 first because there might be an
        # old unknown configuration in the register
        self.write_reg_data(
            b"\x00\x00", cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address
        )

        write_data = (self._control_bit_value | function_number).to_bytes(
            2, byteorder="little"
        )

        self.write_reg_data(
            write_data,
            cpx_e_modbus_registers.PROCESS_DATA_OUTPUTS.register_address,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = int.from_bytes(
                self.read_reg_data(*cpx_e_modbus_registers.PROCESS_DATA_INPUTS),
                byteorder="little",
            )
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        value = int.from_bytes(
            self.read_reg_data(*cpx_e_modbus_registers.DATA_SYSTEM_TABLE_READ),
            byteorder="little",
        )

        Logging.logger.debug(
            f"Read value {value} from function number {function_number}"
        )
        return value

    def module_count(self) -> int:
        """reads the module configuration register from the system

        :returns: total module count
        :rtype: int
        """
        data = int.from_bytes(
            self.read_reg_data(*cpx_e_modbus_registers.MODULE_CONFIGURATION),
            byteorder="little",
        )
        Logging.logger.debug(f"Read {data} from MODULE_CONFIGURATION register")
        return bin(data).count("1")  # python 3.9 compatible `int.bit_count()` function

    def read_fault_detection(self) -> list[bool]:
        """reads the fault detection register from the system

        :returns: list of bools with Errors (True = Error)
        :rtype: list[bool]"""
        data = self.read_reg_data(*cpx_e_modbus_registers.FAULT_DETECTION)

        Logging.logger.debug(f"Read {data} from FAULT_DETECTION register")
        return bytes_to_boollist(data[:6], 3)

    def read_status(self) -> tuple:
        """reads the status register.

        :returns: tuple (Write-protected, Force active)
        :rtype: tuple
        """
        write_protect_bit = 11
        force_active_bit = 15
        data = self.read_reg_data(*cpx_e_modbus_registers.STATUS_REGISTER)
        Logging.logger.debug(f"Read {data} from STATUS_REGISTER register")
        data = bytes_to_boollist(data)
        return (data[write_protect_bit], data[force_active_bit])

    def read_device_identification(self) -> int:
        """reads device identification

        :returns: Objects IDO 1,2,3,4,5
        :rtype: int
        """
        data = self.read_function_number(43)
        return data

    def add_module(self, module):
        """Adds one module to the base. This is required to use the module.

        :param module: the module that should be added to the system
        """
        # we do not want to expose the configure function in the public API
        # pylint: disable=protected-access
        module._configure(self, len(self._modules))
        self._modules.append(module)
        if [type(mod) for mod in self._modules].count(CpxEEp) > 1:
            Logging.logger.warning(
                "Module CpxEEp is assigned multiple times. This is most likey incorrect."
            )
        self.update_module_names()
        Logging.logger.debug(f"Added module {module.name} ({type(module).__name__})")
        return module
