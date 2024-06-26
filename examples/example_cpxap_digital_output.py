"""Example code for CPX-AP digital output"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # Read the automatically generated documentation on your system folder
    # It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)

    # module index 0 is 'CPX-AP-*-EP' (* can be I or A)
    # in this example the first IO module (index 1) is 'CPX-AP-*-4DI4DO-M12-5P'
    # same as with every module, you can access it by the module index or the automatically
    # generated name (get it from documentation) as well as rename it (see digital_input example)

    dido = myCPX.modules[1]
    # set, clear, toggle a digital output
    dido.set_channel(0)  # sets one channel, returns none
    dido.clear_channel(0)  # clear one channel, returns none
    dido.toggle_channel(0)  # toggle the state of one channel, returns none

    # sets all channel to list values [0,1,2,3] and returns none
    dido.write_channels([True, True, False, False])

    # read back the values of all channels. Consists of 4 input channels and 4 output channels
    dido.read_channels()

    # reads back the first input channel
    dido.read_channel(0)
    # reads back the first output channel, same as "read_channel(4)"
    dido.read_channel(0, outputs_only=True)

    # configure the module. Check what parameters are available in the documentation or read
    # them from the module (see parameter_read_write example)
    for parameter in dido.parameter_dict.values():
        print(parameter)

    # sets debounce time to 10ms
    dido.write_module_parameter("Input Debounce Time", "10ms")
    # sets Load supply monitoring inactive, you can access also by ID (is a bit faster than name)
    dido.write_module_parameter(20022, "Load supply monitoring inactive")
    # hold last state on the outputs, you can also set it by the integer value instead of the enum
    dido.write_module_parameter(20052, 1)
