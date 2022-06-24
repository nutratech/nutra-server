# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Local `PostgreSQL` configuration for Linux/macOS (support _startup service_)
- Use `Sanic` instead of `Flask` for server
- Support for `nginx` and ssl
- Refactored controllers & services to more closely align with `MVC` design pattern

### Fixed

- Graceless crashes when `postgres` server was unreachable;
  now we operate in cowardly mode

### Added

- Unit tests, with special `requirements-test.txt` file
- BMR & other calculations for female users

### Removed

- Shop functions (e.g. controller for orders)

## [0.0.0] - 2020-08-02

### Added

- Initial release
- Support for most endpoints
- `Postgres` database driver and bindings
- Add `@auth` annotation
