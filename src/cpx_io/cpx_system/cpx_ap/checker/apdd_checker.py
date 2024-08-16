"""Check APDDs"""

import os
import json
from cpx_io.cpx_system.cpx_ap.builder import ap_module_builder
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp, ApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_supported_datatypes import (
    SUPPORTED_DATATYPES,
    SUPPORTED_IOL_DATATYPES,
)
from cpx_io.utils.logging import Logging


def check_apdd(apdd: dict) -> int:
    """Checks one apdd.
    Returns the number of variants with interpreting errors"""
    variants_with_errors = 0
    variant_list = apdd["Variants"]["VariantList"]
    for variant in variant_list:
        variant_code = variant["VariantIdentification"]["ModuleCode"]
        variant_name = variant["VariantIdentification"]["OrderText"]
        Logging.logger.info(f"Checking variant {variant_code} of {variant_name}")
        try:
            module = ap_module_builder.build_ap_module(apdd, variant_code)

            # check if datatypes are implemented. Needs to decide if IO-Link or not
            if (
                module.apdd_information.product_category
                == ProductCategory.IO_LINK.value
            ):
                supported_types = SUPPORTED_IOL_DATATYPES
            else:
                supported_types = SUPPORTED_DATATYPES

            check_if_apdd_datatypes_are_implemented(module, supported_types)

        # pylint: disable=broad-exception-caught
        # intentionally catching all errors
        except Exception as e:
            Logging.logger.error(
                f"APDD check failed for {variant_name} with module code {variant_code}\n"
                f"{e}"
            )
            variants_with_errors += 1

    return variants_with_errors


def check_apdds_in_folder(folder_path: str) -> int:
    """Checks all apdds in the given folder and returns the amount of failed interpretations"""
    apdds = os.listdir(folder_path)
    modules_with_errors = 0

    for a in apdds:
        with open(folder_path + "/" + a, "r", encoding="utf-8") as f:
            module_apdd = json.load(f)
        Logging.logger.info(f"Loaded apdd {a} from folder {folder_path}")

        if check_apdd(module_apdd):
            modules_with_errors += 1

    return modules_with_errors


def check_if_apdd_datatypes_are_implemented(
    module: ApModule, supported_types: list[str]
):
    """Checks if the used datatypes from ApModule are in the list of supported datatypes"""
    used_types = [
        i.data_type
        for i in module.channels.inputs
        + module.channels.outputs
        + module.channels.inouts
    ]
    missing_types = [
        datatype for datatype in used_types if datatype not in supported_types
    ]
    if missing_types:
        raise NotImplementedError(
            f"The datatypes {missing_types} from the APDD are not implemented"
        )


def main():
    """Main"""
    Logging()
    apdd_folder = CpxAp.create_apdd_path()

    Logging.logger.info(
        f"Check complete with {check_apdds_in_folder(apdd_folder)} failed modules"
    )


if __name__ == "__main__":
    main()
