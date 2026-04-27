"""Example code for CPX-AP startup and system information"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:

    # iterate over each module and print out the available diagnosis object
    for index, module in enumerate(myCPX.modules):
        diagnosis = module.read_diagnosis_information()

        # don't print if diagnosis == None
        if diagnosis:
            print(index, diagnosis)
