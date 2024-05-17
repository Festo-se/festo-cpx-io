"""Contains tests for PhysicalQuantity build"""

from unittest.mock import Mock
import pytest
from cpx_io.cpx_system.cpx_ap.builder.physical_quantity_builder import (
    PhysicalUnit,
    PhysicalQuantity,
    build_physical_unit,
    build_physical_quantity,
)


class TestBuildPhysicalUnit:
    "Test build_physical_unit"

    def test_build_physical_unit(self):
        # Arrange
        format_string = "TestFormatString"
        name = "TestPhysicalUnit"
        physical_unit_id = 1
        physical_unit_dict = {
            "FormatString": format_string,
            "Name": name,
            "PhysicalUnitId": physical_unit_id,
        }

        # Act
        physical_unit = build_physical_unit(physical_unit_dict)

        # Assert
        assert isinstance(physical_unit, PhysicalUnit)
        assert physical_unit.format_string == format_string
        assert physical_unit.name == name
        assert physical_unit.physical_unit_id == physical_unit_id


class TestBuildPhysicalQuantity:
    "Test test_build_physical_quantity"

    def get_test_physical_unit_list(self, n_units):
        unit_list = []
        for i in range(n_units):
            format_string = f"TestFormatString{i}"
            name = f"TestPhysicalUnit{i}"
            physical_unit_id = i
            unit = {
                "FormatString": format_string,
                "Name": name,
                "PhysicalUnitId": physical_unit_id,
            }
            unit_list.append(unit)
        return unit_list

    def test_build_physical_quantity(self):
        # Arrange
        physical_quantity_id = 1
        name = "TestPhysicalQuantity"
        physical_unit_list = self.get_test_physical_unit_list(5)
        physical_quantity_dict = {
            "PhysicalQuantityId": physical_quantity_id,
            "Name": name,
            "PhysicalUnits": physical_unit_list,
        }

        # Act
        physical_quantity = build_physical_quantity(physical_quantity_dict)

        # Assert
        assert isinstance(physical_quantity, PhysicalQuantity)
        assert physical_quantity.physical_quantity_id == physical_quantity_id
        assert physical_quantity.name == name
        print(physical_quantity.units)
        for k, v in physical_quantity.units.items():
            assert v.format_string == f"TestFormatString{k}"
            assert v.name == f"TestPhysicalUnit{k}"
            assert v.physical_unit_id == k
