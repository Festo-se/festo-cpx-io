"""Example code for CPX-AP io-link"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for CpxAp, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # read system information
    module_count = myCPX.read_module_count()
    module_information = [myCPX.read_module_information(i) for i in range(module_count)]

    SDAS_CHANNEL = 0
    # set operating mode of channel 0 to "IO-Link communication"
    myCPX.cpxap4iol.configure_port_mode(2, SDAS_CHANNEL)

    # read back the port status information to check if it's "OPERATE"
    param = myCPX.cpxap4iol.read_fieldbus_parameters()
    assert param[SDAS_CHANNEL]["Port status information"] == "OPERATE"

    # read the channel 0 process data. This takes the device information and returns
    # only relevant bytes (2). If you want to get all bytes so you have the same length
    # for all channels, you can read all cahnnels with read_channels() or
    # read_channel(SDAS_CHANNLE, full_size=True)
    sdas_data = myCPX.cpxap4iol.read_channel(SDAS_CHANNEL)

    # the process data consists of 4 ssc bits and 12 bit pdv (see datasheet sdas)
    # you can convert the bytes data to integer first and then do bitwise operations
    process_data_int = int.from_bytes(process_data, byteorder="big")
    ssc1 = bool(process_data_int & 0x1)
    ssc2 = bool(process_data_int & 0x2)
    ssc3 = bool(process_data_int & 0x4)
    ssc4 = bool(process_data_int & 0x8)
    pdv = (process_data_int & 0xFFF0) >> 4
