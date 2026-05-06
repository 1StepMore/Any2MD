"""Markitdown converter for text-based format support."""

from pathlib import Path
from typing import List

from wheels.converters.base_converter import BaseConverter


class MarkitdownConverter(BaseConverter):
    """Converter using markitdown for text-based formats not handled by other converters.

    Supports: csv, json, xml, yaml, yml, epub, zip
    """

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of text formats markitdown can handle."""
        return [
            ".csv",     # Data files
            ".json",    # Data files
            ".xml",     # Data files
            ".yaml",    # Data files
            ".yml",     # Data files
            ".epub",    # eBook
            ".zip",     # Archive (markitdown iterates over contents)
        ]

    def convert(self, input_path: Path) -> str:
        """Convert using markitdown Python API.

        Args:
            input_path: Path to the input file.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If input file does not exist.
            RuntimeError: If markitdown conversion fails.
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        try:
            from markitdown import MarkItDown
            from markitdown._exceptions import MarkItDownException

            md = MarkItDown()
            result = md.convert(str(input_path))
            return result.markdown
        except ImportError:
            raise RuntimeError(
                "markitdown not installed. Install with: pip install markitdown"
            )
        except MarkItDownException as e:
            raise RuntimeError(f"markitdown conversion failed: {e}")
        except Exception as e:
            raise RuntimeError(f"markitdown conversion failed: {e}")