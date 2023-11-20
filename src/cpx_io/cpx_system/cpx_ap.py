"""CPX AP
"""

import math

from .cpx_base import CpxBase, CpxRequestError


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
        module._initialize(self, len(self._modules))
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

        module_code = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.module_code, position)
            ),
            data_type="int32",
        )
        module_class = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.module_class, position)
            ),
            data_type="uint8",
        )
        communication_profiles = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.communication_profiles, position)
            ),
            data_type="uint16",
        )
        input_size = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.input_size, position)
            ),
            data_type="uint16",
        )
        input_channels = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.input_channels, position)
            ),
            data_type="uint16",
        )
        output_size = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.output_size, position)
            ),
            data_type="uint16",
        )
        output_channels = CpxBase._decode_int(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.output_channels, position)
            ),
            data_type="uint16",
        )
        hw_version = CpxBase._decode_int(
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
        serial_number = CpxBase._decode_hex(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.serial_number, position)
            )
        )
        product_key = CpxBase._decode_string(
            self.read_reg_data(
                *self._module_offset(_ModbusCommands.product_key, position)
            )
        )
        order_text = CpxBase._decode_string(
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
            "HW Version": hW_version,
            "FW Version": fW_version,
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
            registers = [CpxBase._encode_int(d)[0] for d in data]

        elif isinstance(data, int):
            registers = [CpxBase._encode_int(data)[0]]
            data = [data]  # needed for validation check

        elif isinstance(data, bool):
            registers = [CpxBase._encode_int(data, data_type="bool")[0]]
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
            ret = [CpxBase._decode_int([x], data_type="int16") for x in ret]

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


class _CpxApModule(CpxAp):
    """Base class for cpx-ap modules"""

    def __init__(self):
        self.base = None
        self.position = None
        self.information = None

        self.output_register = None
        self.input_register = None

    def _initialize(self, base, position):
        self.base = base
        self.position = position

    def _update_information(self, information):
        self.information = information


class CpxApEp(_CpxApModule):
    """Class for CPX-AP-EP module"""

    def _initialize(self, *args):
        super()._initialize(*args)
        self.output_register = None
        self.input_register = None

        self.base._next_output_register = _ModbusCommands.outputs[0]
        self.base._next_input_register = _ModbusCommands.inputs[0]

    @staticmethod
    def convert_uint32_to_octett(value: int) -> str:
        return f"{value & 0xFF}.{(value >> 8) & 0xFF}.{(value >> 16) & 0xFF}.{(value) >> 24 & 0xFF}"

    @CpxBase._require_base
    def read_parameters(self):
        dhcp_enable = CpxBase._decode_bool(
            self.base._read_parameter(self.position, 12000, 0)
        )

        ip_address = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12001, 0), type="uint32"
        )
        ip_address = self.convert_uint32_to_octett(ip_address)

        subnet_mask = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12002, 0), type="uint32"
        )
        subnet_mask = self.convert_uint32_to_octett(subnet_mask)

        gateway_address = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12003, 0), type="uint32"
        )
        gateway_address = self.convert_uint32_to_octett(gateway_address)

        active_ip_address = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12004, 0), type="uint32"
        )
        active_ip_address = self.convert_uint32_to_octett(active_ip_address)

        active_subnet_mask = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12005, 0), type="uint32"
        )
        active_subnet_mask = self.convert_uint32_to_octett(active_subnet_mask)

        active_gateway_address = CpxBase._decode_int(
            self.base._read_parameter(self.position, 12006, 0), type="uint32"
        )
        active_gateway_address = self.convert_uint32_to_octett(active_gateway_address)

        mac_address = ":".join(
            "{:02x}".format(x & 0xFF) + ":{:02x}".format((x >> 8) & 0xFF)
            for x in self.base._read_parameter(self.position, 12007, 0)
        )

        setup_monitoring_load_supply = CpxBase._decode_int(
            self.base._read_parameter(self.position, 20022, 0), type="uint8"
        )

        return {
            "dhcp_enable": dhcp_enable,
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "gateway_address": gateway_address,
            "active_ip_address": active_ip_address,
            "active_subnet_mask": active_subnet_mask,
            "mac_address": mac_address,
            "setup_monitoring_load_supply": setup_monitoring_load_supply,
        }


class CpxAp4Di(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

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


class CpxAp8Di(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

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


class CpxAp4AiUI(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

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
        return [CpxBase._decode_int([i], type="int16") for i in raw_data]

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
        id = 20043
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

        self.base._write_parameter(self.position, id, channel, value[signalrange])

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


class CpxAp4Di4Do(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

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
    def set_channel(self, channel: int) -> None:
        """set one channel to logic high level"""
        data = self.base.read_reg_data(self.output_register)[0] & 0xF
        self.base.write_reg_data(data | 1 << channel, self.output_register)

    @CpxBase._require_base
    def clear_channel(self, channel: int) -> None:
        """set one channel to logic low level"""
        data = self.base.read_reg_data(self.output_register)[0] & 0xF
        self.base.write_reg_data(data & ~(1 << channel), self.output_register)

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


class CpxAp4Iol(_CpxApModule):
    def _initialize(self, *args):
        super()._initialize(*args)

        self.output_register = self.base._next_output_register
        self.input_register = self.base._next_input_register

        self.base._next_output_register += math.ceil(
            self.information["Output Size"] / 2
        )
        self.base._next_input_register += math.ceil(self.information["Input Size"] / 2)
        # raise NotImplementedError("The module CPX-AP-4IOL-M12 has not yet been implemented")
