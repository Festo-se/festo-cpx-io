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

    # keep in mind that the outputs will switch on and off as fast as your pc allows. It is very
    # likely, that you will not see any change on the outputs before the code runs through and
    # the connection is closed. If you actually want to see something in this example, I suggest
    # using the sleep function from the time module to wait. Keep in mind that this will only work
    # if you disable the modbus timeout by passing timeout=0 in the CpxAp constructor.

    # set, reset, toggle a digital output
    dido.set_channel(0)  # sets one channel, returns none
    dido.reset_channel(0)  # reset one channel, returns none
    dido.toggle_channel(0)  # toggle the state of one channel, returns none

    # sets all channel to list values [0,1,2,3] and returns none
    dido.write_channels([True, True, False, False])

    # read back the values of all channels. Consists of 4 input channels and 4 output channels
    dido.read_channels()

    # reads back the first input channel
    dido.read_channel(0)
    # reads back the first output channel, same as "read_channel(4)"
    dido.read_output_channel(0)

    # configure the module. Check what parameters are available in the documentation or read
    # them from the module (see parameter_read_write example)
    for parameter in dido.module_dicts.parameters.values():
        print(parameter)

    # sets debounce time to 10ms
    dido.write_module_parameter("Input Debounce Time", "10ms")
    # sets Load supply monitoring inactive, you can access also by ID (is a bit faster than name)
    dido.write_module_parameter(20022, "Load supply monitoring inactive")
    # hold last state on the outputs, you can also set it by the integer value instead of the enum
    dido.write_module_parameter(20052, 1)
