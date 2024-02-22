"""Example code for cyclic access with python threading"""

import time
import threading

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


class threadedCpx(CpxAp):
    """Class for threaded CpxAp"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # lock for modbus transmissions
        self.lock = threading.Lock()
        # error flag for error handling outside this thread
        self.status_error = threading.Event()
        self.exit_event = threading.Event()
        # start the thread
        self.continous_thread = threading.Thread(target=self.status_update)
        self.continous_thread.start()

    def __exit__(self, exc_type, exc_value, traceback):
        # exit the thread and then close the connection
        self.exit_event.set()
        return super().__exit__(exc_type, exc_value, traceback)

    def status_update(self):
        """continous thread to read faults in a cyclic access"""
        counter = 0
        while not self.exit_event.is_set():
            # lock the thread when accessing the connection
            with self.lock:
                module_status = self.read_diagnostic_status()

            if any(status.degree_of_severity_error for status in module_status):
                print(
                    f"Status Error in module(s): "
                    f"{[i for i, s in enumerate(module_status) if s.degree_of_severity_error]}"
                )
                self.status_error.set()

            time.sleep(0.05)
            # a counter to show that the thread is running
            print(counter)
            counter += 1


# main task with acyclic access
def main():
    """main thread with acyclic access"""
    with threadedCpx(ip_address="172.16.1.42") as myCPX:

        # your main application here...
        for _ in range(3):
            # acyclic communication with locking
            with myCPX.lock:
                information = myCPX.read_module_information(0)
                channels = myCPX.modules[1].read_channels()

            # error handling
            if myCPX.status_error.is_set():
                print("ERROR handling ...")

            # jobs outside the cpx access can go here so they don't block the cyclic thread
            print(information)
            print(channels)

            time.sleep(10)

    print("End of main")


if __name__ == "__main__":
    main()
