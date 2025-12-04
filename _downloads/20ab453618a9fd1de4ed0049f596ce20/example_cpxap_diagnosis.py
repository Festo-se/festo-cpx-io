"""Example code for diagnosis with CPX-AP"""

import time

# Import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="192.168.1.1") as myCPX:
    # optional: for easy access, assign the IO-Link module to an object
    myIOL = myCPX.cpx_ap_a_4iol_m12_variant_16
    SDAS_CHANNEL = 2  # this assumes you have a SDAS sensor on channel 2

    # Write the validation setting
    myIOL.write_module_parameter(
        "Validation & Backup", "Type compatible Device V1.1", SDAS_CHANNEL
    )

    # Write the IO-Link device ID and Vendor ID to the IO-Link module
    # You can read these with read_fieldbus_parameters()[SDAS_CHANNEL]
    # In this example, we write a wrong ID on purpose (it should be 12)
    # So that an error occures and we can read it out.
    myIOL.write_module_parameter("DeviceID", 13, SDAS_CHANNEL)
    myIOL.write_module_parameter("Nominal Vendor ID", 333, SDAS_CHANNEL)

    # Set the Port Mode to IOL_MANUAL. This will compare the written DeviceID
    # with the actual device ID and the Nominal Vendor ID with the actual vendor
    # ID. If they do not match, the "Port status information" of the fieldbus
    # parameters will change to "PORT_DIAG"
    myIOL.write_module_parameter("Port Mode", "IOL_MANUAL", SDAS_CHANNEL)
    time.sleep(0.05)  # give it some time to set everything

    param = myIOL.read_fieldbus_parameters()
    print(param[SDAS_CHANNEL])

    # If everything works, this loop will run until the port goes into OPERATE
    # mode. But in our example it will go to PORT_DIAG. We catch this with the
    # following if statement and print the diagnosis information from the module
    while param[SDAS_CHANNEL]["Port status information"] != "OPERATE":
        param = myIOL.read_fieldbus_parameters()

        if param[SDAS_CHANNEL]["Port status information"] == "PORT_DIAG":
            print(myIOL.read_diagnosis_information())
            break
