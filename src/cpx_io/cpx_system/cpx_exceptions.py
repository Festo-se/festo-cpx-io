__author__ = "Wiesner, Martin"
__copyright__ = "Copyright 2023, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Wiesner, Martin"
__email__ = "martin.wiesner@festo.com"
__status__ = "Development"


class UnknownTypeError(Exception):
    def __init__(self, message="Unknown Type Error"):
        super().__init__(message)

class UnknownModuleError(Exception):
    def __init__(self, message="Unknown Module Error"):
        super().__init__(message)

class ReadFailedError(Exception):
    def __init__(self, message="Read Failed Error"):
        super().__init__(message)
'''
class WriteFailedError(Exception):
    def __init__(self, message="Write Failed Error"):
        super().__init__(message)
'''