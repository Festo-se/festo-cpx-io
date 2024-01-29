"""Example code for CPX-E with typecode"""

# import the library
from cpx_io.cpx_system.cpx_e.cpx_e import CpxE

# use the typecode to setup all attached modules
with CpxE("60E-EP-MLNINO", ip_address="192.168.1.1") as myCPX:
    # read system information
    module_list = myCPX.modules

    # the modules are all named automatically and one can access them by their name or index
    module_0 = myCPX.modules[0]  # access by index
    module_1 = myCPX.cpxe8do  # access by name (automatically generated)

    # rename modules
    myCPX.modules[0] = "ep_module"  # access by index
    myCPX.cpxe8do = "digital_output"  # access by name (automatically generated)
