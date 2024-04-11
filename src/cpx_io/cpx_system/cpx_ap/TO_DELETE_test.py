"""Test program that needs to be deleted for production"""

import time
from importlib.resources import files
from pathlib import PurePath
import csv
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

    """used_params = []
    for m in cpxap.modules:
        for p in m.parameters.keys():
            used_params.append(p)
    used_params = set(used_params)

    listed_params = []
    parameter_map_file = PurePath(
        files("cpx_io")
        / "cpx_system"
        / "parameters_only_for_reference_use"
        / "parameter_map.csv"
    )
    with open(parameter_map_file, encoding="ascii") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        header = next(reader, None)
        [listed_params.append(int(row[0])) for row in reader]
    listed_params = set(listed_params)

    # print(used_params)
    # print(listed_params)
    diff = used_params - listed_params
    print(diff)
    """

    # TODO: beautiful print output should be moved to cpx_ap !
    cpxap.print_system_information()

    print("-----------------------------------------------------------------")
    print("-----------------------------------------------------------------")

    cpxap.print_system_state()
