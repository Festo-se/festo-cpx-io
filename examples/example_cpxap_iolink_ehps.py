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
    ehps_data = struct.unpack(">HHHH", data)
    # the last 16 bit value of this list is always 0 since ehps only uses 3*16 bit
    assert ehps_data[3] == 0

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
    io_link_master = myCPX.modules[4]

    # (optional) you can reset the power for each channel
    io_link_master.configure_pl_supply(False, EHPS_CHANNEL)
    io_link_master.configure_ps_supply(False)
    time.sleep(0.05)
    io_link_master.configure_pl_supply(True, EHPS_CHANNEL)
    io_link_master.configure_ps_supply(True)
    time.sleep(0.05)

    # set operating mode of channel 0 to "IO-Link communication"
    io_link_master.configure_operating_mode(3, channel=EHPS_CHANNEL)

    time.sleep(0.05)

    # (optional) read line-state, should now be "OPERATE" for the channel
    param = io_link_master.read_line_state()

    # read process data
    raw_data = io_link_master.read_channel(EHPS_CHANNEL)

    # interpret it according to datasheet
    process_data_in = read_process_data_in(raw_data)

    # demo of process data out needed to initialize EHPS
    control_word_msb = 0x00
    control_word_lsb = 0x01  # latch
    gripping_mode = 0x46  # universal
    workpiece_no = 0x00
    gripping_position = 0x03E8
    gripping_force = 0x03  # ca. 85%
    gripping_tolerance = 0x0A

    data = [
        control_word_lsb + (control_word_msb << 8),
        workpiece_no + (gripping_mode << 8),
        gripping_position,
        gripping_tolerance + (gripping_force << 8),
    ]

    # init
    # pack the 4*16bit values to bytes
    process_data_out = struct.pack(">HHHH", *data)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    process_data_out[0] = 0x0100
    process_data_out = struct.pack(">HHHH", *data)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)

    # wait for the process data in to change to "opened"
    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(io_link_master.read_channel(EHPS_CHANNEL))
        time.sleep(0.05)

    # Close command 0x 0200
    process_data_out[0] = 0x0200
    process_data_out = struct.pack(">HHHH", *data)
    io_link_master.write_channel(EHPS_CHANNEL, process_data_out)

    # wait for the process data in to change to "closed"
    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(io_link_master.read_channel(EHPS_CHANNEL))
        time.sleep(0.05)
