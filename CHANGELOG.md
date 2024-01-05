# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- [Minor] Implemented CPX-E-1CI module
- [Minor] New functions for CPX-E-4AI and 4AO
- [Minor] Added utils/helpers with ceil function
- [Minor] Unittests for cpxe and cpxap modules
- [Minor] Added pylintrc file to disable f-string highlighting
- [Minor] CPXAP: Added read function for AP parameters
- [Minor] CPXAP: Functionality for IO-Link module
- [Minor] CPXE: Added more unittests
- [Minor] CpxE and CpxAP: Added __repr__ function
- [Minor] CpxE: Added property setter / getter for more modules.
- [Minor] CpxE: Added access-by-name for modules of CpxE.
- [Minor] CpxE: Added construction from typecode.
- [Minor] CpxE: Added property setter for modules.
- [Minor] CpxE8Do: Added access-by-index-operator to channels
- [Minor] CpxE: Added CLI for writing and reading values.
### Changed
- [Minor] e1ci dicts are now dataclasses
- [Minor] Modbus Commands are now marked as constants
- [Minor] Moved modules to individual files
- [Minor] Moved unittests to subfolder
- [Minor] fixed inheritance for AP and E modules
- [Minor] changed return value of read function number to int
- [Minor] several bugfixes
- [Minor] Added context manager functionality to cpx base class. Adapted examples to use this context manager.
- [Minor] Exchanged int_to_signed16 function with built in function
- [Minor] Added example.py for cpx-ap and cpx-e, minor bugfixing
- [Minor] Added base functionality for CPX-AP-I. Added not implemented modules to CPX-E with Error on init. Several bugfixes on CPX-E.
- [Minor] Fixed that registers are read before writing to them instead of saving the values in the object instance
- [Minor] Updated modules list so each module can be adressed via the base class
- [Minor] Fixed module functions, fixed process data
- [Minor] Fixed system test issues, Minor Bugfixes
- [Minor] Fixed linting issues
- [Minor] Reworked CPX-E class structure.

### Fixed
- [Patch] Fixed bug in CpxE4Iol address calculation
- [Patch] Fixed bug in CPX-E-4AI read_channel
- [Patch] Fixed access to protected members of cpx_base
- [Patch] Bugfix in CPX-E-4IOL read/write and configure functions
- [Patch] Bugfixes for IO-Link modules
- [Patch] Fixed bug in cpx-e-4ai-ui and 4ao configure functions
- [Patch] Fixed diagnostics function in cpx-e-8do
- [Patch] Fixed several linter issues
- [Patch] Bugfixes after Merge

## v0.1.1 - 20.10.23
### Added
- [Patch] Added deployment to artifactory.
### Fixed
- [Patch] Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- [Minor] Initial release
