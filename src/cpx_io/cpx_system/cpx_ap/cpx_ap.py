"""CPX-AP module implementations"""

import json
import struct
from typing import Any, List
from dataclasses import dataclass
import os
import platformdirs
import requests
from cpx_io.cpx_system.cpx_base import CpxBase, CpxRequestError
from cpx_io.cpx_system.cpx_ap.builder.ap_module_builder import build_ap_module
from cpx_io.cpx_system.cpx_ap.ap_module import ApModule
from cpx_io.cpx_system.cpx_ap.ap_product_categories import ProductCategory
from cpx_io.cpx_system.cpx_ap.ap_supported_functions import (
    SUPPORTED_PRODUCT_FUNCTIONS_DICT,
)

from cpx_io.cpx_system.cpx_ap import ap_modbus_registers
from cpx_io.cpx_system.cpx_ap.ap_docu_generator import generate_system_information_file
from cpx_io.cpx_system.cpx_ap.ap_parameter import (
    Parameter,
    parameter_pack,
    parameter_unpack,
)
from cpx_io.utils.helpers import div_ceil
from cpx_io.utils.boollist import bytes_to_boollist
from cpx_io.utils.logging import Logging


class CpxAp(CpxBase):
    """CPX-AP base class"""

    @dataclass
    class ApInformation:
        """Information of AP Module"""

        # pylint: disable=too-many-instance-attributes
        module_code: int = None
        module_class: int = None
        communication_profiles: int = None
        input_size: int = None
        input_channels: int = None
        output_size: int = None
        output_channels: int = None
        hw_version: int = None
        fw_version: str = None
        serial_number: str = None
        product_key: str = None
        order_text: str = None

    @dataclass
    class Diagnostics(CpxBase.BitwiseReg8):
        """Diagnostic information"""

        # pylint: disable=too-many-instance-attributes
        degree_of_severity_information: bool
        degree_of_severity_maintenance: bool
        degree_of_severity_warning: bool
        degree_of_severity_error: bool
        _4: None  # spacer for not-used bit
        _5: None  # spacer for not-used bit
        module_present: bool
        _7: None  # spacer for not-used bit

    def __init__(
        self,
        timeout: float = 0.1,
        apdd_path: str = None,
        docu_path: str = None,
        generate_docu: bool = True,
        **kwargs,
    ):
        """Constructor of the CpxAp class.
        This generates an individual documentation in the <docu_path>. This path is individual for
        each operating system. You can either set the path as a parameter or print <self.docu_path>
        to see the path for your system. CPX-AP systems will be setup automatically from the device
        description files (APDD) of the modules. If there is a change in the system a reconnect is
        always required and this will also update the documentation. The filename will always
        include the ip-address, so you can have multiple systems with individual documentations.

        :param timeout: Modbus timeout (in s) that should be configured on the slave
        :type timeout: float
        :param apdd_path: (optional) Path where the description files of the modules are saved
        :type apdd_path: str
        :param docu_path: (optional) Path where the documentation files are saved
        :type docu_path: str
        :param generate_docu: (optional) parameter to disable the generation of the documentation
            this is useful for big systems when the generation takes too long
        :type generate_docu: bool
        """
        super().__init__(**kwargs)
        if not self.connected():
            return

        self.next_output_register = None
        self.next_input_register = None

        self.global_diagnosis_register = ap_modbus_registers.DIAGNOSIS.register_address
        self.next_diagnosis_register = self.global_diagnosis_register + 6

        self.set_timeout(int(timeout * 1000))

        if apdd_path:
            self._apdd_path = apdd_path
        else:
            self._apdd_path = self.create_apdd_path()

        if docu_path:
            self._docu_path = docu_path
        else:
            self._docu_path = self.create_docu_path()

        apdds = os.listdir(self._apdd_path)

        for i in range(self.read_module_count()):
            info = self.read_apdd_information(i)
            apdd_name = (
                info.order_text + "_v" + info.fw_version.replace(".", "-") + ".json"
            )

            # if correct apdd exists in folder, use it!
            if apdd_name in apdds:
                with open(
                    self._apdd_path + "/" + apdd_name, "r", encoding="utf-8"
                ) as f:
                    module_apdd = json.load(f)
                Logging.logger.debug(
                    f"Loaded apdd {apdd_name} for module index {i} from filesystem"
                )

            # if it does not exist, load it from the module
            else:
                module_apdd = self._grab_apdd(
                    self.ip_address, i, self._apdd_path, info.fw_version
                )
                Logging.logger.debug(
                    f"Loaded apdd {apdd_name} from module index {i} and saved to {self._apdd_path}"
                )

            module = build_ap_module(module_apdd, info.module_code)
            self._add_module(module, info)

        if generate_docu:
            generate_system_information_file(self)

    def connected(self) -> bool:
        """Returns information about connection status"""
        return self.client.connected

    def delete_apdds(self) -> None:
        """Delete all downloaded apdds in the apdds path.
        This forces a refresh when a new CPX-AP System is instantiated
        """
        if os.path.isdir(self._apdd_path):
            for file_name in os.listdir(self._apdd_path):
                file_path = os.path.join(self._apdd_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            Logging.logger.debug(f"Deleted all apdds from {self._apdd_path}")
        else:
            Logging.logger.warning("Apdd folder does not exist. Nothing was deleted")

    @staticmethod
    def create_apdd_path() -> str:
        """Creates the apdd directory depending on the operating system and returns the path"""
        app_directory = platformdirs.user_data_dir(
            appname="festo-cpx-io", appauthor="Festo"
        )

        # Create the directory if it doesn't exist
        apdd_path = os.path.join(app_directory, "apdds")
        os.makedirs(apdd_path, exist_ok=True)
        return apdd_path

    @staticmethod
    def create_docu_path() -> str:
        """Creates the docu directory depending on the operating system and returns the path"""
        app_directory = platformdirs.user_data_dir(
            appname="festo-cpx-io", appauthor="Festo"
        )

        # Create the directory if it doesn't exist
        docu_path = os.path.join(app_directory, "docu")
        os.makedirs(docu_path, exist_ok=True)
        return docu_path

    @property
    def modules(self) -> List[ApModule]:
        """getter function for private modules property"""
        return self._modules

    @property
    def apdd_path(self):
        """getter function for private apdd_path property"""
        return self._apdd_path

    @property
    def docu_path(self):
        """getter function for private docu_path property"""
        return self._docu_path

    def set_timeout(self, timeout_ms: int) -> None:
        """Sets the modbus timeout to the provided value

        :param timeout_ms: Modbus timeout in ms (milli-seconds)
        :type timeout_ms: int
        """
        if 0 < timeout_ms < 100:
            timeout_ms = 100
            Logging.logger.warning(
                f"Setting the timeout below 100 ms can lead to "
                f"exclusion from the system. To prevent this, "
                f"the timeout is limited to a minimum of {timeout_ms} ms"
            )
        Logging.logger.info(f"Setting modbus timeout to {timeout_ms} ms")
        value_to_write = timeout_ms.to_bytes(length=4, byteorder="little")
        self.write_reg_data(
            value_to_write, ap_modbus_registers.TIMEOUT.register_address
        )

        # Check if it actually succeeded
        indata = int.from_bytes(
            self.read_reg_data(*ap_modbus_registers.TIMEOUT),
            byteorder="little",
            signed=False,
        )
        if indata != timeout_ms:
            Logging.logger.error("Setting of modbus timeout was not successful")

    def _add_module(self, module: ApModule, info: ApInformation) -> None:
        """Adds one module to the base. This is required to use the module.
        The module must be identified by the module code in info.

        :param module: Object of the already built module
        :type module: ApModule
        :param info: Object containing the read-out info from the module
        :type info: ApInformation
        """
        module.information = info

        # if the module is a bus-module, the in- and output registers have to be set initially
        if info.module_class == ProductCategory.CONTROLLERS.value:
            self.next_output_register = ap_modbus_registers.OUTPUTS.register_address
            self.next_input_register = ap_modbus_registers.INPUTS.register_address

        module.configure(self, len(self._modules))
        self._modules.append(module)
        self.update_module_names()
        Logging.logger.debug(f"Added module {module.name} ({type(module).__name__})")
        return module

    def read_module_count(self) -> int:
        """Reads and returns IO module count as integer

        :return: Number of the total amount of connected modules
        :rtype: int
        """
        reg = self.read_reg_data(*ap_modbus_registers.MODULE_COUNT)
        value = int.from_bytes(reg, byteorder="little")
        Logging.logger.debug(f"Total module count: {value}")
        return value

    def print_system_information(self) -> None:
        """Prints all parameters from all modules"""
        print("\nInformation")
        print(f"* IP-Address: {self.ip_address}")
        print(f"* Number of modules: {len(self.modules)}")
        print(f"* Docu Path: {self.docu_path}")
        print(f"* APDD Path: {self.apdd_path}")
        for m in self.modules:
            print(f"\n\nModule {m}:")
            print("* Information:")
            print(f"   > {m.apdd_information.description}\n")
            print("* Available Functions: ")
            for function_name in SUPPORTED_PRODUCT_FUNCTIONS_DICT:
                if (
                    m.is_function_supported(function_name)
                    and function_name != "configure"
                ):
                    print(f"    > {function_name}")

            print("\n* Available Parameters: ")
            print(
                "   > ID      Name                                              R/W   Type       "
            )
            print(
                "   > ---------------------------------------------------------------------------"
            )
            for p in m.module_dicts.parameters.values():
                print(f"   > {p}")

    def print_system_state(self) -> None:
        """Prints all parameters and channels from every module"""
        for m in self.modules:
            print(f"\n\nModule {m}:")
            for i, p in m.module_dicts.parameters.items():
                r_w = "R/W" if p.is_writable else "R"
                print(
                    f"{f'  > Read {p.name} (ID {i}):':<64}"
                    f"{f'{m.read_module_parameter(i)} {p.unit}':<32}"
                    f"({r_w})"
                )

            if m.is_function_supported("read_channels"):
                print(f"\n  > Read Channels: {m.read_channels()}")
            else:
                print("\t(No readable channels available)")

    def read_apdd_information(self, position: int) -> ApInformation:
        """Reads and returns detailed information for a specific IO module

        :param position: Module position index starting with 0
        :type position: int
        :return: ApInformation object containing all the module information from the module
        :rtype: ApInformation
        """

        info = self.ApInformation(
            module_code=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.MODULE_CODE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            module_class=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.MODULE_CLASS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            communication_profiles=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(
                        ap_modbus_registers.COMMUNICATION_PROFILE, position
                    )
                ),
                byteorder="little",
                signed=False,
            ),
            input_size=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.INPUT_SIZE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            output_channels=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.INPUT_CHANNELS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            output_size=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.OUTPUT_SIZE, position)
                ),
                byteorder="little",
                signed=False,
            ),
            input_channels=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.OUTPUT_CHANNELS, position)
                ),
                byteorder="little",
                signed=False,
            ),
            hw_version=int.from_bytes(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.HW_VERSION, position)
                ),
                byteorder="little",
                signed=False,
            ),
            fw_version=".".join(
                str(x)
                for x in struct.unpack(
                    "<HHH",
                    self.read_reg_data(
                        *self._module_offset(ap_modbus_registers.FW_VERSION, position)
                    ),
                )
            ),
            serial_number=hex(
                int.from_bytes(
                    self.read_reg_data(
                        *self._module_offset(
                            ap_modbus_registers.SERIAL_NUMBER, position
                        )
                    ),
                    byteorder="little",
                    signed=False,
                )
            ),
            product_key=(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.PRODUCT_KEY, position)
                )
                .decode("ascii")
                .strip("\x00")
            ),
            order_text=(
                self.read_reg_data(
                    *self._module_offset(ap_modbus_registers.ORDER_TEXT, position)
                )
                .decode("ascii")
                .strip("\x00")
            ),
        )
        Logging.logger.debug(f"Reading ApInformation: {info}")
        return info

    def read_diagnostic_status(self) -> list[Diagnostics]:
        """Read the diagnostic status and return a Diagnostics object for each module

        :ret value: Diagnostics status for every module
        :rtype: list[Diagnostics]
        """
        # overwrite the type size with the actual module count + 1 (see datasheet)
        ap_diagnosis_parameter = Parameter(
            parameter_id=20196,
            parameter_instances={"FirstIndex": 0, "NumberOfInstances": 1},
            is_writable=False,
            array_size=self.read_module_count() + 1,
            data_type="UINT8",
            default_value=0,
            description="AP diagnosis status for each Module",
            name="AP diagnosis status",
        )

        reg = self.read_parameter(0, ap_diagnosis_parameter)
        return [self.Diagnostics.from_int(r) for r in reg]

    def read_global_diagnosis_state(self) -> dict:
        """Read the global diagnosis state from the cpx system. Returns dict
        of module diagnosis state containing a logical OR over all modules errors.
        This will give you an overview about what state the system is in.

        :ret value: Diagnosis state
        :rtype: dict"""
        reg = self.read_reg_data(self.global_diagnosis_register, length=2)
        diagnosis_keys = [
            "Device available",
            "Current",
            "Voltage",
            "Temperature",
            "reserved",
            "Movement",
            "Configuration / Parameters",
            "Monitoring",
            "Communication",
            "Safety",
            "Internal Hardware",
            "Software",
            "Maintenance",
            "Misc",
            "reserved(14)",
            "reserved(15)",
            "External Device",
            "Security",
            "Encoder",
        ]
        # the rest of the bits are "reserved" and therefore trunctuated
        diagnosis_dict = {
            diagnosis_keys[i]: bytes_to_boollist(reg)[i]
            for i in range(len(diagnosis_keys))
        }
        return diagnosis_dict

    def read_active_diagnosis_count(self) -> int:
        """Read count of currently active diagnosis from the cpx system

        :ret value: Amount of active diagnosis
        :rtype: int"""
        reg = self.read_reg_data(self.global_diagnosis_register + 2)
        return int.from_bytes(reg, byteorder="little")

    def read_latest_diagnosis_index(self) -> int:
        """Read the index of the module with the latest diagnosis.
        If no diagnosis is available, returns None

        :ret value: Modul index
        :rtype: int or None"""
        reg = self.read_reg_data(self.global_diagnosis_register + 3)
        # subtract one because AP starts with module index 1
        module_index = int.from_bytes(reg, byteorder="little") - 1
        if module_index < 0:
            return None
        return module_index

    def read_latest_diagnosis_code(self) -> int:
        """Read the latest diagnosis code from the cpx system

        :ret value: Diagnosis code
        :rtype: int"""
        reg = self.read_reg_data(self.global_diagnosis_register + 4, length=2)
        return int.from_bytes(reg, byteorder="little")

    def write_parameter(
        self,
        position: int,
        parameter: Parameter,
        data: list[int] | int | bool,
        instance: int = 0,
    ) -> None:
        """Write parameters via module position, param_id, instance (=channel) and data to write
        Data must be a list of (signed) 16 bit values or one 16 bit (signed) value or bool
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param parameter: AP Parameter
        :type parameter: Parameter
        :param data: list of 16 bit signed integers, one signed 16 bit integer or bool to write
        :type data: list | int | bool
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        """
        raw = parameter_pack(parameter, data)
        self._write_parameter_raw(position, parameter.parameter_id, instance, raw)

    def read_parameter(
        self,
        position: int,
        parameter: Parameter,
        instance: int = 0,
    ) -> Any:
        """Read parameter

        :param position: Module position index starting with 0
        :type position: int
        :param parameter: AP Parameter
        :type parameter: Parameter
        :param instance: (optional) Parameter Instance (typically the channel, see datasheet)
        :type instance: int
        :return: Parameter value
        :rtype: Any
        """
        raw = self._read_parameter_raw(position, parameter.parameter_id, instance)
        data = parameter_unpack(parameter, raw)
        return data

    def _write_parameter_raw(
        self, position: int, param_id: int, instance: int, data: bytes
    ) -> None:
        """Read parameters via module position, param_id, instance (=channel)
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :param data: data as bytes object
        :type data: bytes
        """

        param_reg = ap_modbus_registers.PARAMETERS.register_address
        # module indexing starts with 1 (see datasheet)
        module_index = (position + 1).to_bytes(2, byteorder="little")
        param_id = param_id.to_bytes(2, byteorder="little")
        instance = instance.to_bytes(2, byteorder="little")
        # length in bytes
        length_bytes = len(data).to_bytes(2, byteorder="little")
        command = (2).to_bytes(2, byteorder="little")  # 1=read, 2=write

        # prepare the command
        self.write_reg_data(module_index + param_id + instance, param_reg)
        # write length in bytes
        self.write_reg_data(length_bytes, param_reg + 4)
        # write data to register
        self.write_reg_data(data, param_reg + 10)
        # execute the command
        self.write_reg_data(command, param_reg + 3)

        exe_code = 0
        while exe_code != 16:
            exe_code = int.from_bytes(
                self.read_reg_data(param_reg + 3), byteorder="little"
            )
            # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
            if exe_code == 4:
                raise CpxRequestError

        Logging.logger.debug(f"Wrote data {data} to module position: {position - 1}")

    def _read_parameter_raw(self, position: int, param_id: int, instance: int) -> bytes:
        """Read parameters via module position, param_id, instance (=channel)
        Raises "CpxRequestError" if request denied

        :param position: Module position index starting with 0
        :type position: int
        :param param_id: Parameter ID (see datasheet)
        :type param_id: int
        :param instance: Parameter Instance (typically used to define the channel, see datasheet)
        :type instance: int
        :return: Parameter register values
        :rtype: bytes
        """

        param_reg = ap_modbus_registers.PARAMETERS.register_address
        # module indexing starts with 1 (see datasheet)
        module_index = (position + 1).to_bytes(2, byteorder="little")
        param_id = param_id.to_bytes(2, byteorder="little")
        instance = instance.to_bytes(2, byteorder="little")
        command = (1).to_bytes(2, byteorder="little")  # 1=read, 2=write

        # prepare and execute the read command
        self.write_reg_data(module_index + param_id + instance + command, param_reg)

        # 1=read, 2=write, 3=busy, 4=error(request failed), 16=completed(request successful)
        exe_code = 0
        while exe_code != 16:
            exe_code = int.from_bytes(
                self.read_reg_data(param_reg + 3), byteorder="little"
            )
            if exe_code == 4:
                raise CpxRequestError

        # get datalength in bytes from register 10004
        length_bytes = int.from_bytes(
            self.read_reg_data(param_reg + 4), byteorder="little"
        )
        # read 16 bit registers
        length_registers = div_ceil(length_bytes, 2)
        data = self.read_reg_data(param_reg + 10, length_registers)

        Logging.logger.debug(
            f"Read parameter {param_id}: {data} from module position: {position - 1}"
        )

        return data

    def _module_offset(self, modbus_command: tuple, module: int) -> int:
        register, length = modbus_command
        return ((register + 37 * module), length)

    @staticmethod
    def _grab_apdd(
        ip_address, module_index: int, apdd_path: str, fw_version: str
    ) -> json:
        """Grabs all apdd from module and saves them in apdd_path"""
        # Module indexs in ap start with 1
        url = f"http://{ip_address}/cgi-bin/ap-file-get?slot={module_index + 1}&filenumber=6"
        response = requests.get(url, timeout=100)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            json_data = response.json()
            # currently the only module with more than one variant is 4IOL. The order text for all
            # variants is the same, so OrderText of the first variant is used for naming the apdd
            apdd_name = json_data["Variants"]["VariantList"][0][
                "VariantIdentification"
            ]["OrderText"]
            output_file_path = (
                apdd_path
                + "/"
                + apdd_name
                + "_v"
                + fw_version.replace(".", "-")
                + ".json"
            )
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(json_data, indent=4))
            Logging.logger.debug(f"JSON data has been written to: {output_file_path}")
            return json_data

        raise ConnectionError(f"Failed to fetch APDD: {response.status_code}")
