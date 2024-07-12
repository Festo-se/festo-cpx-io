"""Check APDDs"""

import os
import json
from cpx_io.cpx_system.cpx_ap.builder import ap_module_builder
from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp
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
            ap_module_builder.build_ap_module(apdd, variant_code)
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


def main():
    """Main"""
    Logging()
    apdd_folder = CpxAp.create_apdd_path()

    Logging.logger.info(
        f"Check complete with {check_apdds_in_folder(apdd_folder)} failed modules"
    )


if __name__ == "__main__":
    main()
