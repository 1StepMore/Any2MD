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
        try:
            result = subprocess.run(
                ["markitdown", str(input_path)],
                capture_output=True,
                timeout=60,
            )
            if result.returncode == 0:
                return result.stdout.decode("utf-8")
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
        """Convert using marker or docling (dynamic import inside convert())."""
        # Try marker first, then docling fallback
        error_messages = []

        # Try marker
        try:
            marker = importlib.import_module("marker")
            # Use marker.convert directly
            from marker.convert import convert as marker_convert

            result = marker_convert(input_path)
            return result
        except ImportError as e:
            error_messages.append(f"marker: {e}")

        # Try docling
        try:
            docling = importlib.import_module("docling")
            # Use docling backend
            from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
            from docling.datamodel.base_models import InputDocument
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.pipeline.standard_pipeline import StandardPipeline

            # Minimal docling conversion
            pipeline_options = PdfPipelineOptions()
            doc = PyPdfiumDocumentBackend(InputDocument.from_path(input_path, pipeline_options=pipeline_options))
            converter = StandardPipeline(pipeline_options)
            result = converter.process(doc)
            return result.markdown
        except ImportError as e:
            error_messages.append(f"docling: {e}")

        # All engines failed - provide clear install instructions
        install_instructions = (
            "No PDF heavy engine available. Install one of:\n"
            "  pip install marker  # Primary choice (may not work with Python 3.13+)\n"
            "  pip install docling  # Fallback option\n"
            "Also ensure system dependencies: tesseract, poppler-utils (pdftoppm, pdfinfo)"
        )
        raise RuntimeError(
            f"PDF heavy conversion failed. Tried: {', '.join(error_messages)}\n\n{install_instructions}"
        ) from None