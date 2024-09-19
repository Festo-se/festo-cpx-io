"""Contains tests for ApddInformation build"""

import pytest
from cpx_io.cpx_system.cpx_ap.dataclasses.apdd_information import ApddInformation
from cpx_io.cpx_system.cpx_ap.builder.apdd_information_builder import (
    Variant,
    build_variant,
    build_actual_variant,
    build_apdd_information,
)


class TestBuildVariant:
    "Test build_variant"

    def test_build_variant(self):
        # Arrange
        channel_group_ids = [1, 2, 3, 4, 5]
        description = "VariantDescription"
        name = "TestVariant"
        parameter_group_ids = [1, 2, 3, 4, 5]
        profile = [0]
        variant_identification = {"foo": "bar"}
        variant_dict = {
            "ChannelGroupIds": channel_group_ids,
            "Description": description,
            "Name": name,
            "ParameterGroupIds": parameter_group_ids,
            "Profile": profile,
            "VariantIdentification": variant_identification,
        }

        # Act
        variant = build_variant(variant_dict)

        # Assert
        assert isinstance(variant, Variant)
        assert variant.channel_group_ids == channel_group_ids
        assert variant.description == description
        assert variant.name == name
        assert variant.parameter_group_ids == parameter_group_ids
        assert variant.profile == profile
        assert variant.variant_identification == variant_identification


class TestBuildApddInformation:
    "Test build_apdd_information"

    def get_test_variant_list(self, n_variants):
        variant_list = []
        for i in range(n_variants):
            description = "VariantDescription"
            name = f"TestVariant{i}"
            parameter_group_ids = []
            variant_identification = {
                "ConfiguratorCode": 0,
                "FestoPartNumberDevice": 0,
                "ModuleClass": 0,
                "ModuleCode": i,
                "OrderText": f"TestOrder{i}Text",
            }
            variant = {
                "Description": description,
                "Name": name,
                "ParameterGroupIds": parameter_group_ids,
                "VariantIdentification": variant_identification,
            }
            variant_list.append(variant)
        return variant_list

    def test_build_actual_variant_5_variants_returns_correct_variant(self):
        "Test build_actual_variant"
        # Arrange
        # variant module codes = [0,1,2,3,4]
        variant_list = self.get_test_variant_list(n_variants=5)
        product_category = "foo"
        product_family = "bar"
        apdd = {
            "Variants": {
                "VariantList": variant_list,
                "DeviceIdentification": {
                    "ProductCategory": product_category,
                    "ProductFamily": product_family,
                },
            },
        }
        # Act
        actual_variant = build_actual_variant(apdd=apdd, module_code=3)

        # Assert
        assert actual_variant.description == "VariantDescription"
        assert actual_variant.name == "TestVariant3"

    def test_build_apdd_information_5_variants_returns_correct_apdd_information(self):
        # Arrange
        # variant module codes = [0,1,2,3,4]
        variant_list = self.get_test_variant_list(n_variants=5)
        product_category = "foo"
        product_family = "bar"
        apdd = {
            "Variants": {
                "VariantList": variant_list,
                "DeviceIdentification": {
                    "ProductCategory": product_category,
                    "ProductFamily": product_family,
                },
            },
        }
        variant = build_variant(variant_list[3])
        # Act
        apdd_information = build_apdd_information(apdd=apdd, variant=variant)
        # Assert
        assert isinstance(apdd_information, ApddInformation)
        assert apdd_information.name == "testvariant3"
        assert apdd_information.module_type == "TestVariant3"
        assert apdd_information.module_code == 3
        assert apdd_information.product_category == product_category
        assert apdd_information.product_family == product_family

    def test_build_actual_variant_5_variants_no_valid_module_code_raise_exception(
        self,
    ):
        # Arrange
        # variant module codes = [0,1,2,3,4]
        variant_list = self.get_test_variant_list(n_variants=5)
        product_category = "foo"
        product_family = "bar"
        apdd = {
            "Variants": {
                "VariantList": variant_list,
                "DeviceIdentification": {
                    "ProductCategory": product_category,
                    "ProductFamily": product_family,
                },
            },
        }
        # Act & Assert
        with pytest.raises(IndexError):
            build_actual_variant(apdd=apdd, module_code=6)
