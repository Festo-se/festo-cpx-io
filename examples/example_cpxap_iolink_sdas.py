"""Example code for CPX-AP io-link"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for CpxAp, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # Read the automatically generated documentation on your system folder
    # It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)

    SDAS_CHANNEL = 0
    io_link_master = myCPX.modules[4]

    # print available parameters or look at documentation
    for parameter in io_link_master.parameters.values():
        print(parameter)

    # set operating mode of channel 0 to "IO-Link communication"
    io_link_master.write_module_parameter("Port Mode", "IOL_AUTOSTART", SDAS_CHANNEL)

    # read back the port status information to check if it's "OPERATE"
    # wait for it to become "OPERATE"
    param = io_link_master.read_fieldbus_parameters()
    while param[SDAS_CHANNEL]["Port status information"] != "OPERATE":
        param = io_link_master.read_fieldbus_parameters()

    # read the channel 0 process data. This takes the device information and returns
    # only relevant bytes (2). If you want to get all bytes so you have the same length
    # for all channels, you can read all cahnnels with read_channels() or
    # read_channel(SDAS_CHANNEL, full_size=True)
    sdas_data = io_link_master.read_channel(SDAS_CHANNEL)

    # the process data consists of 4 ssc bits and 12 bit pdv (see datasheet sdas)
    # you can convert the bytes data to integer first and then do bitwise operations
    process_data_int = int.from_bytes(sdas_data, byteorder="big")
    ssc1 = bool(process_data_int & 0x1)
    ssc2 = bool(process_data_int & 0x2)
    ssc3 = bool(process_data_int & 0x4)
    ssc4 = bool(process_data_int & 0x8)
    pdv = (process_data_int & 0xFFF0) >> 4
