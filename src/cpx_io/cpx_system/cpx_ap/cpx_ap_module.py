"""CPX-E-AP module implementation"""

from cpx_io.cpx_system.cpx_base import CpxBase


class CpxApModule:
    """Base class for cpx-ap modules"""

    def __init__(self):
        self.base = None
        self.position = None
        self.information = None

        self.output_register = None
        self.input_register = None

    def __repr__(self):
        return f"{self.information.get('Order Text')} at position {self.position}"

    def configure(self, base, position):
        """Set up postion and base for the module when added to cpx system""" ""
        self.base = base
        self.position = position

    def update_information(self, information):
        self.information = information

    @CpxBase.require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters"""
        fieldbus_serial_number = CpxBase.decode_int(
            self.base.read_parameter(self.position, 246, 0), data_type="uint32"
        )
        product_key = CpxBase.decode_string(
            self.base.read_parameter(self.position, 791, 0)
        )
        firmware_version = CpxBase.decode_string(
            self.base.read_parameter(self.position, 960, 0)
        )
        module_code = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20000, 0), data_type="uint32"
        )
        temp_asic = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20085, 0), data_type="int16"
        )
        logic_voltage = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20087, 0), data_type="uint16"
        )
        load_voltage = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20088, 0), data_type="uint16"
        )
        hw_version = CpxBase.decode_int(
            self.base.read_parameter(self.position, 20093, 0), data_type="uint8"
        )

        return {
            "Fieldbus serial number": fieldbus_serial_number,
            "Product Key": product_key,
            "Firmware Version": firmware_version,
            "Module Code": module_code,
            "Measured value of temperature AP-ASIC [°C]": temp_asic,
            "Current measured value of logic supply PS [mV]": logic_voltage,
            "Current measured value of load supply PL [mV]": load_voltage,
            "Hardware Version": hw_version,
        }
