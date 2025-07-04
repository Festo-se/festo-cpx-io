"""cpx_io - IOThread class for handling I/O transfers in a separate thread."""

import threading
import traceback
import time
from cpx_io.utils.logging import Logging


class IOThread(threading.Thread):
    """Class to handle I/O transfers in a separate thread."""

    def __init__(self, perform_io=None, cycle_time: float = 0.01):
        """Constructor of the IOThread class.

        Parameters:
            perform_io (function): function that is called periodically (with interval cycle_time)
                                   and performs the I/O data transfer
            cycle_time (float): Cycle time that should be used for I/O transfers
        """
        self.perform_io = perform_io
        self.cycle_time = cycle_time
        self.active = False
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        """Method that needs to be implemented by child."""
        while self.active:
            try:
                self.perform_io()

            # pylint: disable=bare-except
            except:
                Logging.logger.error(traceback.format_exc())
                self.stop()

            time.sleep(self.cycle_time)

    def start(self):
        """Starts the thread."""
        self.active = True
        super().start()

    def stop(self):
        """Stops the thread."""
        self.active = False
        self.join()
