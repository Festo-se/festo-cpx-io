"""Test program that needs to be deleted for production"""

import time
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="172.16.1.41") as cpxap:
    IDX = 3
    PARAM = 20043
    print("Modules: ", cpxap.modules)
    print("Parameters")
    print(cpxap.modules[IDX].parameters)
    print(f"Channels: {cpxap.modules[IDX].read_channels()}")

    cpxap.modules[IDX].write_module_parameter(PARAM, "+/- 10 V")
    time.sleep(0.05)
    m = cpxap.modules[IDX]

    for i, p in m.parameters.items():
        print(f"Read: {i} ({p.name}): {m.read_module_parameter(i)}")
