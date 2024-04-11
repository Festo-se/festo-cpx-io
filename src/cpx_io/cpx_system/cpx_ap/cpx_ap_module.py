"""CPX-E-AP module implementation"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.helpers import div_ceil


class CpxApModule(CpxModule):
    """Base class for cpx-ap modules"""

    @dataclass
    class ModuleParameters:
        """AP Parameters of module"""

        # pylint: disable=too-many-instance-attributes
        fieldbus_serial_number: int
        product_key: str
        firmware_version: str
        module_code: int
        temp_asic: int
        logic_voltage: float
        load_voltage: float
        hw_version: int
        io_link_variant: str = "n.a."
        operating_supply: bool = False

    def __init__(self, name=None):
        super().__init__(name=name)
        self.information = None

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {type(self).__name__})"

    def configure(self, base: CpxBase, position: int) -> None:
        super().configure(base=base, position=position)

        self.base.next_output_register += div_ceil(self.information.output_size, 2)
        self.base.next_input_register += div_ceil(self.information.input_size, 2)

    def update_information(self, info):
        """Update the module information"""
        self.information = info

    # TODO: This function can be deleted
    # @CpxBase.require_base
    # def read_ap_parameter(self) -> ModuleParameters:
    #     """Read AP parameters

    #     :return: ModuleParameters object containing all AP parameters
    #     :rtype: ModuleParameters
    #     """
    #     params = self.ModuleParameters(
    #         fieldbus_serial_number=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=246,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="UINT32",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #         product_key=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=791,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=12,
    #                 data_type="CHAR",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #         firmware_version=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=960,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=30,
    #                 data_type="CHAR",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #         module_code=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=20000,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="UINT32",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #         temp_asic=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=20085,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="INT16",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #         logic_voltage=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=20087,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="UINT16",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         )
    #         / 1000.0,
    #         load_voltage=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=20088,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="UINT16",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         )
    #         / 1000.0,
    #         hw_version=self.base.read_parameter(
    #             self.position,
    #             Parameter(
    #                 parameter_id=20093,
    #                 parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
    #                 is_writable=False,
    #                 array_size=None,
    #                 data_type="UINT8",
    #                 default_value=0,
    #                 description="",
    #                 name="",
    #             ),
    #         ),
    #     )
    #     Logging.logger.info(f"{self.name}: Reading AP parameters: {params}")
    #     return params
