"""Any2MD - Universal document to Markdown converter

This is a wrapper package that re-exports the public API from wheels.
"""

from wheels.api import convert_to_markdown
from wheels.exceptions import (
    Any2MDRuntimeError,
    FileTooLargeError,
    UnsupportedFormatError,
    ConversionError,
    ConfigError,
)
from wheels.config import get_config, Config

__version__ = "0.2.1"

__all__ = [
    # Public API
    "convert_to_markdown",
    # Exceptions
    "Any2MDRuntimeError",
    "FileTooLargeError",
    "UnsupportedFormatError",
    "ConversionError",
    "ConfigError",
    # Config
    "get_config",
    "Config",
]
