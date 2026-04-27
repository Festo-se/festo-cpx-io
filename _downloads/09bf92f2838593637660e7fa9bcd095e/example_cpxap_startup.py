"""Example code for CPX-AP startup and system information"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # view the system documentation by going to the apdd path on your system directory
    # this documentation is updated everytime the CpxAp Object with this ip address is
    # instanciated. It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)

    # alternatively you can print out the system information in the console
    myCPX.print_system_information()

    # to get an overview of all available parameters, there is a function that iterates
    # over every module and reads out the parameters and channels if available
    myCPX.print_system_state()
