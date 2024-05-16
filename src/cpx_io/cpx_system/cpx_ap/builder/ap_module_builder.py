"""ApModuleBuilder from APDD"""

from cpx_io.cpx_system.cpx_ap.builder.apdd_information_builder import (
    ApddInformationBuilder,
)
from cpx_io.cpx_system.cpx_ap.builder.channel_builder import (
    ChannelListBuilder,
)
from cpx_io.cpx_system.cpx_ap.builder.parameter_builder import (
    ParameterListBuilder,
)
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.utils.logging import Logging


class ApModuleBuilder:
    """ApModuleBuilder for dataclasses"""

    def build(self, apdd: dict, module_code: int) -> ApModule:
        """Build function for generic ap module
        :parameter apdd: apdd json dict for one module
        :type apdd: dict
        :parameter module_code: Module code of actual variant
        :type module_code: int
        :return: AP Module generated from the apdd
        :rtype: ApModule"""
        apdd_information = ApddInformationBuilder().build(
            apdd=apdd, module_code=module_code
        )
        Logging.logger.debug(f"ApddInformation: {apdd_information}")

        input_channel_list = ChannelListBuilder().build(apdd=apdd, direction="in")
        Logging.logger.debug(f"Input Channels: {input_channel_list}")

        output_channel_list = ChannelListBuilder().build(apdd=apdd, direction="out")
        Logging.logger.debug(f"Output Channels: {output_channel_list}")

        parameter_list = ParameterListBuilder().build(apdd=apdd)
        Logging.logger.debug(f"Parameters: {parameter_list}")

        return ApModule(
            apdd_information,
            (input_channel_list, output_channel_list),
            parameter_list,
        )
