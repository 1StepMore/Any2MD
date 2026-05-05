"""HTML to Markdown converter using markdownify."""

from pathlib import Path
from typing import List

from markdownify import markdownify as md, ATX

from wheels.converters.base_converter import BaseConverter


class HtmlConverter(BaseConverter):
    """Converter for HTML files to Markdown."""

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.html', '.htm']

    def convert(self, input_path: Path) -> str:
        """Convert HTML file to markdown.

        Args:
            input_path: Path to the HTML file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            RuntimeError: If conversion fails.
        """
        try:
            html_content = input_path.read_text(encoding='utf-8')
            return md(html_content, heading_style=ATX)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to convert HTML to markdown: {e}") from e