"""CpxModule"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_dataclasses import SystemEntryRegisters


class CpxModule:
    """A class to connect to the Festo CPX system and read data from IO modules"""

    def __init__(self, name=None):
        self.base = None
        self.position = None

        self.system_entry_registers = SystemEntryRegisters()

        self._name = None
        self.name = name

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {type(self).__name__})"

    @property
    def name(self):
        """
        Property getter for name.
        """
        return self._name

    @name.setter
    def name(self, name_value):
        """
        Property setter for name.
        Updates base module list if base exists.
        """
        if name_value:
            self._name = name_value
        else:
            # Use class name (lower cased) as default value
            self._name = type(self).__name__.lower()

        if self.base:
            self.base.update_module_names()

    def configure(self, base: CpxBase, position: int) -> None:
        """Setup a module with the according base and position in the system

        :param base: Base module that implements the modbus functions
        :type base: CpxBase
        :param position: Module position in CPX-AP system starting with 0 for Busmodule
        :type position: int
        """
        self.base = base
        self.position = position

        # if name already exists in module list, add a counter as suffix
        module_name_list = [module.name for module in self.base.modules]
        i = 1
        temp_name = self.name
        while temp_name in module_name_list:
            temp_name = f"{self.name}_{i}"
            i += 1
        self.name = temp_name

        self.system_entry_registers.outputs = self.base.next_output_register
        self.system_entry_registers.inputs = self.base.next_input_register

        Logging.logger.debug(
            f"Configured {self} with output register {self.system_entry_registers.outputs} "
            f"and input register {self.system_entry_registers.inputs}"
        )
