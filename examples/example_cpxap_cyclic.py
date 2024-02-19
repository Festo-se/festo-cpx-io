"""Example code for cyclic access with python threading"""

import time
import threading

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# global error flag
status_error = threading.Event()

# lock for modbus transmissions
transmission_lock = threading.Lock()

IP_ADDRESS = "192.168.1.1"


def continous_status_update():
    """continous thread to read faults in a cyclic access"""
    while True:
        with transmission_lock:

            # initialize the connection
            with CpxAp(ip_address=IP_ADDRESS) as myCPX:

                # read the status information for every module
                module_status = myCPX.read_diagnostic_status()

        if any(status.degree_of_severity_error for status in module_status):
            print(
                f"Status Error in module(s): "
                f"{[i for i, s in enumerate(module_status) if s.degree_of_severity_error]}"
            )
            status_error.set()


# second thread with acyclic access
def main():
    """main thread with acyclic access"""
    while True:
        with transmission_lock:

            # initialize the connection
            # since this connection is established new every loop, lost modules are
            # reconnected automatically. But you can always terminate if an error exists
            # or do something else with the status_error information
            with CpxAp(ip_address=IP_ADDRESS) as myCPX:
                if status_error.is_set():
                    # do Error handling here
                    pass

                # do acyclic jobs
                information = myCPX.read_module_information(0)
                print(information)

        # jobs outside the cpx access can go here so they don't block the cyclic thread
        time.sleep(10)


if __name__ == "__main__":
    # Create threads
    continous_status_update = threading.Thread(target=continous_status_update)
    main = threading.Thread(target=main)

    # Start threads
    continous_status_update.start()
    main.start()
