"""Example code for CPX-E with list of modules"""

# import the librarys
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE
from cpx_io.cpx_system.cpx_e.eep import CpxEEp
from cpx_io.cpx_system.cpx_e.e16di import CpxE16Di

# use list of modules to call CpxE
modules = [CpxEEp(), CpxE16Di()]

with CpxE(ip_address="192.168.1.1", modules=modules) as myCPX:
    # read system information
    module_list = myCPX.modules

    # the modules are all named automatically and one can access them by their name or index
    module_0 = myCPX.modules[0]  # access by index
    module_1 = myCPX.cpxe16di  # access by name (automatically generated)

    # rename modules (also see example_cpxe_add_module.py)
    myCPX.modules[0].name = "ep_module"  # access by index
    myCPX.cpxe16di.name = "digital_input_module"  # access by name
