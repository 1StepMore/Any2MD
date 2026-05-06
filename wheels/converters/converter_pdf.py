"""PDF converter with dynamic engine selection."""

import importlib
import subprocess
import sys
from pathlib import Path
from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from wheels.converters.base_converter import BaseConverter
from wheels.config import get_config


def _retry_on_transient(exception):
    if isinstance(exception, (subprocess.TimeoutExpired, MemoryError)):
        return True
    # FileNotFoundError is OSError subclass - but it's NOT transient
    if isinstance(exception, FileNotFoundError):
        return False
    if isinstance(exception, OSError):
        if hasattr(exception, 'errno') and exception.errno in (11, 12):
            return False
        return True
    return False


class PdfConverter(BaseConverter):
    """Converter for PDF files with light/heavy engine support."""

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return [".pdf"]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_retry_on_transient),
    )
    def convert(self, input_path: Path) -> str:
        """Convert PDF file to markdown.

        Args:
            input_path: Path to the input PDF file.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            RuntimeError: If no PDF engine is available or conversion fails.
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"PDF file not found: {input_path}")

        config = get_config()
        pdf_engine = config.pdf_engine

        if pdf_engine == "light":
            return self._convert_light(input_path)
        else:
            return self._convert_heavy(input_path)

    def _convert_light(self, input_path: Path) -> str:
        """Convert using markitdown subprocess (FastLane pattern)."""
        output_path = input_path.with_suffix(".md")
        try:
            result = subprocess.run(
                ["markitdown", str(input_path), "-o", str(output_path)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                try:
                    return output_path.read_text(encoding="utf-8")
                finally:
                    if output_path.exists():
                        output_path.unlink()
            else:
                error_msg = result.stderr.decode("utf-8") if result.stderr else "Unknown error"
                raise RuntimeError(
                    f"markitdown conversion failed (exit code {result.returncode}): {error_msg}"
                )
        except FileNotFoundError:
            raise RuntimeError(
                "markitdown not found. Install it with: pip install markitdown"
            ) from None
        except subprocess.TimeoutExpired:
            raise RuntimeError("markitdown timed out after 60 seconds") from None

    def _convert_heavy(self, input_path: Path) -> str:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(str(input_path))
        parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            textpage = page.get_textpage()
            text = textpage.get_text_bounded()
            if text.strip():
                parts.append(f"## Page {page_num + 1}\n\n{text.strip()}")
        return "\n\n".join(parts)