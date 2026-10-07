"""Example code for CPX-E digital input"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di

# use the typecode to setup all attached modules
with CpxE(ip_address="192.168.1.1", modules=[CpxEEp(), CpxE16Di()]) as myCPX:
    # the modules are all named automatically and one can access them by their name or index

    # read all channels
    myCPX.cpxe16di.read_channels()

    # read one channel
    myCPX.cpxe16di.read_channel(0)

    # configure the diagnostics of the module
    myCPX.cpxe16di.configure_diagnostics(True)

    # configure the power reset
    myCPX.cpxe16di.configure_power_reset(True)

    # configure input debounce time
    myCPX.cpxe16di.configure_debounce_time(2)
