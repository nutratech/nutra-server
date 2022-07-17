# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2022-07-16

### Changed

- Using `Sanic` instead of `Flask`, and `async` controller functions
- Local `PostgreSQL` configuration for Linux/macOS (support _startup service_)
- Use `Sanic` instead of `Flask` for server
- Support for `nginx` and ssl
- Refactored controllers & services to more closely align with `MVC` design pattern
- No more `message` parameter on `response`, it has moved to `response.data` and
  usually only as an `err_msg` value, e.g. `response.data.error`
- Response `class` is now a function `def`, which accepts `kwargs` instead of only
  a `request` and `response_type` parameter
- Access members through module reference, rather than importing all individually

### Fixed

- Graceless crashes when `postgres` server was unreachable;
  now we operate in cowardly mode
- Configuration issues with systemctl service and `env` vars on the deployment server
- Better error handling inside the Postgres module, and `exc_req()` method

### Added

- Unit tests, with special `requirements-test.txt` file
- BMR & other calculations for female users
- One rep maxes, and algebra to calculate also: `{1, 2, 3, 5, 8, 10, 12, 15, 20}`
- Links to all `GET` requests on home page
- Better comments, `TODO` notes, and organized files generally
- Information about CLI on main route `/` (server landing page)
- Systematic logging (logging module)
- Nginx config
- Coverage and other configs in `setup.cfg`
- A `deploy-dev` GitHub workflow, on self-hosted runner

### Removed

- Shop functions (controller for orders/products, `cache` layer, Postman collection)
- Specific `/bmr/<name_of_equation>` endpoints, in favor of a general `/bmr` one
- Slack message integrations (not the most production worthy mechanism)
- Packages usps, py3dbp (and other references to Flask.. gunicorn, Werkzeug)

## [0.0.38] - 2020-08-02

### Added

- Initial release
- Support for most endpoints
- `Postgres` database driver and bindings
- Add `@auth` annotation
