"""Test fixtures for Any2MD test suite."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    content = "# Test Document\n\nThis is a test file.\n\n## Section 1\n\nSome content here."
    file_path = tmp_path / "sample.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_txt(tmp_path: Path) -> Path:
    content = "This is a plain text file.\n\nNo markdown formatting."
    file_path = tmp_path / "sample.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_html(tmp_path: Path) -> Path:
    content = "<html><head><title>Test</title></head><body><h1>Hello</h1><p>World</p></body></html>"
    file_path = tmp_path / "sample.html"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    content = "name,age,city\nAlice,30,NYC\nBob,25,LA"
    file_path = tmp_path / "sample.csv"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_json(tmp_path: Path) -> Path:
    content = '{"name": "test", "value": 42}'
    file_path = tmp_path / "sample.json"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def large_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "large_file.bin"
    chunk_size = 1024 * 1024
    num_chunks = 52
    with open(file_path, "wb") as f:
        for _ in range(num_chunks):
            f.write(b"\x00" * chunk_size)
    return file_path


@pytest.fixture
def unsupported_file(tmp_path: Path) -> Path:
    content = "This file has an unsupported extension."
    file_path = tmp_path / "sample.xyz"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def nonexistent_file(tmp_path: Path) -> Path:
    return tmp_path / "does_not_exist.txt"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_config():
    from wheels.config import Config
    return Config(
        output_mode="fast",
        pdf_engine="light",
        max_file_size=50,
        concurrency=4,
        retry_count=3,
        output_dir=None,
        log_level="info"
    )
