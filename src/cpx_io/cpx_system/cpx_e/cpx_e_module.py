"""CPX-E module implementation"""
from cpx_io.utils.logging import Logging


class CpxEModule:
    """Base class for cpx-e modules"""

    def __init__(self, name=None):
        self.base = None
        self.position = None

        self.output_register = None
        self.input_register = None
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

    # pylint: disable=duplicate-code
    # intended: cpx-ap and cpx-e have similar functions
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

    def configure(self, base, position):
        """Set up module when added to cpx system"""
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
