"""PhysicalQuantity builder function from APDD"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PhysicalUnit:
    """PhysicalUnits dataclass"""

    format_string: str
    name: str
    physical_unit_id: int


@dataclass
class PhysicalQuantity:
    """PhysicalQuantity dataclass"""

    physical_quantity_id: int
    name: str
    units: Dict[int, PhysicalUnit]


def build_physical_unit(physical_unit_dict):
    """Builds one PhysicalUnit"""
    return PhysicalUnit(
        physical_unit_dict.get("FormatString"),
        physical_unit_dict.get("Name"),
        physical_unit_dict.get("PhysicalUnitId"),
    )


def build_physical_quantity(physical_quantity_dict):
    """Builds one PhysicalQuantity"""
    physical_units = {}
    for p in physical_quantity_dict.get("PhysicalUnits"):
        physical_units[p.get("PhysicalUnitId")] = build_physical_unit(p)

    return PhysicalQuantity(
        physical_quantity_dict.get("PhysicalQuantityId"),
        physical_quantity_dict.get("Name"),
        physical_units,
    )
