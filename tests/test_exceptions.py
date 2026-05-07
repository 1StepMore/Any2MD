"""Exception hierarchy tests."""

import pytest

from wheels.exceptions import (
    Any2MDRuntimeError,
    FileTooLargeError,
    UnsupportedFormatError,
    ConversionError,
    ConfigError,
)


class TestExceptionHierarchy:
    def test_any2md_runtime_error_inherits_from_runtime_error(self):
        error = Any2MDRuntimeError("test")
        assert isinstance(error, RuntimeError)

    def test_file_too_large_error_inherits_from_any2md_runtime_error(self):
        error = FileTooLargeError("test")
        assert isinstance(error, Any2MDRuntimeError)

    def test_file_too_large_error_inherits_from_runtime_error(self):
        error = FileTooLargeError("test")
        assert isinstance(error, RuntimeError)

    def test_unsupported_format_error_inherits_from_any2md_runtime_error(self):
        error = UnsupportedFormatError("test")
        assert isinstance(error, Any2MDRuntimeError)

    def test_unsupported_format_error_inherits_from_runtime_error(self):
        error = UnsupportedFormatError("test")
        assert isinstance(error, RuntimeError)

    def test_conversion_error_inherits_from_any2md_runtime_error(self):
        error = ConversionError("test")
        assert isinstance(error, Any2MDRuntimeError)

    def test_conversion_error_inherits_from_runtime_error(self):
        error = ConversionError("test")
        assert isinstance(error, RuntimeError)

    def test_config_error_inherits_from_any2md_runtime_error(self):
        error = ConfigError("test")
        assert isinstance(error, Any2MDRuntimeError)

    def test_config_error_inherits_from_runtime_error(self):
        error = ConfigError("test")
        assert isinstance(error, RuntimeError)


class TestBackwardCompatibility:
    def test_catching_runtime_error_catches_file_too_large_error(self):
        try:
            raise FileTooLargeError("file too large")
        except RuntimeError as e:
            assert isinstance(e, FileTooLargeError)

    def test_catching_runtime_error_catches_unsupported_format_error(self):
        try:
            raise UnsupportedFormatError("unsupported format")
        except RuntimeError as e:
            assert isinstance(e, UnsupportedFormatError)

    def test_catching_runtime_error_catches_conversion_error(self):
        try:
            raise ConversionError("conversion failed")
        except RuntimeError as e:
            assert isinstance(e, ConversionError)

    def test_catching_runtime_error_catches_config_error(self):
        try:
            raise ConfigError("config error")
        except RuntimeError as e:
            assert isinstance(e, ConfigError)

    def test_catching_any2md_runtime_error_catches_all_specific_errors(self):
        errors = [
            FileTooLargeError("test"),
            UnsupportedFormatError("test"),
            ConversionError("test"),
            ConfigError("test"),
        ]
        for error in errors:
            assert isinstance(error, Any2MDRuntimeError)


class TestExceptionMessages:
    def test_file_too_large_error_message(self):
        msg = "File exceeds 50MB limit"
        error = FileTooLargeError(msg)
        assert str(error) == msg

    def test_unsupported_format_error_message(self):
        msg = "Unsupported format"
        error = UnsupportedFormatError(msg)
        assert str(error) == msg

    def test_conversion_error_message(self):
        msg = "Conversion failed"
        error = ConversionError(msg)
        assert str(error) == msg

    def test_config_error_message(self):
        msg = "Config error"
        error = ConfigError(msg)
        assert str(error) == msg
