"""CPX-AP module implementations"""

import math

from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError


class _ModbusCommands:
    """Modbus start adresses used to read and write registers"""

    # holding registers
    outputs = (0, 4096)
    inputs = (5000, 4096)
    parameter = (10000, 1000)

    diagnosis = (11000, 100)
    module_count = (12000, 1)

    # module information
    module_code = (15000, 2)  # (+37*n)
    module_class = (15002, 1)  # (+37*n)
    communication_profiles = (15003, 1)  # (+37*n)
    input_size = (15004, 1)  # (+37*n)
    input_channels = (15005, 1)  # (+37*n)
    output_size = (15006, 1)  # (+37*n)
    output_channels = (15007, 1)  # (+37*n)
    hw_version = (15008, 1)  # (+37*n)
    fw_version = (15009, 3)  # (+37*n)
    serial_number = (15012, 2)  # (+37*n)
    product_key = (15014, 6)  # (+37*n)
    order_text = (15020, 17)  # (+37*n)


class CpxAp(CpxBase):
    """CPX-AP base class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._next_output_register = None
        self._next_input_register = None
        self._modules = []

        module_count = self.read_module_count()
        for i in range(module_count):
            self.add_module(information=self.read_module_information(i))

    @property
    def modules(self):
        """Function for private modules property"""
        return self._modules

    def add_module(self, information: dict):
        """Adds one module to the base. This is required to use the module.
        The module must be identified by either the module code {"Module Code": 8323}
        or the full module order text {"Order Text": "CPX-AP-I-EP-M12"}
        """
        module_code = information.get("Module Code")
        order_text = information.get("Order Text")

        if module_code == 8323 or order_text == "CPX-AP-I-EP-M12":
            module = CpxApEp()
        elif module_code == 8199 or order_text == "CPX-AP-I-8DI-M8-3P":
            module = CpxAp8Di()
        elif module_code == 8197 or order_text == "CPX-AP-I-4DI4DO-M12-5P":
            module = CpxAp4Di4Do()
        elif module_code == 8202 or order_text == "CPX-AP-I-4AI-U-I-RTD-M12":
            module = CpxAp4AiUI()
        elif module_code == 8201 or order_text == "CPX-AP-I-4IOL-M12":
            module = CpxAp4Iol()
        elif module_code == 8198 or order_text == "CPX-AP-I-4DI-M8-3P":
            module = CpxAp4Di()
        else:
            raise NotImplementedError(
                "This module is not yet implemented or not available"
            )

        module._update_information(information)
        module.configure(self, len(self._modules))
        self.modules.append(module)
        return module

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer"""
        return self.read_reg_data(*_ModbusCommands.module_count)[0]

    def _module_offset(self, modbus_command, module):
        register, length = modbus_command
        return ((register + 37 * module), length)

    def read_module_information(self, position):
        """Reads and returns detailed information for a specific IO module"""

        module_code = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.module_code, position)
            ),
            data_type="int32",
        )
        module_class = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.module_class, position)
            ),
            data_type="uint8",
        )
        communication_profiles = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.communication_profiles, position)
            ),
            data_type="uint16",
        )
        input_size = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.input_size, position)
            ),
            data_type="uint16",
        )
        input_channels = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.input_channels, position)
            ),
            data_type="uint16",
        )
        output_size = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.output_size, position)
            ),
            data_type="uint16",
        )
        output_channels = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.output_channels, position)
            ),
            data_type="uint16",
        )
        hw_version = CpxBase.decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.hw_version, position)
            ),
            data_type="uint8",
        )
        fw_version = ".".join(
            str(x)
            for x in self.read_reg_data(
                *self._module_offset(_ModbusCommands.fw_version, position)
            )
        )
        serial_number = CpxBase.decode_hex(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.serial_number, position)
            )
        )
        product_key = CpxBase.decode_string(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.product_key, position)
            )
        )
        order_text = CpxBase.decode_string(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.order_text, position)
            )
        )

        return {
            "Module Code": module_code,
            "Module Class": module_class,
            "Communication Profiles": communication_profiles,
            "Input Size": input_size,
            "Input Channels": input_channels,
            "Output Size": output_size,
            "Output Channeles": output_channels,
            "HW Version": hw_version,
            "FW Version": fw_version,
            "Serial Number": serial_number,
            "Product Key": product_key,
            "Order Text": order_text,
        }

    def _write_parameter(
        self, position: int, param_id: int, instance: int, data: list | int | bool
    ) -> None:
        """Write parameters via module position, param_id, instance (=channel) and data to write
        Data must be a list of (signed) 16 bit values or one 16 bit (signed) value
        Returns None if successful or raises "CpxRequestError" if request denied
        """
        if isinstance(data, list):
            registers = [CpxBase.encode_int(d)[0] for d in data]

        elif isinstance(data, int):
            registers = [CpxBase.encode_int(data)[0]]
            data = [data]  # needed for validation check

        elif isinstance(data, bool):
            registers = [CpxBase.encode_int(data, data_type="bool")[0]]
            data = [int(data)]  # needed for validation check

        else:
            raise ValueError("Data must be of type list, int or bool")

        param_reg = _ModbusCommands.parameter[0]

        # Strangely this sending has to be repeated several times,
        # actually it is tried up to 10 times.
        # This seems to work but it's not good
        for i in range(10):
            self.write_reg_data(position + 1, param_reg)
            self.write_reg_data(param_id, param_reg + 1)
            self.write_reg_data(instance, param_reg + 2)
            self.write_reg_data(len(registers), param_reg + 3)

            self.write_reg_data(registers, param_reg + 10, len(registers))

            self.write_reg_data(2, param_reg + 3)  # 1=read, 2=write

            exe_code = 0
            while exe_code < 16:
                exe_code = self.read_reg_data(param_reg + 3)[0]
                # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
                if exe_code == 4:
                    raise CpxRequestError

            # Validation check according to datasheet
            data_length = math.ceil(self.read_reg_data(param_reg + 4)[0] / 2)
            ret = self.read_reg_data(param_reg + 10, data_length)
            ret = [CpxBase.decode_int([x], data_type="int16") for x in ret]

            if all(r == d for r, d in zip(ret, data)):
                break

        if i >= 9:
            raise CpxRequestError(
                "Parameter might not have been written correctly after 10 tries"
            )

    def _read_parameter(self, position: int, param_id: int, instance: int) -> list:
        """Read parameters via module position, param_id, instance (=channel)
        Returns data as list if successful or raises "CpxRequestError" if request denied
        """

        param_reg = _ModbusCommands.parameter[0]

        self.write_reg_data(
            position + 1, param_reg
        )  # module index starts with 1 on first module ("position" starts with 0)
        self.write_reg_data(param_id, param_reg + 1)
        self.write_reg_data(instance, param_reg + 2)

        self.write_reg_data(1, param_reg + 3)  # 1=read, 2=write

        exe_code = 0
        while exe_code < 16:
            exe_code = self.read_reg_data(param_reg + 3)[
                0
            ]  # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
            if exe_code == 4:
                raise CpxRequestError

        # data_length from register 10004 is bytewise. 2 bytes = 1 register.
        # But 1 byte also has to read one register with integer division "//"
        # will lead to rounding down, this needs to be rounded up.
        # Therefore math.ceil() is used
        data_length = math.ceil(self.read_reg_data(param_reg + 4)[0] / 2)

        data = self.read_reg_data(param_reg + 10, data_length)
        return data


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
        self.base = base
        self.position = position

    def _update_information(self, information):
        self.information = information

    @CpxBase._require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters"""
        fieldbus_serial_number = CpxBase.decode_int(
            self.base._read_parameter(self.position, 246, 0), data_type="uint32"
        )
        product_key = CpxBase.decode_string(
            self.base._read_parameter(self.position, 791, 0)
        )
        firmware_version = CpxBase.decode_string(
            self.base._read_parameter(self.position, 960, 0)
        )
        module_code = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20000, 0), data_type="uint32"
        )
        temp_asic = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20085, 0), data_type="int16"
        )
        logic_voltage = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20087, 0), data_type="uint16"
        )
        load_voltage = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20088, 0), data_type="uint16"
        )
        hw_version = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20093, 0), data_type="uint8"
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


class CpxApEp(CpxApModule):
    """Class for CPX-AP-EP module"""

    def configure(self, *args):
        super().configure(*args)
        self.output_register = None
        self.input_register = None

        self.base._next_output_register = _ModbusCommands.outputs[0]
        self.base._next_input_register = _ModbusCommands.inputs[0]

    @staticmethod
    def convert_uint32_to_octett(value: int) -> str:
        """Convert one uint32 value to octett. Usually used for displaying ip addresses."""
        return f"{value & 0xFF}.{(value >> 8) & 0xFF}.{(value >> 16) & 0xFF}.{(value) >> 24 & 0xFF}"

    @CpxBase._require_base
    def read_ap_parameter(self) -> dict:
        raise NotImplementedError(
            "CPX-AP-EP module has no AP parameters. Use 'read_parameters()' instead"
        )

    @CpxBase._require_base
    def read_parameters(self):
        """Read parameters from EP module"""
        dhcp_enable = CpxBase.decode_bool(
            self.base._read_parameter(self.position, 12000, 0)
        )

        ip_address = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12001, 0), data_type="uint32"
        )
        ip_address = self.convert_uint32_to_octett(ip_address)

        subnet_mask = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12002, 0), data_type="uint32"
        )
        subnet_mask = self.convert_uint32_to_octett(subnet_mask)

        gateway_address = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12003, 0), data_type="uint32"
        )
        gateway_address = self.convert_uint32_to_octett(gateway_address)

        active_ip_address = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12004, 0), data_type="uint32"
        )
        active_ip_address = self.convert_uint32_to_octett(active_ip_address)

        active_subnet_mask = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12005, 0), data_type="uint32"
        )
        active_subnet_mask = self.convert_uint32_to_octett(active_subnet_mask)

        active_gateway_address = CpxBase.decode_int(
            self.base._read_parameter(self.position, 12006, 0), data_type="uint32"
        )
        active_gateway_address = self.convert_uint32_to_octett(active_gateway_address)

        mac_address = ":".join(
            "{:02x}".format(x & 0xFF) + ":{:02x}".format((x >> 8) & 0xFF)
            for x in self.base._read_parameter(self.position, 12007, 0)
        )

        setup_monitoring_load_supply = CpxBase.decode_int(
            [(self.base._read_parameter(self.position, 20022, 0)[0] << 8) & 0xFF],
            data_type="uint8",
        )  # TODO: shifting should not be required

        return {
            "dhcp_enable": dhcp_enable,
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "gateway_address": gateway_address,
            "active_ip_address": active_ip_address,
            "active_subnet_mask": active_subnet_mask,
            "active_gateway_address": active_gateway_address,
            "mac_address": mac_address,
            "setup_monitoring_load_supply": setup_monitoring_load_supply,
        }


class CpxAp4Di(CpxApModule):
    """Class for CPX-AP-*-4DI-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)

    @CpxBase._require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values"""
        data = self.base.read_reg_data(self.input_register)[0] & 0xF
        return [d == "1" for d in bin(data)[2:].zfill(4)[::-1]]

    @CpxBase._require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase._require_base
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

        self.base._write_parameter(self.position, uid, 0, value)


class CpxAp8Di(CpxApModule):
    """Class for CPX-AP-*-8DI-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)

    @CpxBase._require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values"""
        data = self.base.read_reg_data(self.input_register)[0]
        return [d == "1" for d in bin(data)[2:].zfill(8)[::-1]]

    @CpxBase._require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase._require_base
    def configure_debounce_time(self, value: int) -> None:
        """The "Input debounce time" parameter defines
        when an edge change of the sensor signal shall be assumed as a logical input signal.
        In this way, unwanted signal edge changes can be suppressed
        during switching operations (bouncing of the input signal).
        Accepted values are 0: 0.1 ms; 1: 3 ms (default); 2: 10 ms; 3: 20 ms;
        """
        uid = 20014

        if not 0 <= value <= 3:
            raise ValueError("Value {value} must be between 0 and 3")

        self.base._write_parameter(self.position, uid, 0, value)


class CpxAp4AiUI(CpxApModule):
    """Class for CPX-AP-*-4AI-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = None
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)

    @CpxBase._require_base
    def read_channels(self) -> list[int]:
        """read all channels as a list of (signed) integers"""
        raw_data = self.base.read_reg_data(self.input_register, length=4)
        return [CpxBase.decode_int([i], data_type="int16") for i in raw_data]

    @CpxBase._require_base
    def read_channel(self, channel: int) -> bool:
        """read back the value of one channel"""
        return self.read_channels()[channel]

    @CpxBase._require_base
    def configure_channel_temp_unit(self, channel: int, unit: str) -> None:
        """
        set the channel temperature unit ("C": Celsius (default), "F": Fahrenheit, "K": Kelvin)
        """
        uid = 20032
        value = {
            "C": 0,
            "F": 1,
            "K": 2,
        }
        if unit not in value:
            raise ValueError(f"'{unit}' is not an option. Choose from {value.keys()}")

        self.base._write_parameter(self.position, uid, channel, value[unit])

    @CpxBase._require_base
    def configure_channel_range(self, channel: int, signalrange: str) -> None:
        """set the signal range and type of one channel"""
        reg_id = 20043
        value = {
            "None": 0,
            "-10-+10V": 1,
            "-5-+5V": 2,
            "0-10V": 3,
            "1-5V": 4,
            "0-20mA": 5,
            "4-20mA": 6,
            "0-500R": 7,
            "PT100": 8,
            "NI100": 9,
        }
        if signalrange not in value:
            raise ValueError(
                f"'{signalrange}' is not an option. Choose from {value.keys()}"
            )

        self.base._write_parameter(self.position, reg_id, channel, value[signalrange])

    @CpxBase._require_base
    def configure_channel_limits(
        self, channel: int, upper: int | None = None, lower: int | None = None
    ) -> None:
        """
        Set the channel upper and lower limits (Factory setting -> upper: 32767, lower: -32768)
        This will immediately set linear scaling to true
        because otherwise the limits are not stored.
        """

        self.configure_linear_scaling(channel, True)

        upper_id = 20044
        lower_id = 20045

        if isinstance(lower, int):
            if not -32768 <= lower <= 32767:
                raise ValueError(
                    "Values for low {low} must be between -32768 and 32767"
                )
        if isinstance(upper, int):
            if not -32768 <= upper <= 32767:
                raise ValueError(
                    "Values for high {high} must be between -32768 and 32767"
                )

        if lower == None and isinstance(upper, int):
            self.base._write_parameter(self.position, upper_id, channel, upper)
        elif upper == None and isinstance(lower, int):
            self.base._write_parameter(self.position, lower_id, channel, lower)
        elif isinstance(upper, int) and isinstance(lower, int):
            self.base._write_parameter(self.position, upper_id, channel, upper)
            self.base._write_parameter(self.position, lower_id, channel, lower)
        else:
            raise ValueError("Value must be given for upper, lower or both")

    @CpxBase._require_base
    def configure_hysteresis_limit_monitoring(self, channel: int, value: int) -> None:
        """Hysteresis for measured value monitoring (Factory setting: 100)
        Value must be uint16
        """
        uid = 20046
        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"Value {value} must be between 0 and 65535 (uint16)")

        self.base._write_parameter(self.position, uid, channel, value)

    @CpxBase._require_base
    def configure_channel_smoothing(self, channel: int, smoothing_power: int) -> None:
        """set the signal smoothing of one channel. Smoothing is over 2^n values where n is
        smoothing_power. Factory setting: 5 (2^5 = 32 values)
        """
        uid = 20107
        if smoothing_power > 15:
            raise ValueError(f"'{smoothing_power}' is not an option")

        self.base._write_parameter(self.position, uid, channel, smoothing_power)

    @CpxBase._require_base
    def configure_linear_scaling(self, channel: int, state: bool) -> None:
        """Set linear scaling (Factory setting "False")"""
        uid = 20111

        self.base._write_parameter(self.position, uid, channel, int(state))


