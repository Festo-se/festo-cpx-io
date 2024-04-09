import time
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="172.16.1.41") as cpxap:
    IDX = 3
    PARAM = 20111
    print(cpxap.modules)
    print(cpxap.modules[IDX].get_available_parameters())

    cpxap.modules[IDX].write_module_parameter(True, PARAM)
    time.sleep(0.05)
    print(cpxap.modules[IDX].read_module_parameter(20032))
