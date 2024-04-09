import time
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="172.16.1.41") as cpxap:
    IDX = 3
    PARAM = 20032
    print("Modules: ", cpxap.modules)
    print("")
    print("Parameters: ", cpxap.modules[IDX].get_available_parameters())
    print("")
    print("Enum: ", cpxap.modules[IDX].get_parameter_enums(PARAM))
    print("")

    cpxap.modules[IDX].write_module_parameter(PARAM, "Fahrenheit")
    time.sleep(0.05)
    print(cpxap.modules[IDX].read_module_parameter(PARAM))
