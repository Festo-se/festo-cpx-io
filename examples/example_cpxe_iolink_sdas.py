"""Example code for CPX-E IO-Link master with sensor SDAS"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol

# use the typecode to setup all attached modules
with CpxE(
    ip_address="172.16.1.40",
    modules=[CpxEEp(), CpxE16Di(), CpxE8Do(), CpxE4AiUI(), CpxE4AoUI(), CpxE4Iol()],
) as myCPX:
    # read system information
    module_list = myCPX.modules

    # set operating mode of channel 0 to "IO-Link communication"
    myCPX.cpxe4iol.configure_operating_mode(3, 0)

    # read the channel 0 process data
    sdas_data = myCPX.cpxe4iol.read_channel(0)

    # sdas only requires 2 bytes, so the first 16 bit value from the list is taken
    process_data = sdas_data[0]

    # the process data consists of 4 ssc bits and 12 bit pdv (see datasheet sdas)
    ssc1 = bool(process_data & 0x1)
    ssc2 = bool(process_data & 0x2)
    ssc3 = bool(process_data & 0x4)
    ssc4 = bool(process_data & 0x8)
    pdv = (process_data & 0xFFF0) >> 4

    # you can also read the device error or other parameters
    myCPX.cpxe4iol.read_device_error(0)