class CpxAp4Di4Do(CpxApModule):
    """Class for CPX-AP-*-4DI4DO-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)

    @CpxBase._require_base
    def read_channels(self) -> list[bool]:
        """read all channels as a list of bool values.
        Returns a list of 8 elements where the first 4 elements are the input channels 0..3
        and the last 4 elements are the output channels 0..3
        """
        data = self.base.read_reg_data(self.input_register)[0] & 0xF
        data |= (self.base.read_reg_data(self.output_register)[0] & 0xF) << 4
        return [d == "1" for d in bin(data)[2:].zfill(8)[::-1]]

    @CpxBase._require_base
    def read_channel(self, channel: int, output_numbering=False) -> bool:
        """read back the value of one channel
        Optional parameter 'output_numbering' defines
        if the outputs are numbered with the inputs ("True", default),
        so the range of output channels is 4..7 (as 0..3 are the input channels).
        If "False", the outputs are numbered from 0..3, the inputs cannot be accessed this way.
        """
        if output_numbering:
            channel -= 4
        return self.read_channels()[channel]

    @CpxBase._require_base
    def write_channels(self, data: list[bool]) -> None:
        """write all channels with a list of bool values"""
        if len(data) != 4:
            raise ValueError("Data must be list of four elements")
        # Make binary from list of bools
        binary_string = "".join("1" if value else "0" for value in reversed(data))
        # Convert the binary string to an integer
        integer_data = int(binary_string, 2)
        self.base.write_reg_data(integer_data, self.output_register)

    @CpxBase._require_base
    def write_channel(self, channel: int, value: bool) -> None:
        """set one channel to logic value"""
        data = (
            self.base.read_reg_data(self.output_register)[0] & 0xF
        )  # read current value
        mask = 1 << channel  # Compute mask, an integer with just bit 'channel' set.
        data &= ~mask  # Clear the bit indicated by the mask
        if value:
            data |= mask  # If x was True, set the bit indicated by the mask.

        self.base.write_reg_data(data, self.output_register)

    @CpxBase._require_base
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level"""
        self.write_channel(channel, True)

    @CpxBase._require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level"""
        self.write_channel(channel, False)

    @CpxBase._require_base
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

    @CpxBase._require_base
    def configure_debounce_time(self, value: int) -> None:
        """The "Input debounce time" parameter defines
        when an edge change of the sensor signal shall be assumed as a logical input signal.
        In this way, unwanted signal edge changes can be suppressed during switching operations
        (bouncing of the input signal).
        Accepted values are 0: 0.1 ms; 1: 3 ms (default); 2: 10 ms; 3: 20 ms;
        """
        uid = 20014

        if not 0 <= value <= 3:
            raise ValueError("Value {value} must be between 0 and 3")

        self.base._write_parameter(self.position, uid, 0, value)

    @CpxBase._require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Accepted values are
        0: Load supply monitoring inactive
        1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
        2: Load supply monitoring active
        """
        uid = 20022

        if not 0 <= value <= 2:
            raise ValueError("Value {value} must be between 0 and 2")

        self.base._write_parameter(self.position, uid, 0, value)

    @CpxBase._require_base
    def configure_behaviour_in_fail_state(self, value: int) -> None:
        """Accepted values are
        0: Reset Outputs (default)
        1: Hold last state
        """
        uid = 20052

        if not 0 <= value <= 1:
            raise ValueError("Value {value} must be between 0 and 2")

        self.base._write_parameter(self.position, uid, 0, value)


