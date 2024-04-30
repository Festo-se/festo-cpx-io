"""AP module Builder from APDD"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter, ParameterEnum
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.utils.logging import Logging


@dataclass
class Channel:
    """Channel dataclass"""

    # pylint: disable=too-many-instance-attributes
    array_size: int
    bits: int
    byte_swap_needed: bool
    channel_id: int
    data_type: str
    description: str
    direction: str
    name: str
    parameter_group_ids: list
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


class Builder:
    """Builder for dataclasses"""

    def build_channel_group(self, channel_group_dict):
        """Builds one ChannelGroup"""
        return ChannelGroup(
            channel_group_dict.get("ChannelGroupId"),
            channel_group_dict.get("Channels"),
            channel_group_dict.get("Name"),
            channel_group_dict.get("ParameterGroupIds"),
        )

    def build_channel(self, channel_dict):
        """Builds one Channel"""
        return Channel(
            channel_dict.get("ArraySize"),
            channel_dict.get("Bits"),
            channel_dict.get("ByteSwapNeeded"),
            channel_dict.get("ChannelId"),
            channel_dict.get("DataType"),
            channel_dict.get("Description"),
            channel_dict.get("Direction"),
            channel_dict.get("Name"),
            channel_dict.get("ParameterGroupIds"),
            channel_dict.get("ProfileList"),
        )

    def build_variant(self, variant_dict):
        """Builds one Variant"""
        return Variant(
            variant_dict.get("Description"),
            variant_dict.get("Name"),
            variant_dict.get("ParameterGroupIds"),
            variant_dict.get("VariantIdentification"),
        )

    def build_parameter(self, parameter_item, enums=None, units=None):
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

    def build_parameter_enum(self, enum_dict):
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

    def build_physical_unit(self, physical_unit_dict):
        """Builds one PhysicalUnit"""
        return PhysicalUnit(
            physical_unit_dict.get("FormatString"),
            physical_unit_dict.get("Name"),
            physical_unit_dict.get("PhysicalUnitId"),
        )

    def build_physical_quantities(self, physical_quantity_dict):
        """Builds one PhysicalQuantity"""
        physical_units = {}
        for p in physical_quantity_dict.get("PhysicalUnits"):
            physical_units[p.get("PhysicalUnitId")] = self.build_physical_unit(p)

        return PhysicalQuantity(
            physical_quantity_dict.get("PhysicalQuantityId"),
            physical_quantity_dict.get("Name"),
            physical_units,
        )

    def build_apdd_information(self, apdd_information_dict):
        """Builds one ApddInformation"""
        return ApModule.ApddInformation(
            apdd_information_dict.get("Description"),
            apdd_information_dict.get("Name"),
            apdd_information_dict.get("Module Type"),
            apdd_information_dict.get("Configurator Code"),
            apdd_information_dict.get("Part Number"),
            apdd_information_dict.get("Module Class"),
            apdd_information_dict.get("Module Code"),
            apdd_information_dict.get("Order Text"),
            apdd_information_dict.get("Product Category"),
            apdd_information_dict.get("Product Family"),
        )

    def _setup_channel_types(self, apdd_channels) -> list:
        channel_types = []
        if apdd_channels:
            for channel_dict in apdd_channels:
                channel_types.append(self.build_channel(channel_dict))
            Logging.logger.debug(f"Set up Channel Types: {channel_types}")
        return channel_types

    def _setup_channel_groups(self, apdd_channel_groups) -> list:
        channel_groups = []
        if apdd_channel_groups:
            for channel_group_dict in apdd_channel_groups:
                channel_groups.append(self.build_channel_group(channel_group_dict))
            Logging.logger.debug(f"Set up Channel Groups: {channel_groups}")
        return channel_groups

    def _setup_variants(self, apdd_variants) -> list:
        variants = []
        for variant_dict in apdd_variants["VariantList"]:
            variants.append(self.build_variant(variant_dict))

        Logging.logger.debug(f"Set up Variants: {variants}")
        return variants

    def _setup_channels(self, channel_groups, channel_types) -> list:
        channels = []
        channel_type = None
        for channel_group in channel_groups:
            for channel in channel_group.channels:
                for channel_type in channel_types:
                    if channel_type.channel_id == channel.get("ChannelId"):
                        break

                for _ in range(channel["Count"]):
                    channels.append(channel_type)

        Logging.logger.debug(f"Set up Channels: {channels}")
        return channels

    def _setup_parameters(self, apdd_parameters, enums, units) -> list:

        parameter_list = apdd_parameters.get("ParameterList")

        parameters = {
            p["ParameterId"]: self.build_parameter(p, enums, units)
            for p in parameter_list
            if p.get("FieldbusSettings")
        }
        Logging.logger.debug(f"Set up Parameters: {parameters}")
        return parameters

    def build_ap_module(self, apdd: dict, module_code: int) -> ApModule:
        """Build function for generic ap module
        :parameter apdd: apdd json dict for one module
        :type apdd: dict
        :parameter module_code: Module code of actual variant
        :type module_code: int
        :return: AP Module generated from the apdd
        :rtype: ApModule"""

        for v in self._setup_variants(apdd["Variants"]):
            if v.variant_identification["ModuleCode"] == module_code:
                actual_variant = v

        if actual_variant:
            Logging.logger.debug(f"Set module variant to: {actual_variant}")
        else:
            raise IndexError(f"Could not find variant for ModuleCode {module_code}")

        apdd_information = self.build_apdd_information(
            {
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
                "Product Category": apdd["Variants"]["DeviceIdentification"][
                    "ProductCategory"
                ],
                "Product Family": apdd["Variants"]["DeviceIdentification"][
                    "ProductFamily"
                ],
            }
        )

        # setup all channels for the module
        channels = self._setup_channels(
            self._setup_channel_groups(apdd.get("ChannelGroups")),
            self._setup_channel_types(apdd.get("Channels")),
        )

        # split them in input and output channels
        input_channels = [c for c in channels if c.direction == "in"]
        output_channels = [c for c in channels if c.direction == "out"]

        # setup metadata
        metadata = apdd.get("Metadata")
        if metadata:
            enum_list = metadata.get("EnumDataTypes")
            physical_quantities_list = metadata.get("PhysicalQuantities")

        if enum_list:
            ## setup enums used in the module
            enums = {e["Id"]: self.build_parameter_enum(e) for e in enum_list}

        ## setup quantities used in the module
        if physical_quantities_list:
            physical_quantities = {
                q["PhysicalQuantityId"]: self.build_physical_quantities(q)
                for q in physical_quantities_list
            }

        ## setup units used in the module
        if physical_quantities:
            units = {
                k: v for p in physical_quantities.values() for k, v in p.units.items()
            }

        return ApModule(
            apdd_information,
            (input_channels, output_channels),
            self._setup_parameters(apdd.get("Parameters"), enums, units),
        )
