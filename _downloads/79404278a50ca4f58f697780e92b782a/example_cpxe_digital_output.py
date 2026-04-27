"""Example code for CPX-E digital output"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do

# use the typecode to setup all attached modules
with CpxE(ip_address="192.168.1.1", modules=[CpxEEp(), CpxE8Do()]) as myCPX:
    # the modules are all named automatically and one can access them by their name or index

    # read all channels
    myCPX.cpxe8do.read_channels()

    # read one channel
    myCPX.cpxe8do.read_channel(0)

    # write all channels at once
    data = [False] * 8
    myCPX.cpxe8do.write_channels(data)

    # set and reset or toggle the state of one channel
    myCPX.cpxe8do.set_channel(0)
    myCPX.cpxe8do.reset_channel(0)
    myCPX.cpxe8do.toggle_channel(0)

    # configure the diagnostics of the module
    myCPX.cpxe8do.configure_diagnostics(short_circuit=False, undervoltage=False)

    # configure the power reset
    myCPX.cpxe8do.configure_power_reset(True)
