# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- [Minor] CpxE: Added access-by-name for modules of CpxE.
- [Minor] CpxE: Added construction from typecode.
- [Minor] CpxE: Added property setter for modules.

### Changed
- [Minor] several bugfixes
- [Minor] Added context manager functionality to cpx base class. Adapted examples to use this context manager
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
- [Patch] Bugfixes after Merge

## v0.1.1 - 20.10.23
### Added
- [Patch] Added deployment to artifactory.
### Fixed
- [Patch] Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- [Minor] Initial release
