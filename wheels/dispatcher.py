"""Dispatcher for routing files to appropriate converters."""

from pathlib import Path
from typing import List, Optional

from wheels.converters.base_converter import BaseConverter
from wheels.converters.converter_html import HtmlConverter
from wheels.converters.converter_mammoth import MammothConverter
from wheels.converters.converter_pandoc import PandocConverter
from wheels.converters.converter_passthrough import PassthroughConverter
from wheels.converters.converter_pdf import PdfConverter
from wheels.fast_lane import FastLane


class FastLaneConverter(BaseConverter):
    """Converter that wraps FastLane for .docx, .xlsx, .pptx, .pdf files."""

    _fast_lane: Optional[FastLane] = None

    @property
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return [".docx", ".xlsx", ".pptx", ".pdf"]

    def convert(self, input_path: Path) -> str:
        """Convert file using FastLane subprocess.

        Args:
            input_path: Path to the input file to convert.

        Returns:
            Markdown content as a string.

        Raises:
            FileNotFoundError: If the input file does not exist.
            RuntimeError: If the conversion fails.
        """
        if FastLaneConverter._fast_lane is None:
            FastLaneConverter._fast_lane = FastLane()

        output_path = input_path.with_suffix(".md")

        success = FastLaneConverter._fast_lane.convert(input_path, output_path)
        if not success:
            raise RuntimeError("Conversion failed")

        try:
            content = output_path.read_text(encoding="utf-8")
        finally:
            if output_path.exists():
                output_path.unlink()

        return content


class Dispatcher:

    def __init__(self, mode: str = "fast", pdf_engine: str = "light"):
        self._mode = mode
        self._pdf_engine = pdf_engine
        self._passthrough_converter = PassthroughConverter()
        self._fastlane_converter = FastLaneConverter()

        self._pandoc_converter: Optional[PandocConverter] = None
        self._mammoth_converter: Optional[MammothConverter] = None
        self._html_converter: Optional[HtmlConverter] = None
        self._pdf_converter: Optional[PdfConverter] = None

    def _get_pandoc_converter(self) -> PandocConverter:
        if self._pandoc_converter is None:
            self._pandoc_converter = PandocConverter()
        return self._pandoc_converter

    def _get_mammoth_converter(self) -> MammothConverter:
        if self._mammoth_converter is None:
            self._mammoth_converter = MammothConverter()
        return self._mammoth_converter

    def _get_html_converter(self) -> HtmlConverter:
        if self._html_converter is None:
            self._html_converter = HtmlConverter()
        return self._html_converter

    def _get_pdf_converter(self) -> PdfConverter:
        if self._pdf_converter is None:
            self._pdf_converter = PdfConverter()
        return self._pdf_converter

    def get_converter(self, file_path: Path) -> BaseConverter:
        suffix = file_path.suffix.lower()

        if self._mode == "quality":
            if suffix in (".md", ".txt"):
                return self._passthrough_converter
            if suffix == ".docx":
                try:
                    return self._get_pandoc_converter()
                except RuntimeError:
                    return self._get_mammoth_converter()
            if suffix in (".pptx", ".xlsx"):
                return self._get_pandoc_converter()
            if suffix in (".html", ".htm"):
                return self._get_html_converter()
            if suffix == ".pdf":
                return self._get_pdf_converter()

        elif self._mode == "fast":
            if suffix in (".md", ".txt"):
                return self._passthrough_converter
            if suffix in (".docx", ".xlsx", ".pptx", ".html", ".htm"):
                return self._fastlane_converter
            if suffix == ".pdf":
                return self._get_pdf_converter()

        raise ValueError(f"Unsupported format: {suffix}")