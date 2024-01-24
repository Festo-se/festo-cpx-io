# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- Feature.md file
- Added content to README.md
- Added Parameter write for CPX-AP-*-EP
- Handling of naming for more modules of one type (CPX-E and -AP)
- Added warning if cpx-e-ep module is added multiple times
- Added black job to CI/CD
- Added tests for other CPX-AP modules
- Added vabx module for vtux access
- ISDU Access for CPX-AP-4IOL
- Added CPX-AP-A modules
- Implemented CPX-E-1CI module
- New functions for CPX-E-4AI and 4AO
- Added utils/helpers with ceil function
- Unittests for cpxe and cpxap modules
- Added pylintrc file to disable f-string highlighting
- CPXAP: Added read function for AP parameters
- CPXAP: Functionality for IO-Link module
- CPXE: Added more unittests
- CpxE and CpxAP: Added __repr__ function
- CpxE: Added property setter / getter for more modules.
- CpxE: Added access-by-name for modules of CpxE.
- CpxE: Added construction from typecode.
- CpxE: Added property setter for modules.
- CpxE8Do: Added access-by-index-operator to channels
- CpxE: Added CLI for writing and reading values.

### Changed
- Removed timeout and port from CPX-base, implemented timeout for CPX-AP
- Reworked unit tests
- Moved typecode ids to cpx_*_definitions.py
- e1ci dicts are now dataclasses
- Modbus Commands are now marked as constants
- Moved modules to individual files
- Moved unittests to subfolder
- fixed inheritance for AP and E modules
- changed return value of read function number to int
- several bugfixes
- Added context manager functionality to cpx base class. Adapted examples to use this context manager.
- Exchanged int_to_signed16 function with built in function
- Added example.py for cpx-ap and cpx-e, minor bugfixing
- Added base functionality for CPX-AP-I. Added not implemented modules to CPX-E with Error on init. Several bugfixes on CPX-E.
- Fixed that registers are read before writing to them instead of saving the values in the object instance
- Updated modules list so each module can be adressed via the base class
- Fixed module functions, fixed process data
- Fixed system test issues, Minor Bugfixes
- Fixed linting issues
- Reworked CPX-E class structure.

### Fixed
- Fixed README links
- Docstrings and Logging
- Bugfix encode_int with data_type "bool"
- Fixed Example code CPX-E
- Bugfix CPX-AP Parameter
- Bugfix CPX-AP- Systemtest
- Fixed bug in IDSU access cpx-ap-4iol
- Fixed bug in CpxE4Iol address calculation
- Fixed bug in CPX-E-4AI read_channel
- Fixed access to protected members of cpx_base
- Bugfix in CPX-E-4IOL read/write and configure functions
- Bugfixes for IO-Link modules
- Fixed bug in cpx-e-4ai-ui and 4ao configure functions
- Fixed diagnostics function in cpx-e-8do
- Fixed several linter issues
- Bugfixes after Merge

## v0.1.1 - 20.10.23
### Added
- Added deployment to artifactory.

### Fixed
- Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- Initial release