class CpxAp4Iol(CpxApModule):
    """Class for CPX-AP-*-4IOL-* module"""

    def __getitem__(self, key):
        return self.read_channel(key)

    def __setitem__(self, key, value):
        self.write_channel(key, value)

    def configure(self, *args):
        super().configure(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)

    @CpxBase._require_base
    def read_ap_parameter(self) -> dict:
        """Read AP parameters"""
        ap_dict = super().read_ap_parameter()

        variant_dict = {
            8201: "variant 8",
            8205: "variant 8 OE",
            8206: "variant 2",
            8207: "variant 2 OE",
            8208: "variant 4",
            8209: "variant 4 OE",
            8210: "variant 16",
            8211: "variant 16 OE",
            8212: "variant 23",
            8213: "variant 32 OE",
        }
        # TODO: Why is this UINT16 stored in the second byte of the parameter?
        io_link_variant = CpxBase.decode_int(
            self.base._read_parameter(self.position, 20090, 0)[:-1], data_type="uint16"
        )

        activation_operating_voltage = CpxBase.decode_bool(
            self.base._read_parameter(self.position, 20097, 0)
        )

        ap_dict["IO-Link variant"] = variant_dict[io_link_variant]
        ap_dict["Operating Supply"] = activation_operating_voltage
        return ap_dict

    @CpxBase._require_base
    def read_channels(self) -> list[int]:
        """read all IO-Link input data
        register order is [msb, ... , ... , lsb]
        """
        module_input_size = math.ceil(self.information["Input Size"] / 2) - 2

        data = self.base.read_reg_data(self.input_register, length=module_input_size)
        data = [
            CpxBase.decode_int([d], data_type="uint16", byteorder="little")
            for d in data
        ]

        channel_size = (module_input_size) // 4

        channels = [
            data[: channel_size * 1],
            data[channel_size * 1 : channel_size * 2],
            data[channel_size * 2 : channel_size * 3],
            data[channel_size * 3 :],
        ]
        return channels

    @CpxBase._require_base
    def read_channel(self, channel: int) -> bool:
        """read back the register values of one channel
        register order is [msb, ... , ... , lsb]
        channel order is [0, 1, 2, 3]
        """
        return self.read_channels()[channel]

    @CpxBase._require_base
    def write_channel(self, channel: int, data: list[int]) -> None:
        """set one channel to list of uint16 values
        channel order is [0, 1, 2, 3]
        """
        module_output_size = math.ceil(self.information["Output Size"] / 2)
        channel_size = (module_output_size) // 4

        register_data = [
            CpxBase.encode_int(d, data_type="uint16", byteorder="little")[0]
            for d in data
        ]
        self.base.write_reg_data(
            register_data, self.output_register + channel_size * channel
        )

    @CpxBase._require_base
    def read_pqi(self, channel: int | None = None) -> dict | list[dict]:
        """Returns Port Qualifier Information for each channel. If no channel is given,
        returns a list of PQI dict for all channels"""
        data45 = self.base.read_reg_data(self.input_register + 16)[0]
        data67 = self.base.read_reg_data(self.input_register + 17)[0]
        data = [
            data45 & 0xFF,
            (data45 & 0xFF00) >> 8,
            data67 & 0xFF,
            (data67 & 0xFF00) >> 8,
        ]

        channels_pqi = []

        for d in data:
            port_qualifier = (
                "input data is valid"
                if (d & 0b10000000) >> 7
                else "input data is invalid"
            )
            device_error = (
                "there is at least one error or warning on the device or port"
                if (d & 0b01000000) >> 6
                else "there are no errors or warnings on the device or port"
            )
            dev_com = (
                "device is in status PREOPERATE or OPERATE"
                if (d & 0b00100000) >> 5
                else "device is not connected or not yet in operation"
            )

            channels_pqi.append(
                {
                    "Port Qualifier": port_qualifier,
                    "Device Error": device_error,
                    "DevCOM": dev_com,
                }
            )
        if channel is None:
            return channels_pqi

        return channels_pqi[channel]

    @CpxBase._require_base
    def configure_monitoring_load_supply(self, value: int) -> None:
        """Accepted values are
        0: Load supply monitoring inactive
        1: Load supply monitoring active, diagnosis suppressed in case of switch-off (default)
        2: Load supply monitoring active
        """
        uid = 20022

        if not 0 <= value <= 2:
            raise ValueError("Value {value} must be between 0 and 2")

        self.base._write_parameter(self.position, uid, 0, value)

    @CpxBase._require_base
    def configure_target_cycle_time(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Target cycle time in ms for the given channels. If no channel is specified,
        target cycle time is applied to all channels. Possible cycle time values:
        -  0: as fast as possible (default)
        - 16: 1.6 ms
        - 32: 3.2 ms
        - 48: 4.8 ms
        - 68: 8.0 ms
        - 73: 10.0 ms
        - 78: 12.0 ms
        - 88: 16.0 ms
        - 98: 20.0 ms
        - 133: 40.0 ms
        - 158: 80.0 ms
        - 183: 120.0 ms
        """
        uid = 20049

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = [0, 16, 32, 48, 68, 73, 78, 88, 98, 133, 158, 183]

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, value)

    @CpxBase._require_base
    def configure_device_lost_diagnostics(
        self, value: bool, channel: int | list | None = None
    ) -> None:
        """Activation of diagnostics for IO-Link device lost (default: True) for given channel. If no
        channel is provided, value will be written to all channels."""

        uid = 20050

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, int(value))

    @CpxBase._require_base
    def configure_port_mode(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Port mode. Available values:
        - 0: DEACTIVATED (factory setting)
        - 1: IOL_MANUAL
        - 2: IOL_AUTOSTART
        - 3: DI_CQ
        - 97: PREOPERATE (Only supported in combination with IO-Link V1.1 devices)
        """

        uid = 20071

        if channel is None:
            channel = [0, 1, 2, 3]

        allowed_values = [0, 1, 2, 3, 97]

        if value not in allowed_values:
            raise ValueError("Value {value} not valid")

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, value)

    @CpxBase._require_base
    def configure_review_and_backup(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Review and backup. Available values:
        - 0: no test (factory setting)
        - 1: device compatible V1.0
        - 2: device compatible V1.1
        - 3: device compatible V1.1 Data storage Backup+ Restore
        - 4: device compatible V1.1 Data storage Restore
        Changes only become effective when the port mode is changed (ID 20071).
        """

        uid = 20072

        if channel is None:
            channel = [0, 1, 2, 3]

        if not 0 <= value <= 4:
            raise ValueError("Value {value} must be between 0 and 4")

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, value)

    @CpxBase._require_base
    def configure_target_vendor_id(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Target Vendor ID
        Changes only become effective when the port mode is changed (ID 20071)."""

        uid = 20073

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, value)

    @CpxBase._require_base
    def configure_setpoint_device_id(
        self, value: int, channel: int | list | None = None
    ) -> None:
        """Setpoint device ID
        Changes only become effective when the port mode is changed (ID 20071)."""

        uid = 20080

        if channel is None:
            channel = [0, 1, 2, 3]

        if isinstance(channel, int):
            channel = [channel]

        for ch in channel:
            self.base._write_parameter(self.position, uid, ch, value)

    @CpxBase._require_base
    def read_fieldbus_parameters(self) -> list[dict]:
        """Read all fieldbus parameters (status/information) for all channels
        Returns a dict of parameters for every channel.
        """

        channel_params = []

        port_status_dict = {
            0: "NO_DEVICE",
            1: "DEACTIVATED",
            2: "PORT_DIAG",
            3: "PREOPERATE",
            4: "OPERATE",
            5: "DI_CQ",
            6: "DO_CQ",
            254: "PORT_POWER_OFF",
            255: "NOT_AVAILABLE",
        }
        transmission_rate_dict = {0: "not detected", 1: "COM1", 2: "COM2", 3: "COM3"}

        for i in range(4):
            port_status_information = port_status_dict.get(
                CpxBase.decode_int(
                    self.base._read_parameter(self.position, 20074, i),
                    data_type="uint8",
                )
            )

            revision_id = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20075, i),
                data_type="uint8",
            )

            transmission_rate = transmission_rate_dict.get(
                CpxBase.decode_int(
                    self.base._read_parameter(self.position, 20076, i),
                    data_type="uint8",
                )
            )

            actual_cycle_time = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20077, i),
                data_type="uint16",
            )

            actual_vendor_id = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20078, i),
                data_type="uint16",
            )

            actual_device_id = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20079, i),
                data_type="uint32",
            )

            input_data_length = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20108, i),
                data_type="uint8",
            )

            output_data_length = CpxBase.decode_int(
                self.base._read_parameter(self.position, 20109, i),
                data_type="uint8",
            )

            channel_params.append(
                {
                    "Port status information": port_status_information,
                    "Revision ID": revision_id,
                    "Transmission rate": transmission_rate,
                    "Actual cycle time [in 100 us]": actual_cycle_time,
                    "Actual vendor ID": actual_vendor_id,
                    "Actual device ID": actual_device_id,
                    "Input data length": input_data_length,
                    "Output data length": output_data_length,
                }
            )

        return channel_params
