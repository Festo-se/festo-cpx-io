"""Example code for CPX-E"""
# pylint: disable=no-member

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do

# use the typecode to setup all attached modules
with CpxE(ip_address="172.16.1.40", modules=[CpxEEp(), CpxE16Di(), CpxE8Do()]) as myCPX:
    # the modules are all named automatically and one can access them by their name or index

    # read all channels
    myCPX.cpxe16di.read_channels()
    myCPX.cpxe8do.read_channels()

    # read one channel
    myCPX.cpxe16di.read_channel(0)
    myCPX.cpxe8do.read_channel(0)

    # write all channels at once
    data = [False] * 8
    myCPX.cpxe8do.write_channels(data)

    # set and reset or toggle the state of one channel
    myCPX.cpxe8do.set_channel(0)
    myCPX.cpxe8do.clear_channel(0)
    myCPX.cpxe8do.toggle_channel(0)

    # configure the diagnostics of the module
    myCPX.cpxe8do.configure_diagnostics(short_circuit=False, undervoltage=False)
    myCPX.cpxe16di.configure_diagnostics(True)

    # configure the power reset
    myCPX.cpxe8do.configure_power_reset(True)
    myCPX.cpxe16di.configure_power_reset(True)

    # configure input debounce time
    myCPX.cpxe16di.configure_debounce_time(2)
