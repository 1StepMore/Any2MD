# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.5] - 2025-05-11

### Fixed
- **Batch format scanning**: Added missing formats to batch folder scanning (.epub, .csv, .json, .xml, .yaml, .yml, .zip)
- **API import**: Fixed relative import in `wheels/api.py` for proper module imports

## [0.3.0] - 2025-05-07

### Added
- **Test Suite**: 83 tests covering API, exceptions, config, dispatcher, and integration
- **GitHub Actions CI**: Automated testing (Python 3.10/3.11/3.12) with lint and type-check
- **Trusted Publishing**: Auto-publish to PyPI via GitHub Actions OIDC (no tokens)
- **Python API Documentation**: Full API docs in README with code examples

### Changed
- **README**: Added Python API section, pip install instructions, config access tip, updated architecture diagram
- **requirements.txt**: Added pytest for testing

### Fixed
- **Wrapper package**: `any2md/` wrapper properly exposes `convert_to_markdown`
- **CI triggers**: Fixed to trigger on `main` branch and `v*` tags
- **PyPI project name**: Matched to `Any2MD-1StepMore` (not `any2md` which was taken)

## [0.2.0] - 2025-05-07

### Added
- **Wheel package**: Full wheelization for `pip install -e .` support
- **Public API**: `convert_to_markdown()` function returning markdown string
- **Exception hierarchy**: `Any2MDRuntimeError`, `FileTooLargeError`, `UnsupportedFormatError`, `ConversionError`, `ConfigError`
- **PyPI-ready**: `pyproject.toml` with proper package configuration

## Prior Versions
- See git history for v0.1.x and earlier releases