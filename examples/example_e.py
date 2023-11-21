"""Example code for CPX-E"""

# import the library
from cpx_io.cpx_system.cpx_e import (
    CpxE,
    CpxEEp,
    CpxE16Di,
    CpxE8Do,
    CpxE4AiUI,
    CpxE4AoUI,
)

# for cpx_e, the attached modules must be attached manually

modules = [CpxEEp(), CpxE16Di(), CpxE8Do(), CpxE4AiUI(), CpxE4AoUI()]

with CpxE(ip_address="172.16.1.40", modules=modules) as cpx_e:
    # modules might be added later by using add_module(module), this will return the object
    # the order of the added modules must be the same as the actual order of the modules.
    # a module can only be added to the end of the module list.
    # e8do = cpxe.add_module(CpxE8Do())

    # read system information
    module_count = cpx_e.read_module_count()
    module_list = cpx_e.modules

    # to make the reading more easy, the modules are extracted from the cpxe object and renamed

    # read digital input
    e_16di = cpx_e.cpxe16di
    one_input = e_16di.read_channel(0)  # returns bool
    all_inputs = e_16di.read_channels()  # returns list of bool

    # set digital output
    e_8do = cpx_e.cpxe8do
    e_8do.set_channel(0)  # sets one channel, returns none
    e_8do.clear_channel(0)  # clear one channel, returns none
    e_8do.toggle_channel(0)  # toggle the state of one channel, returns none
    e_8do.write_channels(
        [True, False, True, False, True, False, True, False]
    )  # sets all channel to list values [0,1,2,3,4,5,6,7] and returns none
    all_outputs = e_8do.read_channels()  # reads back all 8 channels as list of bool
    one_input = e_8do.read_channel(0)  # reads back the first input channel

    # read analog input
    e_4ai = cpx_e.cpxe4aiui
    one_input = e_4ai.read_channel(0)  # returns integer value of one channel
    all_inputs = (
        e_4ai.read_channels()
    )  # returns list of integer values for all channels [0,1,2,3]

    # write analog input
    e_4ao = cpx_e.cpxe4aoui
    e_4ao.configure_channel_range(0, "0-10V")
    e_4ao.write_channel(
        0, 500
    )  # sets the first channel to the integer value 500, returns none
    e_4ao.write_channels(
        [100, 200, 300, 400]
    )  # sets all channels to the integer values, returns none
    one_output = e_4ao.read_channel(0)  # reads back one channel
    all_outputs = e_4ao.read_channels()  # read back all channels
