"""Example code for CPX-E IO-Link master with gripper EHPS"""
# pylint: disable=no-member

import time

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do
from cpx_io.cpx_system.cpx_e.e4aiui import CpxE4AiUI
from cpx_io.cpx_system.cpx_e.e4aoui import CpxE4AoUI
from cpx_io.cpx_system.cpx_e.e4iol import CpxE4Iol


# process data as dict
def read_process_data_in(data):
    """Read the process data and return as dict"""
    # ehps provides 3 x 16bit "process data in".

    _process_data_in = {}

    _process_data_in["Error"] = bool((data[0] >> 15) & 1)
    _process_data_in["DirectionCloseFlag"] = bool((data[0] >> 14) & 1)
    _process_data_in["DirectionOpenFlag"] = bool((data[0] >> 13) & 1)
    _process_data_in["LatchDataOk"] = bool((data[0] >> 12) & 1)
    _process_data_in["UndefinedPositionFlag"] = bool((data[0] >> 11) & 1)
    _process_data_in["ClosedPositionFlag"] = bool((data[0] >> 10) & 1)
    _process_data_in["GrippedPositionFlag"] = bool((data[0] >> 9) & 1)
    _process_data_in["OpenedPositionFlag"] = bool((data[0] >> 8) & 1)

    _process_data_in["Ready"] = bool((data[0] >> 6) & 1)

    _process_data_in["ErrorNumber"] = data[1]
    _process_data_in["ActualPosition"] = data[2]

    return _process_data_in


# list of some connected modules. IO-Link module is specified with 8 bytes per port:
# Datasheet: Per port: 8 E / 8 A  Module: 32 E / 32 A. This has to be set up with the
# switch on the module.
with CpxE(
    ip_address="172.16.1.40",
    modules=[CpxEEp(), CpxE16Di(), CpxE8Do(), CpxE4AiUI(), CpxE4AoUI(), CpxE4Iol(8)],
) as myCPX:
    # read system information
    module_list = myCPX.modules

    # example EHPS-20-A-LK on port 1
    ehps_channel = 1

    # set operating mode of channel 0 to "IO-Link communication"
    myCPX.cpxe4iol.configure_operating_mode(3, channel=ehps_channel)

    time.sleep(0.05)

    # read line-state, should now be "OPERATE"
    param = myCPX.cpxe4iol.read_line_state()

    # read process data
    raw_data = myCPX.cpxe4iol.read_channel(ehps_channel)

    # interpret it according to datasheet
    process_data_in = read_process_data_in(raw_data)

    # demo of process data out
    control_word_msb = 0x00
    control_word_lsb = 0x01  # latch
    gripping_mode = 0x46  # universal
    workpiece_no = 0x00
    gripping_position = 0x03E8
    gripping_force = 0x03  # ca. 85%
    gripping_tolerance = 0x0A

    process_data_out = [
        control_word_lsb + (control_word_msb << 8),
        workpiece_no + (gripping_mode << 8),
        gripping_position,
        gripping_tolerance + (gripping_force << 8),
    ]

    # init
    myCPX.cpxe4iol.write_channel(ehps_channel, process_data_out)
    time.sleep(0.05)

    # Open command: 0x0100
    process_data_out[0] = 0x0100
    myCPX.cpxe4iol.write_channel(ehps_channel, process_data_out)

    # wait for the process data in to change to "opened"
    while not process_data_in["OpenedPositionFlag"]:
        process_data_in = read_process_data_in(
            myCPX.cpxe4iol.read_channel(ehps_channel)
        )
        time.sleep(0.05)

    # Close command 0x 0200
    process_data_out[0] = 0x0200
    myCPX.cpxe4iol.write_channel(ehps_channel, process_data_out)

    # wait for the process data in to change to "closed"
    while not process_data_in["ClosedPositionFlag"]:
        process_data_in = read_process_data_in(
            myCPX.cpxe4iol.read_channel(ehps_channel)
        )
        time.sleep(0.05)
