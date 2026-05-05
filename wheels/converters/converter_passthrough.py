"""Passthrough converter for text and markdown files."""

from pathlib import Path
from typing import List

from wheels.converters.base_converter import BaseConverter


class PassthroughConverter(BaseConverter):
    """Converter for text and markdown files that returns contents as-is."""

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions.

        Returns:
            List of file extensions this converter handles.
        """
        return [".md", ".txt"]

    def convert(self, input_path: Path) -> str:
        """Read and return the file contents as-is.

        Args:
            input_path: Path to the input file to convert.

        Returns:
            The file contents as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
        """
        return input_path.read_text(encoding="utf-8")