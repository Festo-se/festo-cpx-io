"""Example code for CPX-E IO-Link master with sensor SDAS"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol

# use the typecode to setup all attached modules
# adapt the address_space according to your setup (dip switches)
# default is 2 bytes per port
with CpxE(
    ip_address="192.168.1.1",
    modules=[CpxEEp(), CpxE4Iol()],
) as myCPX:
    # read system information
    module_list = myCPX.modules

    SDAS_CHANNEL = 0
    # set operating mode of channel 0 to "IO-Link communication"
    myCPX.cpxe4iol.configure_operating_mode(3, SDAS_CHANNEL)

    # read line-state, should now be "OPERATE"
    param = myCPX.cpxe4iol.read_line_state()

    # read the channel 0 process data
    sdas_data = myCPX.cpxe4iol.read_channel(SDAS_CHANNEL)

    # the process data consists of 4 ssc bits and 12 bit pdv (see datasheet sdas)
    # you can convert the bytes data to integer first and then do bitwise operations
    process_data_int = int.from_bytes(sdas_data, byteorder="big")
    ssc1 = bool(process_data_int & 0x1)
    ssc2 = bool(process_data_int & 0x2)
    ssc3 = bool(process_data_int & 0x4)
    ssc4 = bool(process_data_int & 0x8)
    pdv = (process_data_int & 0xFFF0) >> 4

    # you can also read the device error or other parameters
    myCPX.cpxe4iol.read_device_error(0)
