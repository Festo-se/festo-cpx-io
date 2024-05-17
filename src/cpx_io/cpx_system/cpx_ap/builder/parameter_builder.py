"""Parameter builder functions from APDD"""

from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter, ParameterEnum
from cpx_io.cpx_system.cpx_ap.builder.physical_quantity_builder import (
    build_physical_quantity,
)


def build_parameter_enum(enum_dict):
    """Builds one ParameterEnum"""
    enum_values = {
        enum.get("Text"): enum.get("Value") for enum in enum_dict.get("EnumValues")
    }

    return ParameterEnum(
        enum_dict.get("Id"),
        enum_dict.get("Bits"),
        enum_dict.get("DataType"),
        enum_values,
        enum_dict.get("EthercatEnumId"),
        enum_dict.get("Name"),
    )


def build_parameter(parameter_item, enums=None, units=None):
    """Builds one Parameter"""
    valid_unit = (
        units.get(parameter_item.get("DataDefinition").get("PhysicalUnitId"))
        if units
        else None
    )
    format_string = valid_unit.format_string if valid_unit else ""

    return Parameter(
        parameter_item.get("ParameterId"),
        parameter_item.get("ParameterInstances"),
        parameter_item.get("IsWritable"),
        parameter_item.get("DataDefinition").get("ArraySize"),
        parameter_item.get("DataDefinition").get("DataType"),
        parameter_item.get("DataDefinition").get("DefaultValue"),
        parameter_item.get("DataDefinition").get("Description"),
        parameter_item.get("DataDefinition").get("Name"),
        format_string,
        enums.get(
            parameter_item.get("DataDefinition")
            .get("LimitEnumValues")
            .get("EnumDataType")
            if parameter_item.get("DataDefinition").get("LimitEnumValues")
            else None
        ),
    )


def build_parameter_list(apdd) -> list:
    """Builds one ParameterList"""
    # setup metadata
    metadata = apdd.get("Metadata")
    enum_list = metadata.get("EnumDataTypes")
    physical_quantities_list = metadata.get("PhysicalQuantities")

    ## setup enums used in the module
    enums = {e["Id"]: build_parameter_enum(e) for e in enum_list}

    ## setup quantities used in the module
    physical_quantities = {
        q["PhysicalQuantityId"]: build_physical_quantity(q)
        for q in physical_quantities_list
    }

    ## setup units used in the module
    units = {k: v for p in physical_quantities.values() for k, v in p.units.items()}

    # parameter dict
    apdd_parameter_list = apdd.get("Parameters").get("ParameterList")
    return [
        build_parameter(p, enums, units)
        for p in apdd_parameter_list
        if p.get("FieldbusSettings")
    ]
