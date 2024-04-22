"""Example code for CPX-AP digital input"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # Read the automatically generated documentation on your system folder
    # It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)

    # module index 0 is 'CPX-AP-*-EP' (* can be I or A)
    # The first IO module (index 1) is 'CPX-AP-I-8DI-M8-3P'

    # read digital input on channel 0
    # access by index
    myCPX.modules[1].read_channel(0)

    # or access by automatically generated name, you can see the default names
    # in the documentation but you can rename the modules anytime you like
    myCPX.modules[1].name = "cpxap8di"
    myCPX.cpxap8di.read_channel(0)

    # you can also assign it to a custom object
    myIO = myCPX.modules[1]
    myIO.read_channel(0)

    # you can read all channels at once, this returns a list of bool
    myIO.read_channels()

    # configure the module
    # you can read/write the parameters from the module. Check the parameter_read_write example
    # for detailed information. The Input Debounce Time parameter will return an enum string.
    debounce_time = myIO.read_module_parameter("Input Debounce Time")
