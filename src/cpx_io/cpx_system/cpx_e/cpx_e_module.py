"""CPX-E module implementation"""
from cpx_io.utils.logging import Logging


class CpxEModule:
    """Base class for cpx-e modules"""

    def __init__(self, name=None):
        # pylint: disable=duplicate-code
        # intended: cpx-ap and cpx-e have similar functions
        if name:
            self.name = name
        else:
            # Use class name (lower cased) as default value
            self.name = type(self).__name__.lower()
        self.base = None
        self.position = None

        self.output_register = None
        self.input_register = None

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {type(self).__name__})"

    def configure(self, base, position):
        """Set up module when added to cpx system

        :param base: Base module that implements the modbus functions
        :type base: CpxBase
        :param position: Module position in CPX-AP system starting with 0 for Busmodule
        :type position: int
        """
        # pylint: disable=duplicate-code
        # intended: cpx-ap and cpx-e have similar functions
        self.base = base
        self.position = position

        # if name already exists in module list, add a counter as suffix
        module_type_list = [type(module) for module in self.base.modules]
        if type(self) in module_type_list:
            self.name = f"{self.name}_{module_type_list.count(type(self))}"

        self.output_register = self.base.next_output_register
        self.input_register = self.base.next_input_register

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register} "
            f"and input register {self.input_register}"
        )
