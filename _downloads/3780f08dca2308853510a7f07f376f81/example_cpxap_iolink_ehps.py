"""Example code for CPX-AP IO-Link master with gripper EHPS"""

import struct
import time

# import the libraries
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


# process data as dict
def read_process_data_in(data):
    """Read the process data and return as dict"""
    # ehps provides 3 x UIntegerT16 "process data in" according to datasheet.
    # you can unpack the data easily with stuct
    ehps_data = struct.unpack(">HHH", data)

    process_data_dict = {}

    process_data_dict["Error"] = bool((ehps_data[0] >> 15) & 1)
    process_data_dict["DirectionCloseFlag"] = bool((ehps_data[0] >> 14) & 1)
    process_data_dict["DirectionOpenFlag"] = bool((ehps_data[0] >> 13) & 1)
    process_data_dict["LatchDataOk"] = bool((ehps_data[0] >> 12) & 1)
    process_data_dict["UndefinedPositionFlag"] = bool((ehps_data[0] >> 11) & 1)
    process_data_dict["ClosedPositionFlag"] = bool((ehps_data[0] >> 10) & 1)
    process_data_dict["GrippedPositionFlag"] = bool((ehps_data[0] >> 9) & 1)
    process_data_dict["OpenedPositionFlag"] = bool((ehps_data[0] >> 8) & 1)

    process_data_dict["Ready"] = bool((ehps_data[0] >> 6) & 1)

    process_data_dict["ErrorNumber"] = ehps_data[1]
    process_data_dict["ActualPosition"] = ehps_data[2]

    return process_data_dict


# list of some connected modules. IO-Link module is specified with 8 bytes per port:
# Datasheet: Per port: 8 E / 8 A  Module: 32 E / 32 A. This has to be set up with the
# switch on the module.
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # example EHPS-20-A-LK on port 1
    EHPS_CHANNEL = 1

    # (optional) get the module and assign it to a new variable for easy access
    io_link_master = myCPX.modules[5]

    # set operating mode of channel 0 to "IO-Link communication"
    io_link_master.write_module_parameter("Port Mode", "IOL_AUTOSTART", EHPS_CHANNEL)

    time.sleep(0.05)

    # (optional) read line-state, should now be "OPERATE" for the channel
    param = io_link_master.read_fieldbus_parameters()
    while param[EHPS_CHANNEL]["Port status information"] != "OPERATE":
        param = io_link_master.read_fieldbus_parameters()

    # read process data
    raw_data = io_link_master.read_channel(EHPS_CHANNEL)

    # interpret it according to datasheet
    process_data_in = read_process_data_in(raw_data)

    # demo of process data out needed to initialize EHPS
    control_word = 0x0001  # latch
    gripping_mode = 0x46  # universal
    workpiece_no = 0x00
    gripping_position = 0x03E8
    gripping_force = 0x03  # ca. 85%
    gripping_tolerance = 0x0A

    pd_list = [
        control_word,
        gripping_mode,
        workpiece_no,
        gripping_position,
        gripping_force,
        gripping_tolerance,
    ]

    # init
    process_data_out = struct.pack(">HBBHBB", *pd_list)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    pd_list[0] = 0x0100
    process_data_out = struct.pack(">HBBHBB", *pd_list)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)

    # wait for the process data in to change to "opened"
    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(io_link_master.read_channel(EHPS_CHANNEL))
        time.sleep(0.05)

    # Close command 0x 0200
    pd_list[0] = 0x0200
    process_data_out = struct.pack(">HBBHBB", *pd_list)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)

    # wait for the process data in to change to "closed"
    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(io_link_master.read_channel(EHPS_CHANNEL))
        time.sleep(0.05)

    io_link_master.write_module_parameter("Port Mode", "DEACTIVATED", EHPS_CHANNEL)
    # wait for inactive
    param = io_link_master.read_fieldbus_parameters()
    while param[EHPS_CHANNEL]["Port status information"] != "DEACTIVATED":
        param = io_link_master.read_fieldbus_parameters()
