# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed
- [Minor] Exchanged int_to_signed16 function with built in function

### Changed
- [Minor] Added example.py for cpx-ap and cpx-e, minor bugfixing

### Changed
- [Minor] Added base functionality for CPX-AP-I. Added not implemented modules to CPX-E with Error on init. Several bugfixes on CPX-E.

### Changed
- [Minor] Fixed that registers are read before writing to them instead of saving the values in the object instance

### Changed
- [Minor] Updated modules list so each module can be adressed via the base class

### Changed
- [Minor] Fixed module functions, fixed process data

### Changed
- [Minor] Fixed system test issues, Minor Bugfixes

### Changed
- [Minor] Fixed linting issues

### Changed
- [Minor] Reworked CPX-E class structure.

## v0.1.1 - 20.10.23
### Added
- [Patch] Added deployment to artifactory.
### Fixed
- [Patch] Fixed CI stages for unit test and linting.

## v0.1.0 - 17.10.23
- [Minor] Initial release
