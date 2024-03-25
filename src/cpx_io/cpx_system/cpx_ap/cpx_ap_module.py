"""CPX-E-AP module implementation"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.cpx_system.cpx_module import CpxModule
from cpx_io.utils.logging import Logging
from cpx_io.utils.helpers import div_ceil
from cpx_io.cpx_system.parameter_mapping import ParameterNameMap


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

    @CpxBase.require_base
    def read_ap_parameter(self) -> ModuleParameters:
        """Read AP parameters

        :return: ModuleParameters object containing all AP parameters
        :rtype: ModuleParameters
        """
        params = self.ModuleParameters(
            fieldbus_serial_number=self.base.read_parameter(
                self.position, ParameterNameMap()["FieldbusSerialNumber"]
            ),
            product_key=self.base.read_parameter(
                self.position, ParameterNameMap()["Productkey"]
            ),
            firmware_version=self.base.read_parameter(
                self.position, ParameterNameMap()["FirmwareVersionString"]
            ),
            module_code=self.base.read_parameter(
                self.position, ParameterNameMap()["ModuleCode"]
            ),
            temp_asic=self.base.read_parameter(
                self.position, ParameterNameMap()["TemperatureValueASIC"]
            ),
            logic_voltage=self.base.read_parameter(
                self.position, ParameterNameMap()["UElsenValue"]
            )
            / 1000.0,
            load_voltage=self.base.read_parameter(
                self.position, ParameterNameMap()["ULoadValue"]
            )
            / 1000.0,
            hw_version=self.base.read_parameter(
                self.position, ParameterNameMap()["HardwareVersion"]
            ),
        )
        Logging.logger.info(f"{self.name}: Reading AP parameters: {params}")
        return params
