"""Example code for CPX-AP"""
# pylint: disable=no-member

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="172.16.1.41") as myCPX:
    # read system information
    module_count = myCPX.read_module_count()
    module_information = [myCPX.read_module_information(i) for i in range(module_count)]

    # in this example the first IO module is 'CPX-AP-I-8DI-M8-3P'

    # rename modules
    ## access by index
    myCPX.modules[0] = "myCpxApEp"
    ## access by automatically generated name
    myCPX.cpxap8di = "myCpxAp8Di"

    # read digital input
    ap_8di = myCPX.modules[1]
    myCPX.myCpxAp8Di.read_channel(0)  # returns bool
    myCPX.myCpxAp8Di.read_channels()  # returns list of bool

    # you can also set the module to a new variable (python object)
    myDi = myCPX.myCpxAp8Di

    # access functions with your object
    myDi.read_channel(1)

    # configure the module
    myDi.configure_debounce_time(3)  # 20 ms debounce time (see datasheet)
