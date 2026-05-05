"""Mammoth converter for DOCX files."""

import sys
from pathlib import Path
from typing import List

from wheels.converters.base_converter import BaseConverter

try:
    import mammoth
    from markdownify import markdownify as md, ATX
except ImportError as e:
    raise RuntimeError(f"Missing required dependency for MammothConverter: {e}") from e


class MammothConverter(BaseConverter):
    """Converter for DOCX files using the Mammoth library."""

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions.

        Returns:
            List of file extensions this converter handles.
        """
        return [".docx"]

    def convert(self, input_path: Path) -> str:
        """Convert DOCX file to markdown.

        Args:
            input_path: Path to the input .docx file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            RuntimeError: If the conversion fails.
        """
        try:
            with open(input_path, "rb") as f:
                result = mammoth.convert_to_html(f)
        except OSError as e:
            raise RuntimeError(f"Failed to read DOCX file: {e}") from e

        if result.messages:
            for message in result.messages:
                print(f"Mammoth: {message}", file=sys.stderr)

        try:
            markdown = md(result.value, heading_style=ATX)
        except Exception as e:
            raise RuntimeError(f"Failed to convert HTML to markdown: {e}") from e

        return markdown