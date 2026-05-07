"""Dispatcher tests for routing files to correct converters."""

from pathlib import Path

import pytest

from wheels.dispatcher import Dispatcher
from wheels.converters.converter_passthrough import PassthroughConverter
from wheels.converters.converter_markitdown import MarkitdownConverter


class TestDispatcherQualityMode:
    def test_md_extension_returns_passthrough_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.md")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, PassthroughConverter)

    def test_txt_extension_returns_passthrough_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.txt")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, PassthroughConverter)

    def test_docx_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.docx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_pptx_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.pptx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_xlsx_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.xlsx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_html_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.html")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_htm_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.htm")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_pdf_extension_returns_converter(self):
        dispatcher = Dispatcher(mode="quality")
        file_path = Path("test.pdf")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")


class TestDispatcherFastMode:
    def test_md_extension_returns_passthrough_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.md")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, PassthroughConverter)

    def test_txt_extension_returns_passthrough_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.txt")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, PassthroughConverter)

    def test_docx_extension_returns_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.docx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_xlsx_extension_returns_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.xlsx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_pptx_extension_returns_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.pptx")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_html_extension_returns_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.html")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")

    def test_pdf_extension_returns_converter_fast_mode(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.pdf")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")


class TestDispatcherUnknownExtension:
    def test_unknown_extension_returns_markitdown_converter(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.xyz")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, MarkitdownConverter)

    def test_csv_extension_returns_markitdown_converter(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.csv")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, MarkitdownConverter)

    def test_json_extension_returns_markitdown_converter(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.json")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, MarkitdownConverter)

    def test_xml_extension_returns_markitdown_converter(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.xml")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, MarkitdownConverter)


class TestDispatcherCaseInsensitive:
    def test_uppercase_extension(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.MD")
        converter = dispatcher.get_converter(file_path)
        assert isinstance(converter, PassthroughConverter)

    def test_mixed_case_extension(self):
        dispatcher = Dispatcher(mode="fast")
        file_path = Path("test.HtML")
        converter = dispatcher.get_converter(file_path)
        assert hasattr(converter, "convert")
