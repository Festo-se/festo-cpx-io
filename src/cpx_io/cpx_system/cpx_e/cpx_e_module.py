"""CPX-E module implementation"""


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
