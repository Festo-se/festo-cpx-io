"""CPX-E module implementation"""
from cpx_io.utils.logging import Logging


class CpxEModule:
    """Base class for cpx-e modules"""

    def __init__(self, name=None):
        # pylint: disable=duplicate-code
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
        """Set up postion and base for the module when added to cpx system"""
        self.base = base
        self.position = position

        self.output_register = self.base.next_output_register
        self.input_register = self.base.next_input_register

        Logging.logger.debug(
            f"Configured {self} with output register {self.output_register} "
            f"and input register {self.input_register}"
        )
