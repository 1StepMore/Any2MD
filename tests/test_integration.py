"""Integration tests for Any2MD pipeline."""

from pathlib import Path

import pytest

from pipeline import convert_file
from wheels.exceptions import FileTooLargeError, UnsupportedFormatError


class TestSingleFileConversion:
    def test_markdown_file_converts_successfully(self, sample_md: Path):
        result = convert_file(sample_md, mode="fast", output_dir=None)
        assert result.exists()
        assert result.suffix == ".md"
        content = result.read_text(encoding="utf-8")
        assert "# Test Document" in content

    def test_text_file_converts_successfully(self, sample_txt: Path):
        result = convert_file(sample_txt, mode="fast", output_dir=None)
        assert result.exists()
        assert result.suffix == ".md"
        content = result.read_text(encoding="utf-8")
        assert "plain text" in content.lower()


class TestFileNotFound:
    def test_nonexistent_file_raises(self, nonexistent_file: Path):
        with pytest.raises(FileNotFoundError):
            convert_file(nonexistent_file)


class TestFileTooLarge:
    def test_large_file_raises(self, large_file: Path):
        with pytest.raises(FileTooLargeError):
            convert_file(large_file)


class TestUnsupportedFormat:
    def test_unknown_extension_gets_markitdown_converter(self, unsupported_file: Path):
        from wheels.dispatcher import Dispatcher
        dispatcher = Dispatcher(mode="fast")
        converter = dispatcher.get_converter(unsupported_file)
        from wheels.converters.converter_markitdown import MarkitdownConverter
        assert isinstance(converter, MarkitdownConverter)


class TestOutputPath:
    def test_output_path_is_markdown(self, sample_md: Path, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result = convert_file(sample_md, mode="fast", output_dir=output_dir)
        assert result.suffix == ".md"

    def test_output_path_unique_increments(self, sample_md: Path, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result1 = convert_file(sample_md, mode="fast", output_dir=output_dir)
        result2 = convert_file(sample_md, mode="fast", output_dir=output_dir)
        assert result1 != result2
        assert result1.stem.startswith(sample_md.stem)
        assert result2.stem.startswith(sample_md.stem)


class TestPassthroughFormats:
    def test_md_passthrough(self, sample_md: Path):
        result = convert_file(sample_md, mode="fast")
        content = result.read_text(encoding="utf-8")
        assert "# Test Document" in content

    def test_txt_passthrough(self, sample_txt: Path):
        result = convert_file(sample_txt, mode="fast")
        content = result.read_text(encoding="utf-8")
        assert "plain text" in content.lower()
