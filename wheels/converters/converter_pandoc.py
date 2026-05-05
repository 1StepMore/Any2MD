"""Pandoc converter using pypandoc for document conversion."""

from pathlib import Path
from typing import List

from wheels.converters.base_converter import BaseConverter

try:
    import pypandoc
except ImportError:
    raise RuntimeError(
        "pypandoc is required for PandocConverter. "
        "Install it with: pip install pypandoc"
    )


class PandocConverter(BaseConverter):
    """Converter for docx, pptx, and xlsx files using Pandoc via pypandoc."""

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions.

        Returns:
            List of file extensions this converter handles.
        """
        return [".docx", ".pptx", ".xlsx"]

    def convert(self, input_path: Path) -> str:
        """Convert the input file to markdown using Pandoc.

        Args:
            input_path: Path to the input file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            RuntimeError: If pandoc conversion fails or pandoc binary is missing.
        """
        try:
            return pypandoc.convert_file(str(input_path), "gfm")
        except OSError as e:
            raise RuntimeError(
                f"Pandoc conversion failed: {e}. "
                "Ensure pandoc is installed and in PATH."
            ) from e
        except Exception as e:
            raise RuntimeError(f"Pandoc conversion failed: {e}") from e