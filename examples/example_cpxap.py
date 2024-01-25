"""Example code for CPX-AP"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="172.16.1.41") as myCPX:
    # read system information
    module_count = myCPX.read_module_count()
    module_information = [myCPX.read_module_information(i) for i in range(module_count)]

    # in this example the first IO module is 'CPX-AP-I-8DI-M8-3P'
    # read digital input
    ap_8di = myCPX.modules[1]
    myCPX.cpxap8di.read_channel(0)  # returns bool
    myCPX.cpxap8di.read_channels()  # returns list of bool

    # the second module is 'CPX-AP-I-4DI4DO-M12-5P'
    # set digital output
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

    # third module is 'CPX-AP-I-4AI-U-I-RTD-M12'
    # configure the channel range
    myCPX.cpxap4aiui.configure_channel_range(0, "0-10V")
    # read analog input
    myCPX.cpxap4aiui.read_channel(0)  # returns integer value of one channel
    # returns list of integer values for all channels [0,1,2,3]
    myCPX.cpxap4aiui.read_channels()
