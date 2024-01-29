"""Example code for CPX-AP digital input"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # read system information
    module_count = myCPX.read_module_count()
    module_information = [myCPX.read_module_information(i) for i in range(module_count)]

    # module index 0 is 'CPX-AP-I-EP'
    # in this example the first IO module (index 1) is 'CPX-AP-I-8DI-M8-3P'

    # read digital input on channel 0
    # access by index
    myCPX.modules[1].read_channel(0)
    # or access by automatically generated name
    myCPX.cpxap8di.read_channel(0)

    # you can also assign it to a custom object
    myIO = myCPX.modules[1]
    myIO.read_channel(0)

    # you can also rename the module and access it by its new name
    myCPX.cpxap8di.name = "my8di"
    myCPX.my8di.read_channel(0)

    # you can read all channels at once, this returns a list of bool
    myIO.read_channels()

    # configure the module
    myIO.configure_debounce_time(3)  # 20 ms debounce time (see datasheet)
