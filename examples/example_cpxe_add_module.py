"""Example code for CPX-E"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do

with CpxE(ip_address="172.16.1.40") as myCPX:
    # add modules (the order must be from left to right in the cpx-e system,
    # the first module -EP is already added at position 0)
    myCPX.add_module(CpxE16Di())
    myCPX.add_module(CpxE8Do())

    # read system information
    module_list = myCPX.modules

    # the modules are all named automatically and one can access them by their name or index
    module_0 = myCPX.modules[0]  # access by index
    module_1 = myCPX.cpxe16di  # access by name (automatically generated)
    module_2 = myCPX.cpxe8do  # access by name (automatically generated)

    # rename modules
    myCPX.modules[0] = "ep_module"  # access by index
    myCPX.cpxe16di = "digital_input"  # access by name (automatically generated)
    myCPX.cpxe16di = "digital_output"  # access by name (automatically generated)
