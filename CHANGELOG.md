# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## v0.2.0 - 26.01.24
### Added
- CpxApEp: read_diagnostic_status reads Diagnostics for each module
- CpxApEp: read_bootloader_version
- Unittests for CpxBase
- More examples
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
- Removed timeout and port from CPX-base, implemented timeout for CPX-AP
- changed return value of read function number to int
- Added context manager functionality to cpx base class. Adapted examples to use this context manager.
- Updated modules list so each module can be adressed via the base class

### Fixed
- ip-address octetts now in correct order
- Project URLs in pyproject.toml
- General Bugfixes

## v0.1.1 - 20.10.23
### Added
- Added deployment to artifactory.

### Fixed
- Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- Initial release
