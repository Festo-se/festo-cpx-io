"""ApModule builder function from APDD"""

from cpx_io.cpx_system.cpx_ap.builder.apdd_information_builder import (
    build_apdd_information,
)
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import build_channel_list
from cpx_io.cpx_system.cpx_ap.builder.parameter_builder import build_parameter_list
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.utils.logging import Logging


def build_ap_module(apdd: dict, module_code: int) -> ApModule:
    """Build function for generic ap module
    :parameter apdd: apdd json dict for one module
    :type apdd: dict
    :parameter module_code: Module code of actual variant
    :type module_code: int
    :return: AP Module generated from the apdd
    :rtype: ApModule"""
    apdd_information = build_apdd_information(apdd=apdd, module_code=module_code)
    Logging.logger.debug(f"ApddInformation: {apdd_information}")

    input_channel_list = build_channel_list(apdd=apdd, direction="in")
    Logging.logger.debug(f"Input Channels: {input_channel_list}")

    output_channel_list = build_channel_list(apdd=apdd, direction="out")
    Logging.logger.debug(f"Output Channels: {output_channel_list}")

    parameter_list = build_parameter_list(apdd=apdd)
    Logging.logger.debug(f"Parameters: {parameter_list}")

    return ApModule(
        apdd_information,
        (input_channel_list, output_channel_list),
        parameter_list,
    )
