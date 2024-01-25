"""CPX-E-AP module implementation"""

from dataclasses import dataclass
from cpx_io.cpx_system.cpx_base import CpxBase
from cpx_io.utils.logging import Logging
from cpx_io.utils.helpers import div_ceil


class CpxApModule:
    """Base class for cpx-ap modules"""

    @dataclass
    class ApParameters:
        """AP Parameters of module"""

        # pylint: disable=too-many-instance-attributes
        fieldbus_serial_number: int
        product_key: str
        firmware_version: str
        module_code: int
        temp_asic: int
        logic_voltage: int
        load_voltage: int
        hw_version: int
        io_link_variant: str = "n.a."
        operating_supply: bool = False

    def __init__(self, name=None):
        self.base = None
        self.position = None
        self.information = None

        self.output_register = None
        self.input_register = None
        self._name = None
        self.name = name

    def __repr__(self):
        return f"{self.name} (idx: {self.position}, type: {type(self).__name__})"

    @property
    def name(self):
        """
        Property getter for name.
        """
        return self._name

    # pylint: disable=duplicate-code
    # intended: cpx-ap and cpx-e have similar functions
    @name.setter
    def name(self, name_value):
        """
        Property setter for name.
        Updates base module list if base exists.
        """
        if name_value:
            self._name = name_value
        else:
            # Use class name (lower cased) as default value
            self._name = type(self).__name__.lower()

        if self.base:
            self.base.update_module_names()

    def configure(self, base, position):
        """Set up module when added to cpx system"""
        # pylint: disable=duplicate-code
        # intended: cpx-ap and cpx-e have similar functions
        self.base = base
        self.position = position

        # if name already exists in module list, add a counter as suffix
        module_type_list = [type(module) for module in self.base.modules]
        if type(self) in module_type_list:
            self.name = f"{self.name}_{module_type_list.count(type(self))}"

        self.output_register = self.base.next_output_register
        self.input_register = self.base.next_input_register

        self.base.next_output_register += div_ceil(self.information.output_size, 2)
        self.base.next_input_register += div_ceil(self.information.input_size, 2)

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    def update_information(self, info):
        """Update the module information"""
        self.information = info

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters"""
        params = self.ApParameters(
            fieldbus_serial_number=CpxBase.decode_int(
                self.base.read_parameter(self.position, 246, 0), data_type="uint32"
            ),
            product_key=CpxBase.decode_string(
                self.base.read_parameter(self.position, 791, 0)
            ),
            firmware_version=CpxBase.decode_string(
                self.base.read_parameter(self.position, 960, 0)
            ),
            module_code=CpxBase.decode_int(
                self.base.read_parameter(self.position, 20000, 0), data_type="uint32"
            ),
            temp_asic=CpxBase.decode_int(
                self.base.read_parameter(self.position, 20085, 0), data_type="int16"
            ),
            logic_voltage=CpxBase.decode_int(
                self.base.read_parameter(self.position, 20087, 0), data_type="uint16"
            ),
            load_voltage=CpxBase.decode_int(
                self.base.read_parameter(self.position, 20088, 0), data_type="uint16"
            ),
            hw_version=CpxBase.decode_int(
                self.base.read_parameter(self.position, 20093, 0), data_type="uint8"
            ),
        )
        return params
