"""ApddInformation builder function from APDD"""

from dataclasses import dataclass
from typing import List
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation
from cpx_io.utils.logging import Logging


@dataclass
class Variant:
    """Variant dataclass"""

    channel_group_ids: List[int]
    description: str
    name: str
    parameter_group_ids: List[int]
    profile: List[int]
    variant_identification: dict


def build_variant(variant_dict):
    """Builds one Variant"""
    return Variant(
        variant_dict.get("ChannelGroupIds"),
        variant_dict.get("Description"),
        variant_dict.get("Name"),
        variant_dict.get("ParameterGroupIds"),
        variant_dict.get("Profile"),
        variant_dict.get("VariantIdentification"),
    )


def build_actual_variant(apdd, module_code):
    """Build variant and return the correct one according to module_code"""
    variant_list = [build_variant(d) for d in apdd["Variants"]["VariantList"]]
    Logging.logger.debug(f"Variants: {variant_list}")
    variant = next(
        (
            v
            for v in variant_list
            if v.variant_identification["ModuleCode"] == module_code
        ),
        None,
    )
    if variant is None:
        raise IndexError(f"Could not find variant for ModuleCode {module_code}")
    Logging.logger.debug(f"Module Variant: {variant}")
    return variant


def build_apdd_information(apdd, variant):
    """Builds one ApddInformation"""

    product_category = apdd["Variants"]["DeviceIdentification"].get("ProductCategory")
    product_family = apdd["Variants"]["DeviceIdentification"].get("ProductFamily")

    if not product_category or not product_family:
        raise RuntimeError(
            f"{variant.name} can not be build due to outdated firmware. "
            "Consider updating your cpx-ap module with the latest firmware "
            "from https://www.festo.com"
        )

    return ApddInformation(
        variant.description,
        variant.name.lower().replace("-", "_").replace(" ", "_"),
        variant.name,
        variant.variant_identification["ConfiguratorCode"],
        variant.variant_identification["FestoPartNumberDevice"],
        variant.variant_identification["ModuleClass"],
        variant.variant_identification["ModuleCode"],
        variant.variant_identification["OrderText"],
        product_category,
        product_family,
    )
