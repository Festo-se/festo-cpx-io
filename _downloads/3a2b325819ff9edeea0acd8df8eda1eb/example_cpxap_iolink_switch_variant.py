"""Example code for CPX-AP IO-Link master variant switch"""

import struct
import time

# import the libraries
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp


with CpxAp(ip_address="192.168.1.1") as myCPX:
    print(myCPX.modules[5])
    # (optional) get the module and assign it to a new variable for easy access
    io_link_master = myCPX.modules[5]
    io_link_master.change_variant("CPX-AP-I-4IOL-M12 Variant 16")
    # alternatively, change by module code
    # io_link_master.change_variant(8210)
# We have to reinitialize the myCPX object to update the system information and new
# process data length
with CpxAp(ip_address="192.168.1.1") as myCPX:
    print(myCPX.modules[5])
    io_link_master = myCPX.modules[5]
    # now we can use the new variant of the IO-Link master
    io_link_master.write_module_parameter("Port Mode", "IOL_AUTOSTART", 1)
