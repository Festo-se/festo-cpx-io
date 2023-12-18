"""CPX-AP-4DI module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.utils.helpers import div_ceil

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule


class CpxAp4Di(CpxApModule):
    """Class for CPX-AP-*-4DI-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base.next_input_register

        self.base.next_output_register += div_ceil(self.information["Output Size"], 2)
        self.base.next_input_register += div_ceil(self.information["Input Size"], 2)

        Logging.logger.debug(
            (
                f"Configured {self} with output register {self.output_register}"
                f"and input register {self.input_register}"
            )
        )

    @CpxBase.require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values"""
        data = self.base.read_reg_data(self.input_register)[0] & 0xF
        return [d == "1" for d in bin(data)[2:].zfill(4)[::-1]]

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def configure_debounce_time(self, value: int) -> None:
        """
        The "Input debounce time" parameter defines
        when an edge change of the sensor signal shall be assumed as a logical input signal.
        In this way, unwanted signal edge changes can be suppressed
        during switching operations (bouncing of the input signal).
        Accepted values are 0: 0.1 ms; 1: 3 ms (default); 2: 10 ms; 3: 20 ms;
        """
        uid = 20014

        if not 0 <= value <= 3:
            raise ValueError("Value {value} must be between 0 and 3")

        self.base.write_parameter(self.position, uid, 0, value)
