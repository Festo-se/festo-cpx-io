"""AP module Builder from APDD"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter, ParameterEnum
from cpx_io.cpx_system.cpx_ap.generic_ap_module import GenericApModule
from cpx_io.utils.logging import Logging


@dataclass
class Channel:
    """Channel dataclass"""

    bits: int
    channel_id: int
    data_type: str
    description: str
    direction: str
    name: str
    profile_list: list


@dataclass
class ChannelGroup:
    """ChannelGroup dataclass"""

    channel_group_id: int
    channels: dict
    name: str
    parameter_group_ids: list


@dataclass
class PhysicalQuantity:
    """PhysicalQuantity dataclass"""

    physical_quantity_id: int
    name: str
    units: list


@dataclass
class PhysicalUnit:
    """PhysicalUnits dataclass"""

    format_string: str
    name: str
    physical_unit_id: int


@dataclass
class Variant:
    """Variant dataclass"""

    description: str
    name: str
    parameter_group_ids: list
    variant_identification: dict


class ChannelGroupBuilder:
    """ChannelGroupBuilder"""

    def build(self, channel_group_dict):
        """Builds one ChannelGroup"""
        return ChannelGroup(
            channel_group_dict.get("ChannelGroupId"),
            channel_group_dict.get("Channels"),
            channel_group_dict.get("Name"),
            channel_group_dict.get("ParameterGroupIds"),
        )


class ChannelBuilder:
    """ChannelBuilder"""

    def build(self, channel_dict):
        """Builds one Channel"""
        return Channel(
            channel_dict.get("Bits"),
            channel_dict.get("ChannelId"),
            channel_dict.get("DataType"),
            channel_dict.get("Description"),
            channel_dict.get("Direction"),
            channel_dict.get("Name"),
            channel_dict.get("ProfileList"),
        )


class VariantBuilder:
    """VariantBuilder"""

    def build(self, variant_dict):
        """Builds one Variant"""
        return Variant(
            variant_dict.get("Description"),
            variant_dict.get("Name"),
            variant_dict.get("ParameterGroupIds"),
            variant_dict.get("VariantIdentification"),
        )


class ParameterBuilder:
    """ParameterBuilder"""

    def build(self, parameter_item, enums=None, units=None):
        """Builds one Parameter"""
        if parameter_item.get("ParameterId") == 20087:
            pass
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


class ParameterEnumBuilder:
    """ParameterEnumBuilder"""

    def build(self, enum_dict):
        """Builds one ParameterEnum"""
        enum_values = {}
        for e in enum_dict.get("EnumValues"):
            enum_values[e.get("Text")] = e.get("Value")

        return ParameterEnum(
            enum_dict.get("Id"),
            enum_dict.get("Bits"),
            enum_dict.get("DataType"),
            enum_values,
            enum_dict.get("EthercatEnumId"),
            enum_dict.get("Name"),
        )


class PhysicalUnitBuilder:
    """PhysicalUnit"""

    def build(self, physical_unit_dict):
        """Builds one PhysicalUnit"""
        return PhysicalUnit(
            physical_unit_dict.get("FormatString"),
            physical_unit_dict.get("Name"),
            physical_unit_dict.get("PhysicalUnitId"),
        )


class PhysicalQuantitiesBuilder:
    """PhysicalQuantities"""

    def build(self, physical_quantity_dict):
        """Builds one PhysicalQuantity"""
        physical_units = {}
        for p in physical_quantity_dict.get("PhysicalUnits"):
            physical_units[p.get("PhysicalUnitId")] = PhysicalUnitBuilder().build(p)

        return PhysicalQuantity(
            physical_quantity_dict.get("PhysicalQuantityId"),
            physical_quantity_dict.get("Name"),
            physical_units,
        )


class CpxApModuleBuilder:
    """Builder class for GenericApModule
    :return: AP Module generated from the apdd
    :rtype: GenericApModule
    """

    @staticmethod
    def _setup_channel_types(apdd_channels) -> list:
        channel_types = []
        if apdd_channels:
            for channel_dict in apdd_channels:
                channel_types.append(ChannelBuilder().build(channel_dict))
            Logging.logger.debug(f"Set up Channel Types: {channel_types}")
        return channel_types

    @staticmethod
    def _setup_channel_groups(apdd_channel_groups) -> list:
        channel_groups = []
        if apdd_channel_groups:
            for channel_group_dict in apdd_channel_groups:
                channel_groups.append(ChannelGroupBuilder().build(channel_group_dict))
            Logging.logger.debug(f"Set up Channel Groups: {channel_groups}")
        return channel_groups

    def build(self, apdd, module_code):
        """Build function for generic ap module"""

        product_category = apdd["Variants"]["DeviceIdentification"]["ProductCategory"]
        product_family = apdd["Variants"]["DeviceIdentification"]["ProductFamily"]

        variants = []
        for variant_dict in apdd["Variants"]["VariantList"]:
            variants.append(VariantBuilder().build(variant_dict))

        Logging.logger.debug(f"Set up Variants: {variants}")

        for v in variants:
            if v.variant_identification["ModuleCode"] == module_code:
                actual_variant = v

        if actual_variant:
            Logging.logger.debug(f"Set module variant to: {actual_variant}")
        else:
            raise IndexError(f"Could not find variant for ModuleCode {module_code}")

        module_information = {
            "Description": actual_variant.description,
            "Name": actual_variant.name.lower().replace("-", "_").replace(" ", "_"),
            "Module Type": actual_variant.name,
            "Configurator Code": actual_variant.variant_identification[
                "ConfiguratorCode"
            ],
            "Part Number": actual_variant.variant_identification[
                "FestoPartNumberDevice"
            ],
            "Module Class": actual_variant.variant_identification["ModuleClass"],
            "Module Code": actual_variant.variant_identification["ModuleCode"],
            "Order Text": actual_variant.variant_identification["OrderText"],
            "Product Category": product_category,
            "Product Family": product_family,
        }
        # setup all channel types
        channel_types = self._setup_channel_types(apdd.get("Channels"))

        # setup all channel groups
        channel_groups = self._setup_channel_groups(apdd.get("ChannelGroups"))

        # setup all channels for the module
        channels = []
        for channel_group in channel_groups:
            for channel in channel_group.channels:
                for channel_type in channel_types:
                    if channel_type.channel_id == channel.get("ChannelId"):
                        break

                for _ in range(channel["Count"]):
                    channels.append(channel_type)

        Logging.logger.debug(f"Set up Channels: {channels}")

        input_channels = [c for c in channels if c.direction == "in"]
        output_channels = [c for c in channels if c.direction == "out"]

        # setup metadata
        metadata = apdd.get("Metadata")
        if metadata:
            enum_list = metadata.get("EnumDataTypes")
            physical_quantities_list = metadata.get("PhysicalQuantities")

        ## setup enums used in the module
        enums = {e["Id"]: ParameterEnumBuilder().build(e) for e in enum_list}

        ## setup quantities used in the module
        physical_quantities = {
            q["PhysicalQuantityId"]: PhysicalQuantitiesBuilder().build(q)
            for q in physical_quantities_list
        }

        ## setup units used in the module
        units = {k: v for p in physical_quantities.values() for k, v in p.units.items()}

        # setup parameter groups, including list of all used parameters
        parameter_ids = {}
        parameter_groups = apdd.get("ParameterGroups")
        for pg in parameter_groups:
            parameter_ids[pg.get("Name")] = pg.get("ParameterIds")

        # setup parameters
        apdd_parameters = apdd.get("Parameters")
        if apdd_parameters:
            parameter_list = apdd_parameters.get("ParameterList")

        parameters = {
            p["ParameterId"]: ParameterBuilder().build(p, enums, units)
            for p in parameter_list
            if p.get("FieldbusSettings")
        }

        return GenericApModule(
            module_information,
            input_channels,
            output_channels,
            parameters,
            enums,
        )
