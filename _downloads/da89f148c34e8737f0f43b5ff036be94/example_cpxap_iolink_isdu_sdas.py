"""Example code for CPX-AP io-link isdu access"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for CpxAp, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # Read the automatically generated documentation on your system folder
    # It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)

    SDAS_CHANNEL = 0
    io_link_master = myCPX.modules[4]

    # setup the master for communication (see example_cpxap_iolink_sdas)
    io_link_master.write_module_parameter("Port Mode", "IOL_AUTOSTART", SDAS_CHANNEL)

    param = io_link_master.read_fieldbus_parameters()
    while param[SDAS_CHANNEL]["Port status information"] != "OPERATE":
        param = io_link_master.read_fieldbus_parameters()

    # Read raw isdu value into a single channel as parameter
    ret = io_link_master.read_isdu(SDAS_CHANNEL, 0x0010)  # subindex is optional
    # without specifying the data_type, this returns a list with a bytes object. Since in
    # io-Link strings are encoded "msb first", no change is required in decoding.
    # For example:
    print(ret.decode("ascii"))

    # Read isdu with data_type defined with channel in a list
    ret = io_link_master.read_isdu([SDAS_CHANNEL], 0x0010, data_type="str")
    # If you know the expected datatype, you can specify it and get the isdu data
    # interpreted correctly. ret will now be a python str type.
    print(ret)

    # Write isdu raw (bytes) into a single channel as parameter
    io_link_master.write_isdu(b"FESTO", SDAS_CHANNEL, 0x0018)
    # this will write b"FESTO" to the isdu, can be read back with:
    ret = io_link_master.read_isdu(SDAS_CHANNEL, 0x0018)
    print(ret.decode("ascii"))

    # Write isdu with datatype defined with channel in a list
    io_link_master.write_isdu("FESTO", [SDAS_CHANNEL], 0x0018)
    # this will write a string "FESTO" to the isdu with correct interpretation of the
    # datatype. This can be read back with:
    ret = io_link_master.read_isdu([SDAS_CHANNEL], 0x0018, data_type="str")
    print(ret)
