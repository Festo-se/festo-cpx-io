"""Example code for CPX-AP parameter read and write"""

# import the library
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

# for cpx_ap, the attached modules are found automatically
with CpxAp(ip_address="192.168.1.1") as myCPX:
    # Read the automatically generated documentation on your system folder
    # It gives an overview of all parameters and functions of each module
    print(myCPX.docu_path)
    print("--------------------\n")

    # to get an overview of all available parameters, there is a function that iterates
    # over every module and reads out the parameters and channels if available
    myCPX.print_system_state()
    print("--------------------\n")

    # to read or write an individual parameter, you can either call it by ID or name,
    # ID is a bit faster. You can get both ID and name from the print_system_state function
    # or from the documentation or print the available parameters from each module. If the
    # value has enums as value, it will return the enum strings instead of the integer.
    module = myCPX.modules[1]
    for parameter in module.parameter_dict.values():
        # if you want to read it and print the correct unit of the value, you can get the unit
        # from the parameter. If you want to get the (if available) enum string, use
        # read_module_parameter_enum_str() instead.
        print(
            parameter.name,
            module.read_module_parameter(parameter.parameter_id),
            parameter.unit,
        )
    print("--------------------\n")

    # writing a parameter is almost the same, you can check if the parameter is writable by
    # the R/W tag or get it from the parameter. You should also check the datatype of the
    # parameter to reduce unwanted behaviours. If the parameter allows enums as value you can
    # either use the enum strings (you can get them by printing them from the parameter)

    # try this example with a cpx-ap digital input module on index 1 or adapt VALUE to the
    # correct value for your module parameter
    module = myCPX.modules[1]
    PARAM_VALUE = "3ms"
    PARAM_ID = 20014

    for parameter in module.parameter_dict.values():
        print(
            parameter.parameter_id,
            parameter.name,
            "\tIs writeable: ",
            parameter.is_writable,
            "\tData type: ",
            parameter.data_type,
            "\tEnums: ",
            parameter.enums,
        )

    # adapt this to your found parameter
    module.write_module_parameter(PARAM_ID, PARAM_VALUE)
