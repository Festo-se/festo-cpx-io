"""Test program that needs to be deleted for production"""

import time
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="172.16.1.41", timeout=1) as cpxap:
    IDX = 3
    PARAM = 20043
    # print("Modules: ", cpxap.modules)
    # print("Parameters")
    # print(cpxap.modules[5].parameters)

    # print(f"Channels: {cpxap.modules[IDX].read_channels()}")

    # cpxap.modules[IDX].write_module_parameter(PARAM, "+/- 10 V")
    # time.sleep(0.05)
    # m = cpxap.modules[IDX]

    # TODO: This print output should be moved to cpx_ap !

    for m in cpxap.modules:
        print(f"\n\nModule {m}:\n_____________________________________________________")
        for i, p in m.parameters.items():
            print(f"\tRead {p.name} (ID {i}) : {m.read_module_parameter(i)} {p.unit}")

        try:
            print(f"\n\tChannels: {m.read_channels()}")
        except NotImplementedError:
            print("\t(No readable channels available)")
