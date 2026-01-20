# Import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


# This is your personal class. It doesn't inherit from anything!
class PersonalClass:
    # Initialize your CpxAp System and configure it with your (default) parameters
    def __init__(
        self, ip_address="192.168.1.1"
    ):  # you can pass down the arguments that you want.
        print("initialize the personal class")
        self.cpx = CpxAp(ip_address=ip_address)

    # to be used in a context manager, add the enter and exit function (leave the enter as it is)
    def __enter__(self):
        print("enter the personal class")
        return self

    # be sure to shutdown the cpx object in the exit function.
    def __exit__(self, *args):
        print("clean up CpxAp")
        # clean up everything
        self.cpx.shutdown()

    # implement your personal functions. For example a pressurize function with VTUX
    def pressurize(self, valve_number: int):
        # do some complex computation and evaluation of different
        # ap modules
        self.cpx.modules[1].set_channel(valve_number)



# Demo to show that everything works correctly
# if you run this script it will create a personal class but then raise a ZeroDivisionError.
# You can see from the prints in the console how it behaves and that the use of the context
# manager of PersonalClass is working and shutting down the cpx correctly
if __name__ == "__main__":
    # simply use the pressurize command
    with PersonalClass() as personal:
        personal.pressurize(1)

    with PersonalClass() as personal:
        i = 1 / 0
        print("This is never reached")
