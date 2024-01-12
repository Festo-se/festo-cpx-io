"""CPX-E module implementations"""

from cpx_io.utils.logging import Logging
from cpx_io.utils.helpers import module_list_from_typecode
from cpx_io.cpx_system.cpx_base import CpxBase, CpxInitError
from cpx_io.cpx_system.cpx_e import cpx_e_registers
from cpx_io.cpx_system.cpx_e.cpx_e_module_definitions import CPX_E_MODULE_ID_DICT
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.utils.boollist import int_to_boollist


class CpxE(CpxBase):
    """CPX-E base class"""

    def __init__(self, modules=None, **kwargs):
        super().__init__(**kwargs)
        self._control_bit_value = 1 << 15
        self._write_bit_value = 1 << 13

        self.next_output_register = None
        self.next_input_register = None
        self._modules = []

        self.modules = modules

        Logging.logger.info(f"Created {self}")

    def __repr__(self):
        return f"{type(self).__name__}: [{', '.join(str(x) for x in self.modules)}]"

    @property
    def modules(self):
        """Property getter for modules"""
        return self._modules

    @modules.setter
    def modules(self, modules_value):
        """
        Property setter for modules.
        Enables overwriting of modules list.
        """
        for mod in self._modules:
            delattr(self, mod.name)
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
        """Write parameters via function number"""
        self.write_reg_data(value, *cpx_e_registers.DATA_SYSTEM_TABLE_WRITE)
        # need to write 0 first because there might be an
        # old unknown configuration in the register
        self.write_reg_data(0, *cpx_e_registers.PROCESS_DATA_OUTPUTS)
        self.write_reg_data(
            self._control_bit_value | self._write_bit_value | function_number,
            *cpx_e_registers.PROCESS_DATA_OUTPUTS,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.read_reg_data(*cpx_e_registers.PROCESS_DATA_INPUTS)[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

    def read_function_number(self, function_number: int) -> int:
        """Read parameters via function number"""
        # need to write 0 first because there might be an
        # old unknown configuration in the register
        self.write_reg_data(0, *cpx_e_registers.PROCESS_DATA_OUTPUTS)
        self.write_reg_data(
            self._control_bit_value | function_number,
            *cpx_e_registers.PROCESS_DATA_OUTPUTS,
        )

        data = 0
        its = 0
        while (data & self._control_bit_value) == 0 and its < 1000:
            data = self.read_reg_data(*cpx_e_registers.PROCESS_DATA_INPUTS)[0]
            its += 1

        if its >= 1000:
            raise ConnectionError()

        data &= ~self._control_bit_value
        value = self.read_reg_data(*cpx_e_registers.DATA_SYSTEM_TABLE_READ)
        return value[0]

    def module_count(self) -> int:
        """returns the total count of attached modules"""
        data = self.read_reg_data(*cpx_e_registers.MODULE_CONFIGURATION)
        return sum(d.bit_count() for d in data)

    def fault_detection(self) -> list[bool]:
        """returns list of bools with Errors (True = Error)"""
        ret = self.read_reg_data(*cpx_e_registers.FAULT_DETECTION)
        data = ret[2] << 16 | ret[1] << 8 | ret[0]
        return int_to_boollist(data, 3)

    def status_register(self) -> tuple:
        """returns (Write-protected, Force active)"""
        write_protect_bit = 1 << 11
        force_active_bit = 1 << 15
        data = self.read_reg_data(*cpx_e_registers.STATUS_REGISTER)
        return (bool(data[0] & write_protect_bit), bool(data[0] & force_active_bit))

    def read_device_identification(self) -> int:
        """returns Objects IDO 1,2,3,4,5"""
        data = self.read_function_number(43)
        return data

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer"""
        return len(self._modules)

    def add_module(self, module):
        """Adds one module to the base. This is required to use the module."""
        module.configure(self, len(self._modules))
        self._modules.append(module)
        if [type(mod) for mod in self._modules].count(CpxEEp) > 1:
            Logging.logger.warning(
                "Module CpxEEp is assigned multiple times. This is most likey incorrect."
            )
        setattr(self, module.name, module)
        Logging.logger.debug("Added module %s (%s)", module.name, type(module).__name__)
        return module
