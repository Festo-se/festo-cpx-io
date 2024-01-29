"""Example code for CPX-AP digital output"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # read system information
    module_count = myCPX.read_module_count()
    module_information = [myCPX.read_module_information(i) for i in range(module_count)]

    # module index 0 is 'CPX-AP-*-EP' (* can be I or A)
    # in this example the first IO module (index 1) is 'CPX-AP-*-4DI4DO-M12-5P'
    # same as with every module, you can access it by the module index or the automatically
    # generated name 'cpxap4di4do' as well as rename it (see example_cpxap_digital_input.py)

    # set, clear, toggle a digital output
    myCPX.cpxap4di4do.set_channel(0)  # sets one channel, returns none
    myCPX.cpxap4di4do.clear_channel(0)  # clear one channel, returns none
    myCPX.cpxap4di4do.toggle_channel(0)  # toggle the state of one channel, returns none

    # sets all channel to list values [0,1,2,3] and returns none
    myCPX.cpxap4di4do.write_channels([True, True, False, False])

    # read back the values of all channels. Consists of 4 input channels and 4 output channels
    myCPX.cpxap4di4do.read_channels()

    # reads back the first input channel
    myCPX.cpxap4di4do.read_channel(0)
    # reads back the first output channel, same as "read_channel(4)"
    myCPX.cpxap4di4do.read_channel(0, output_numbering=True)

    # configure the module
    # sets debounce time to 10 ms (see datasheet)
    myCPX.cpxap4di4do.configure_debounce_time(2)
    # sets Load supply monitoring inactive
    myCPX.cpxap4di4do.configure_monitoring_load_supply(0)
    # hold last state on the outputs
    myCPX.cpxap4di4do.configure_behaviour_in_fail_state(1)
