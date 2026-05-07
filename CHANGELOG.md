# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-05-07

### Added
- **Test Suite**: 83 tests covering API, exceptions, config, dispatcher, and integration
- **GitHub Actions CI**: Automated testing and linting on push/PR
- **Python API Documentation**: Full API docs in README with code examples

### Changed
- **README**: Added Python API section, pip install instructions, config access tip
- **requirements.txt**: Added pytest for testing

### Fixed
- **Wrapper package**: `any2md/` wrapper properly exposes `convert_to_markdown`

## [0.2.0] - 2025-05-07

### Added
- **Wheel package**: Full wheelization for `pip install -e .` support
- **Public API**: `convert_to_markdown()` function returning markdown string
- **Exception hierarchy**: `Any2MDRuntimeError`, `FileTooLargeError`, `UnsupportedFormatError`, `ConversionError`, `ConfigError`
- **PyPI-ready**: `pyproject.toml` with proper package configuration

## Prior Versions
- See git history for v0.1.x and earlier releases