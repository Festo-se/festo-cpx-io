"""VABX-A-P-EL-E12-API module implementation"""

from cpx_io.utils.logging import Logging
from cpx_io.cpx_system.cpx_base import CpxBase

from cpx_io.utils.helpers import div_ceil

from cpx_io.cpx_system.cpx_ap.cpx_ap_module import CpxApModule


class VabxAP(CpxApModule):
    """Class for VABX-A-P-EL-E12-API module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = self.base.next_output_register
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
        """read all channels as a list of bool values.
        Returns a list of all 32 coils
        """

        data0, data1 = self.base.read_reg_data(self.output_register, length=2)
        data = data1 << 16 + data0

        return [d == "1" for d in bin(data)[2:].zfill(32)[::-1]]

    @CpxBase.require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase.require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values"""
        if len(data) != 32:
            raise ValueError("Data must be list of 32 elements")
        # Make binary from list of bools
        binary_string = "".join("1" if value else "0" for value in reversed(data))
        # Convert the binary string to an integer
        integer_data = int(binary_string, 2)

        data0 = integer_data & 0xFFFF
        data1 = integer_data >> 16
        self.base.write_reg_data(data0, self.output_register)
        self.base.write_reg_data(data1, self.output_register + 1)

    @CpxBase.require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value"""
        if channel not in range(33):
            raise ValueError("Channel must be in range 0...32")

        # read current values
        data0, data1 = self.base.read_reg_data(self.output_register, length=2)
        data = data1 << 16 + data0

        mask = 1 << channel  # Compute mask, an integer with just bit 'channel' set.
        data &= ~mask  # Clear the bit indicated by the mask
        if value:
            data |= mask  # If x was True, set the bit indicated by the mask.

        data0 = data & 0xFFFF
        data1 = data >> 16
        self.base.write_reg_data(data0, self.output_register)
        self.base.write_reg_data(data1, self.output_register + 1)

    @CpxBase.require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level"""
        self.write_channel(channel, True)

    @CpxBase.require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level"""
        self.write_channel(channel, False)

    @CpxBase.require_base
    def toggle_channel(self, channel: int) -> None:
        """set one channel the inverted of current logic level"""
        data = (
            self.base.read_reg_data(self.output_register)[0] & 1 << channel
        ) >> channel
        if data == 1:
            self.clear_channel(channel)
        elif data == 0:
            self.set_channel(channel)
        else:
            raise ValueError
