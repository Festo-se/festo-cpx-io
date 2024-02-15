"""CPX-E module implementations"""

from cpx_io.utils.logging import Logging
from cpx_io.utils.helpers import module_list_from_typecode
from cpx_io.cpx_system.cpx_base import CpxBase, CpxInitError
from cpx_io.cpx_system.cpx_e import cpx_e_registers
from cpx_io.cpx_system.cpx_e.cpx_e_module_definitions import CPX_E_MODULE_ID_DICT
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.utils.boollist import bytes_to_boollist


class CpxE(CpxBase):
    """CPX-E base class"""

    def __init__(self, modules=None, **kwargs):
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

        Logging.logger.info(f"Created {self}")

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
            Logging.logger.info("Use typecode %s for module setup", modules_value)
            module_list = module_list_from_typecode(modules_value, CPX_E_MODULE_ID_DICT)
        else:
            raise CpxInitError

        for mod in module_list:
            self.add_module(mod)

    def write_function_number(self, function_number: int, value: int) -> None:
        """Write parameters via function number

        :param function_number: Function number (see datasheet)
        :type function_number: int
        :param value: Value to write to function number
        :type value: int
        """
        value_bytes = value.to_bytes(2, byteorder="little")
        self.write_reg_data(
            value_bytes, cpx_e_registers.DATA_SYSTEM_TABLE_WRITE.register_address
        )
        # need to write 0 first because there might be an
        # old unknown configuration in the register
        self.write_reg_data(
            b"\x00\x00", cpx_e_registers.PROCESS_DATA_OUTPUTS.register_address
        )

        write_data = (
            self._control_bit_value | self._write_bit_value | function_number
        ).to_bytes(2, byteorder="little")

        self.write_reg_data(
            write_data,
            cpx_e_registers.PROCESS_DATA_OUTPUTS.register_address,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = int.from_bytes(
                self.read_reg_data(*cpx_e_registers.PROCESS_DATA_INPUTS),
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
            b"\x00\x00", cpx_e_registers.PROCESS_DATA_OUTPUTS.register_address
        )

        write_data = (self._control_bit_value | function_number).to_bytes(
            2, byteorder="little"
        )

        self.write_reg_data(
            write_data,
            cpx_e_registers.PROCESS_DATA_OUTPUTS.register_address,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = int.from_bytes(
                self.read_reg_data(*cpx_e_registers.PROCESS_DATA_INPUTS),
                byteorder="little",
            )
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        value = int.from_bytes(
            self.read_reg_data(*cpx_e_registers.DATA_SYSTEM_TABLE_READ),
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
            self.read_reg_data(*cpx_e_registers.MODULE_CONFIGURATION),
            byteorder="little",
        )
        Logging.logger.debug(f"Read {data} from MODULE_CONFIGURATION register")
        return data.bit_count()

    def read_fault_detection(self) -> list[bool]:
        """reads the fault detection register from the system

        :returns: list of bools with Errors (True = Error)
        :rtype: list[bool]"""
        data = self.read_reg_data(*cpx_e_registers.FAULT_DETECTION)

        Logging.logger.debug(f"Read {data} from FAULT_DETECTION register")
        return bytes_to_boollist(data[:6], 3)

    def read_status(self) -> tuple:
        """reads the status register.

        :returns: tuple (Write-protected, Force active)
        :rtype: tuple
        """
        write_protect_bit = 11
        force_active_bit = 15
        data = self.read_reg_data(*cpx_e_registers.STATUS_REGISTER)
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
        module.configure(self, len(self._modules))
        self._modules.append(module)
        if [type(mod) for mod in self._modules].count(CpxEEp) > 1:
            Logging.logger.warning(
                "Module CpxEEp is assigned multiple times. This is most likey incorrect."
            )
        self.update_module_names()
        Logging.logger.debug(f"Added module {module.name} ({type(module).__name__})")
        return module
