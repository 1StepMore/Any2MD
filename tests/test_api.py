"""API tests for convert_to_markdown function."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from wheels.api import convert_to_markdown
from wheels.exceptions import (
    FileTooLargeError,
    ConversionError,
)


class TestConvertToMarkdown:
    def test_returns_string(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md)

            assert isinstance(result, str)

    def test_mode_fast(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test content", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md, mode="fast")

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["mode"] == "fast"

    def test_mode_quality(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test content", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md, mode="quality")

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["mode"] == "quality"

    def test_pdf_engine_light(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test content", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md, pdf_engine="light")

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["pdf_engine"] == "light"

    def test_pdf_engine_heavy(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test content", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md, pdf_engine="heavy")

            mock_convert.assert_called_once()
            call_kwargs = mock_convert.call_args.kwargs
            assert call_kwargs["pdf_engine"] == "heavy"

    def test_file_not_found_raises(self, nonexistent_file: Path):
        with pytest.raises(FileNotFoundError):
            convert_to_markdown(nonexistent_file)

    def test_file_too_large_raises(self, large_file: Path):
        with pytest.raises(FileTooLargeError):
            convert_to_markdown(large_file)

    def test_conversion_failure_raises(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            mock_convert.side_effect = ConversionError("Conversion failed")

            with pytest.raises(ConversionError):
                convert_to_markdown(sample_md)

    def test_string_path(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(str(sample_md))

            assert isinstance(result, str)

    def test_pathlib_path(self, sample_md: Path, tmp_path: Path):
        with patch("pipeline.convert_file") as mock_convert:
            output_file = tmp_path / "output.md"
            output_file.write_text("# Test", encoding="utf-8")
            mock_convert.return_value = output_file

            result = convert_to_markdown(sample_md)

            assert isinstance(result, str)
