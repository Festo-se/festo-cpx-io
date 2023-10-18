__author__ = "Wiesner, Martin"
__copyright__ = "Copyright 2022, Festo"
__credits__ = [""]
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Wiesner, Martin"
__email__ = "martin.wiesner@festo.com"
__status__ = "Development"


import logging

from cpx_base import CPX_BASE


class CPX_E(CPX_BASE):

    def __init__(self):
        # TODO: Is this really neccessary?
        try:
            self.client.write_register(46100, 0)

        except Exception as e:
            print("Incorrect Modbus configuration : ", str(e))


    def writeData(self, register, data):
        """Todo

        """
        try:
            self.client.write_register(register, data)
        except Exception as e:
            print("Error while writing: ", str(e))

    def writeMultipleData(self, register, data):
        """Todo

        """
        try:
            self.client.write_registers(register, data)
        except Exception as e:
            print("Error while writing: ", str(e))
  

    def writeOutputRegData(self, register, data):
        """Todo

        """
        return self.writeData(register, data)

    def writeOutputMultiRegData(self, register, data):
        """Todo

        """
        return self.writeMultipleData(register, data)

    def __del__(self):
        self.client.close()
        logging.info("Disconnected")
