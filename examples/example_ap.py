"""Example code for CPX-AP"""

# import the library
from cpx_io.cpx_system.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="172.16.1.41") as cpx_ap:
    # read system information
    module_count = cpx_ap.read_module_count()
    module_information = [
        cpx_ap.read_module_information(i) for i in range(module_count)
    ]

    # to make the reading more easy, the modules are extracted from the cpxap object and renamed

    # in this example the first IO module is 'CPX-AP-I-8DI-M8-3P'
    # read digital input
    ap_8di = cpx_ap.modules[1]
    one_input = ap_8di.read_channel(0)  # returns bool
    all_inputs = ap_8di.read_channels()  # returns list of bool

    # the second module is 'CPX-AP-I-4DI4DO-M12-5P'
    # set digital output
    ap_4di4do = cpx_ap.modules[2]
    ap_4di4do.set_channel(0)  # sets one channel, returns none
    ap_4di4do.clear_channel(0)  # clear one channel, returns none
    ap_4di4do.toggle_channel(0)  # toggle the state of one channel, returns none
    ap_4di4do.write_channels(
        [True, True, False, False]
    )  # sets all channel to list values [0,1,2,3] and returns none
    all_io = (
        ap_4di4do.read_channels()
    )  # read back the values of all channels. Consists of 4 input channels and 4 output channels
    one_input = ap_4di4do.read_channel(0)  # reads back the first input channel
    one_output = ap_4di4do.read_channel(
        0, output_numbering=True
    )  # reads back the first output channel, same as "read_channel(4)"

    # third module is 'CPX-AP-I-4AI-U-I-RTD-M12'
    # read analog input
    ap_4ai = cpx_ap.modules[3]
    ap_4ai.configure_channel_range(0, "0-10V")
    one_input = ap_4ai.read_channel(0)  # returns integer value of one channel
    all_inputs = (
        ap_4ai.read_channels()
    )  # returns list of integer values for all channels [0,1,2,3]
