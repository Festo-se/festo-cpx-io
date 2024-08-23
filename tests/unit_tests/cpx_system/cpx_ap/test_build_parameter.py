"""Contains tests for PhysicalQuantity build"""

from cpx_io.cpx_system.cpx_ap.ap_parameter import Parameter, ParameterEnum
from cpx_io.cpx_system.cpx_ap.builder.physical_quantity_builder import PhysicalUnit
from cpx_io.cpx_system.cpx_ap.builder.parameter_builder import (
    build_parameter_enum,
    build_parameter,
    build_parameter_list,
)


class TestBuildParameterEnum:
    "Test build_parameter_enum"

    def test_build_parameter_enum(self):
        # Arrange
        enum_id = 1
        bits = 4
        data_type = "int"
        enum_values = [{"Text": "a", "Value": 1}, {"Text": "b", "Value": 2}]
        ethercat_enum_id = 100
        name = "TestName"
        parameter_enum_dict = {
            "Id": enum_id,
            "Bits": bits,
            "DataType": data_type,
            "EnumValues": enum_values,
            "EthercatEnumId": ethercat_enum_id,
            "Name": name,
        }

        # Act
        parameter_enum = build_parameter_enum(parameter_enum_dict)

        # Assert
        assert isinstance(parameter_enum, ParameterEnum)
        assert parameter_enum.enum_id == enum_id
        assert parameter_enum.bits == bits
        assert parameter_enum.data_type == data_type
        assert parameter_enum.enum_values == {"a": 1, "b": 2}
        assert parameter_enum.ethercat_enum_id == ethercat_enum_id
        assert parameter_enum.name == name


class TestBuildParameter:
    "Test build_parameter"

    def test_build_parameter_no_unit(self):
        # Arrange
        parameter_id = 1
        parameter_instances = 1
        is_writable = True
        data_definition = {
            "ArraySize": 1,
            "DataType": "int",
            "DefaultValue": 5,
            "Description": "TestDescription",
            "Name": "foo",
            "LimitEnumValues": {"EnumDataType": "bar"},
        }
        module_dicts.parameters = {
            "ParameterId": parameter_id,
            "ParameterInstances": parameter_instances,
            "IsWritable": is_writable,
            "DataDefinition": data_definition,
        }
        enum_dict = {"bar": ["a", "b", "c"]}

        # Act
        parameter = build_parameter(module_dicts.parameters, enum_dict)

        # Assert
        assert isinstance(parameter, Parameter)
        assert parameter.parameter_id == parameter_id
        assert parameter.parameter_instances == parameter_instances
        assert parameter.is_writable == is_writable
        assert parameter.array_size == 1
        assert parameter.data_type == "int"
        assert parameter.default_value == 5
        assert parameter.description == "TestDescription"
        assert parameter.name == "foo"
        assert parameter.unit == ""
        assert parameter.enums == ["a", "b", "c"]

    def test_build_parameter_with_unit(self):
        # Arrange
        parameter_id = 1
        parameter_instances = 1
        is_writable = True
        data_definition = {
            "ArraySize": 1,
            "DataType": "int",
            "DefaultValue": 5,
            "Description": "TestDescription",
            "Name": "foo",
            "LimitEnumValues": {"EnumDataType": "bar"},
            "PhysicalUnitId": "TestPhysicalUnitId",
        }
        module_dicts.parameters = {
            "ParameterId": parameter_id,
            "ParameterInstances": parameter_instances,
            "IsWritable": is_writable,
            "DataDefinition": data_definition,
        }
        enum_dict = {"bar": ["a", "b", "c"]}
        test_physical_unit = PhysicalUnit("TestFormatString", "TestPhysicalUnitName", 4)
        units = {"TestPhysicalUnitId": test_physical_unit}

        # Act
        parameter = build_parameter(module_dicts.parameters, enum_dict, units)

        # Assert
        assert isinstance(parameter, Parameter)
        assert parameter.parameter_id == parameter_id
        assert parameter.parameter_instances == parameter_instances
        assert parameter.is_writable == is_writable
        assert parameter.array_size == 1
        assert parameter.data_type == "int"
        assert parameter.default_value == 5
        assert parameter.description == "TestDescription"
        assert parameter.name == "foo"
        assert parameter.unit == "TestFormatString"
        assert parameter.enums == ["a", "b", "c"]


class TestBuildParameterList:
    "Test build_parameter_list"

    def get_enum_data_type_list(self, n_enum_types):
        enum_data_type_list = []
        for i in range(n_enum_types):
            enum_values = [{"Text": f"a{i}", "Value": 1}, {"Text": f"b{i}", "Value": 2}]
            parameter_enum_dict = {
                "Id": i,
                "Bits": 0,
                "DataType": f"TestDataType{i}",
                "EnumValues": enum_values,
                "EthercatEnumId": 0,
                "Name": f"TestEnumTypeName{i}",
            }
            enum_data_type_list.append(parameter_enum_dict)
        return enum_data_type_list

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

    def get_physical_quantity_list(self, n_physical_quantities):
        physical_quantity_list = []
        for i in range(n_physical_quantities):
            physical_unit_list = self.get_test_physical_unit_list(5)
            physical_quantity_dict = {
                "PhysicalQuantityId": i,
                "Name": "PhysicalQuantity{i}",
                "PhysicalUnits": physical_unit_list,
            }
            physical_quantity_list.append(physical_quantity_dict)
        return physical_quantity_list

    def get_parameter_list(self, n_parameters):
        parameter_list = []
        for i in range(n_parameters):
            data_definition = {
                "ArraySize": 1,
                "DataType": f"TestDataType{i}",
                "DefaultValue": 5,
                "Description": f"TestDescription{i}",
                "Name": f"ParameterName{i}",
                "LimitEnumValues": {"EnumDataType": "bar"},
                "PhysicalUnitId": f"TestPhysicalUnitId{i}",
            }
            module_dicts.parameters = {
                "ParameterId": i,
                "ParameterInstances": 1,
                "IsWritable": False,
                "DataDefinition": data_definition,
                "FieldbusSettings": True,
            }
            parameter_list.append(module_dicts.parameters)
        return parameter_list

    def test_build_parameter_list(self):
        # Arrange
        enum_data_type_list = self.get_enum_data_type_list(5)
        physical_quantity_list = self.get_physical_quantity_list(5)

        metadata = {
            "EnumDataTypes": enum_data_type_list,
            "PhysicalQuantities": physical_quantity_list,
        }
        parameter_list = self.get_parameter_list(5)
        parameters = {"ParameterList": parameter_list}
        apdd = {
            "Metadata": metadata,
            "Parameters": parameters,
        }

        # Act
        parameter_list = build_parameter_list(apdd=apdd)

        # Assert
        assert len(parameter_list) == 5
        for i, parameter in enumerate(parameter_list):
            assert isinstance(parameter, Parameter)
            assert parameter.parameter_id == i
            assert parameter.data_type == f"TestDataType{i}"
            assert parameter.description == f"TestDescription{i}"
            assert parameter.name == f"ParameterName{i}"
