# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Fixed
- Docstrings and types of CpxE4Iol `write_channel()`
- Renaming modules manually now checks for duplicates and increments suffix if needed
- Register order in bytes on reading and writing from and to IO-Link masters

### Changed
- `read_module_parameter_enum_str()` doesn't raise TypeError anymore when no enums available. Instead gives Logger Info message and returns values.
- Renamed `clear_channel()` to `reset_channel()`
- `print_system_information` now prints enum strings for parameters
- removed `read_output_channel()` from IO-Link masters
- removed `full_size` parameter

### Added
- `write_channels()` function for IO-Link masters
- Simple diagnosis example
- Utils to documentation

## v0.6.4 - 30.10.24
### Changed
- Updated all dependencies

### Fixed
- Fixed non ascii characters in user path leading to exception

## v0.6.3 - 17.10.24
### Fixed
- All "renaming modules" examples
- Issue with ´CpxE(TYPECODE)´ containing more than two of the same module type
- CPX-E-8DO `write_channel()` now behaves correctly and does not reset other channels

### Added
- Added example code for isdu read/write

### Changed
- Set dependencies to static versions

## v0.6.2 - 30.09.24
### Fixed
- Length calculation in IO-Link function `write_isdu()`
- Amount of tries and check in isdu functions are now consistent
- Fixed some Docstrings 

### Changed
- CPX-AP ISDU access now returns only relevant and valid data. Optional parameter `data_type`
 defines the expected return value of `read_isdu()`. While `write_isdu()` checks for the data_type 
 of parameter `data` and behaves accordingly
- Made `CpxAp.add_module()` a private function as it should not be accessed by the user
- Some minor code improvements
- Added further explanation to `example_cpxap_digital_output.py` regarding timeout
- Several backend changes in ap_module to clear lately ignored pylint issues

## Added
- Unittests for CpxAp

## v0.6.1 - 22.08.24
### Fixed
- Parameter handling for CHAR types

## v0.6.0 - 22.08.24
### Added
- Support for INT8 and UINT8 channels (used by vacuum valves for VTUX)
- Support for AP modules with different channel types
- System tests for VTUX-AS
- Information on channels in system_information docu

### Changed
- Removed optional parameter `raw` from `read_module_parameter()`. Added `read_module_parameter_enum_str()` instead.
- Removed optional parameter `outputs_only` from `read_channel(s)()`. Added `read_output_channel(s)()` instead.
- Updated examples

### Fixed
- Updated ModbusException handling for ConnectionAbortedError and corresponding unittest
- Corrected (U)INT16 handling and corresponding unittests
- Typos in CPX-AP docu (import, instantiation)

## v0.5.3 - 09.08.24
### Added
- Added optional parameter `raw` for `read_module_parameter()` which returns ENUM id instead of name.

## v0.5.2 - 02.08.24
### Added
- Checker script to read in APDDs and check if they are compatible with the library
- Added type hint for ap modules property to enable autocompletion.
- Added `int_to_boollist()` to utils.boollist

### Changed
- CPX-AP now interprets apdds with utf-8 instead of ascii encoding
- `CpxAp.read_global_diagnosis_state()` now returns dict according to "module diagnostics state" (see datasheet CPX-AP-\*-EP-\*)
- Increment pymodbus version to 3.7.0

### Fixed
- Updated `requests` dependency to remove missing `chardet` error. Will now only raise a warning. Can be fixed by manually installing `chardet`

## v0.5.1 - 21.06.24
### Fixed
- CPX-AP: Limited the modbus timeout to a minimum 100 ms. Values lower that that could lead to exclusion from the system.

### Added
- boollist_to_int convenience function
- CLI: cpx_ap read/write channel functionality
- CPX-AP: Outdated and not-supported module firmware will now raise RuntimeError with suggestion to update firmware.

### Changed
- CPX-AP: Changed default apdd and docu path "appauthor" to Festo
- CPX-AP: Added diagnosis example

### Fixed
- ApModule: write_channel bug causing other channels to be resetted for some module types. 
### Removed
- Removed `chardet` dependency

## v0.5.0 - 17.06.24
### Added
- Diagnosis for CpxAp and ApModule. This includes a ModuleInformation dataclass and builder as well as some new functions
- CpxAp: Read the global diagnosis state from the cpx-ap system with `CpxAp.read_global_diagnosis_state()`
- CpxAp: Read the count of active diagnosis from the cpx-ap system with `CpxAp.read_active_diagnosis_count()`
- CpxAp: Read the module index with the latest diagnosis from the cpx-ap system with `CpxAp.read_latest_diagnosis_index()`
- CpxAp: Read the latest diagnosis code from the cpx-ap system with `CpxAp.read_latest_diagnosis_code()`
- CpxAp: Added INT16 and UINT16 support for MPA modules in read/write functions, expanded system tests
- ApModule: Read the diagnosis code from the module with `ApModule.read_diagnosis_code()`
- ApModule: Read the diagnosis information from the module with `ApModule.read_diagnosis_information()`

