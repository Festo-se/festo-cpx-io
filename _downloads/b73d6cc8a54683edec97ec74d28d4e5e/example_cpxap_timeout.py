"""Example code for cyclic access with python threading"""

import time

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


class CustomPerfomIo(CpxAp):
    """Class for error event using the internal cycle_time feature"""

    def perform_io(self):
        """Overwrite perform_io function, which is called periodically in a thread.
        It has to perform some input/output with the device in order to reset
        the modbus timeout, e.g. read_diagnostic_status()"""
        print(self.modules[1].read_channels())


# main task with acyclic access
def main():
    """main thread with acyclic access"""
    with CpxAp(ip_address="192.168.1.1", timeout=0.5, cycle_time=0.05) as myCPX:
        print(myCPX.read_diagnostic_status())
        # the modbus connection does not timeout although we wait 10 seconds
        time.sleep(2)
        print(myCPX.read_diagnostic_status())

    # It is possible to overwrite the function is called in the thread cyclicly
    with CustomPerfomIo(
        ip_address="192.168.1.1", timeout=0.5, cycle_time=0.05
    ) as myCPX:
        time.sleep(2)


if __name__ == "__main__":
    main()
