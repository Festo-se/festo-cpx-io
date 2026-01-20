"""Example code for CPX-E add module"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di
from cpx_io.cpx_system.cpx_e.e8do import CpxE8Do

with CpxE(ip_address="192.168.1.1") as myCPX:
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
    myCPX.modules[0].name = "ep_module"  # access by index
    myCPX.cpxe16di.name = "digital_input_module"  # access by name
    myCPX.cpxe8do.name = "digital_output_module"  # access by name

    # rename them again
    myCPX.modules[0].name = "my_ep_module"  # access by index
    myCPX.digital_input_module.name = "my_digital_input_module"  # access by name
    myCPX.digital_output_module.name = "my_digital_output_module"  # access by name