## v0.4.2 - 29.05.24
### Changed
- Updated links to public repo

## v0.4.1 - 29.05.24
### Changed
- improved ap_module `read_channels()`/`write_channels()` functions
- improved unittests for ap_module
### Fixed
- fixed bug in ap_module `_check_instances()` that lead to incorrect behaviour when no instances where specified

## v0.4.0 - 23.05.24
### Changed
- This release will drastically change the usability of all AP components. Modules are now autogenerated in the runtime. The documentation will only be available on the user device. There is a very useful `CpxAp.print_system_information()` function that will give you all the details about your system.
- Exchanged individual `configure_...` functions to generic `read_module_parameter()`/`write_module_parameter()`
- Exchanged parameter mapping with read out information from ap system
- CPX-AP-*-EP: `read_parameters()` renamed to `read_system_parameters()`

### Added
- Documentation for usage in README
- Documentation will now be generated on user device
- ap_module_builder that configures a generic_ap_module by its apdd
- Added gitlab release job

### Fixed
- TypeError message in `write_channel()` doesn't raise AttributeError anymore
- IndexError output on digital functions `set_channel()`/`clear_channel()`/`toggle_channel()` now show correct string

## v0.3.0 - 02.04.24
### Added 
- Added VABA (electric interface for VTSA valve terminal)
- CLI command `parameter` (options `--list` and `--meta`) showing parameter meta data
- channel_range_check in helpers, now raises IndexError instead of ValueError
- VMPAL Valve Terminal for CPX-AP
- VAEM Valve Terminal for CPX-AP
- Enums for configure functions
- Systemtests for VABX
- Examples for cyclic access with threading
- CpxBase: read_device_info
- CpxApEp: read_diagnostic_status reads Diagnostics for each module
- Unittests for CpxBase
- More examples

### Changed
- Determine parameter ids based on .csv.
- configure functions don't accept strings anymore. Instead use enums from cpx_ap/e_enums
- Moved read_diagnostics_status from CpxApEp to CpxAp
- Renamed ApParameter to ParameterMapItem,
- Renamed ApParameters to ModuleParameters
- ap4iol: code optimization
- CpxE: functions renamed to read_status, read_fault_detection
- CpxBase: now initializes with self.base=None instead of no self.base at all
- CpxAp: Parameter read/write now utilizes multi-register access
- CpxAp4Iol: read_channel now takes "full_size" parameter. Default is now to return the length from the device information (returns only relevant bytes)
- CpxApEP: deleted write_parameters(), added configure_monitoring_load_supply() instead
- Pybodmus Error now raises "ConnectionAbortedError" instead of "ValueError"
- IO-Link modules now read and write bytes objects
- Deleted obsolete cpx-e "read_module_count" function

### Fixed
- 4DI4DO and 12DI4DO modules toggle channel now working as expected
- AP Parameter length register is now interpreted correctly as "in bytes"
- Removed unnecessary validation check in write_parameter_raw
- Many logger.info strings in modules
- Docstring in e4aoui configure_channel_range
- ip-address octetts now in correct order
- Project URLs in pyproject.toml

## v0.2.0 - 26.01.24
### Added
- Added content to README.md
- Added module functions CPX-E/AP
- Handling of naming for more modules of one type (CPX-E and -AP)
- Added warning if cpx-e-ep module is added multiple times
- Added vabx module for vtux access
- ISDU Access for CPX-AP-4IOL
- Added CPX-AP-A modules
- Implemented CPX-E-1CI module
- Unittests for cpxe and cpxap modules
- CpxE and CpxAP: Added `__repr__` function
- CpxE: Added property setter / getter for more modules.
- CpxE: Added access-by-name for modules of CpxE.
- CpxE: Added construction from typecode.
- CpxE: Added property setter for modules.
- CpxE8Do: Added access-by-index-operator to channels
- CpxE: Added CLI for writing and reading values.

### Changed
- Removed timeout and port from CPX-base, implemented timeout for CPX-AP
- changed return value of read function number to int
- Added context manager functionality to cpx base class. Adapted examples to use this context manager.
- Updated modules list so each module can be adressed via the base class

### Fixed
- General Bugfixes

## v0.1.1 - 20.10.23
### Added
- Added deployment to artifactory.

### Fixed
- Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- Initial release
