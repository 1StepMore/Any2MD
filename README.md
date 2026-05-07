# Any2MD - 格式工厂分发引擎

> Universal document to Markdown converter with quality/fast dual-mode pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Any2MD** converts documents to Markdown with two processing modes:
- **Quality Mode**: Uses specialized converters (pypandoc, mammoth, markdownify) for superior output
- **Fast Mode**: Uses markitdown for quick "good enough" results

## Features

- **Dual-Mode Pipeline**: Quality vs Fast mode for optimal results
- **PDF Heavy Channel**: MarkItDown (primary) + pypdfium2 (fallback)
- **Async Batch Processing**: Concurrent file conversion with Semaphore control
- **Smart Retry**: Tenacity-based retry for transient failures
- **Non-Destructive Output**: Auto-incremented filenames, never overwrites
- **Organized Output**: Folder batch outputs to `{folder}_converted/`
- **BAT Drag-and-Drop**: Zero-config usage on Windows

## Quick Start

### Installation

```bash
# From source (development)
git clone https://github.com/1StepMore/Any2MD.git
cd Any2MD
pip install -e .

# Or install from PyPI (when available)
pip install any2md
```

### Usage

**Drag-and-Drop (Windows)**
```
1. Drag a file onto bat\run.bat
2. Done! Markdown appears next to original
```

**Drag-and-Drop Folder (Windows)**
```
1. Drag a folder onto bat\run.bat
2. Done! Markdown files appear in {folder}_converted/
```

**Command Line**

```bash
# Single file conversion
python cli.py -i document.pdf

# With quality mode (better output)
python cli.py -i document.docx --mode quality

# Batch folder processing
python cli.py -i ./documents --concurrency 4

# Verbose logging
python cli.py -i document.pdf --verbose

# Full options
python cli.py --help
```

## Python API

```python
from any2md import convert_to_markdown

# Basic usage
md = convert_to_markdown("document.pdf")
print(md)

# With options
md = convert_to_markdown("document.docx", mode="quality")
md = convert_to_markdown("document.pdf", mode="fast", pdf_engine="heavy")

# Error handling
from any2md import (
    convert_to_markdown,
    FileTooLargeError,
    UnsupportedFormatError,
    ConversionError,
)

try:
    md = convert_to_markdown("document.pdf")
except FileTooLargeError:
    print("File too large (max 50MB)")
except UnsupportedFormatError:
    print("Format not supported")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```

## CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input file or folder | **Required** |
| `--output` | `-o` | Output directory | Same as input |
| `--mode` | - | `quality` or `fast` | From config |
| `--pdf-engine` | - | `light` (markitdown) or `heavy` (MarkItDown) | From config |
| `--concurrency` | - | Max parallel conversions | From config |
| `--config` | - | Config file path | `config.yaml` |
| `--verbose` | `-v` | Enable debug logging | `false` |

## Configuration

Edit `config.yaml`:

```yaml
# Output mode: quality (best) or fast (quick)
output_mode: fast

# PDF engine: light (markitdown) or heavy (MarkItDown -> pypdfium2)
pdf_engine: light

# Max file size (MB) - files larger are skipped
max_file_size: 50

# Async concurrency level
concurrency: 4

# Retry attempts for transient failures
retry_count: 3
```

> Tip: You can also access config programmatically via `from wheels.config import get_config`

## Architecture

```
Any2MD/
├── bat/
│   └── run.bat              # Windows drag-and-drop entry
├── wheels/
│   ├── converters/         # Format-specific converters
│   │   ├── converter_pandoc.py   # Quality: docx/pptx/xlsx
│   │   ├── converter_mammoth.py   # Quality: complex DOCX
│   │   ├── converter_html.py      # Quality: HTML
│   │   ├── converter_pdf.py       # Dynamic: PDF (light/heavy)
│   │   └── converter_passthrough.py # .md/.txt passthrough
│   │   └── converter_markitdown.py # Fast: csv/json/xml/yaml/epub/zip
│   ├── dispatcher.py        # Format routing
│   ├── fast_lane.py        # markitdown wrapper
│   ├── cleaner.py           # Text post-processing
│   └── logger.py           # Logging configuration
├── cli.py                  # Typer CLI entry
├── pipeline.py              # Async batch orchestration
├── config.yaml             # Configuration
└── requirements.txt        # Dependencies
```

## Supported Formats

| Format | Quality Mode | Fast Mode |
|--------|-------------|-----------|
| .docx | pypandoc → mammoth fallback | markitdown |
| .pptx / .xlsx | pypandoc | markitdown |
| .html / .htm | markdownify | markitdown |
| .pdf | MarkItDown (heavy) or markitdown (light) | markitdown |
| .md / .txt | passthrough | passthrough |
| .csv / .json / .xml | - | markitdown |
| .yaml / .yml | - | markitdown |
| .epub | - | markitdown |
| .zip | - | markitdown |

## PDF Engine

**Light Mode**: Uses markitdown with zero external dependencies.

**Heavy Mode**: Uses Microsoft MarkItDown for table/layout detection, falls back to pypdfium2 for raw text extraction.

Install heavy dependencies:
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr poppler-utils

# Windows (requires admin)
winget install --id UB-Mannheim.TesseractOCR -e
winget install --id oschwartz10612.Poppler -e
```

## Error Handling

- **File too large**: Files >50MB are skipped with error log
- **Unsupported format**: Clear error message with supported formats
- **Missing dependencies**: Install instructions in error message
- **Transient failures**: Automatic retry (up to 3 attempts)
- **Batch continuation**: Single file failure doesn't stop batch processing

## Development

```bash
# Run CLI help
python cli.py --help

# Test with sample files
python cli.py -i sample.docx --mode quality

# Check environment
python check_env.py
```

## License

MIT License - see LICENSE file for details

## Credits

Built with these excellent open-source libraries:
- [pypandoc](https://github.com/JessicaTegner/pypandoc) - Pandoc wrapper
- [mammoth](https://github.com/mwilliamson/python-mammoth) - DOCX to Markdown
- [markdownify](https://github.com/matthewwithanm/markdownify) - HTML to Markdown
- [markitdown](https://github.com/microsoft/markitdown) - Microsoft format converter
- [pypdfium2](https://github.com/pypdfium2/pypdfium2) - PDF rendering
- [tenacity](https://github.com/jd/tenacity) - Retry logic
- [Typer](https://github.com/tiangolo/typer) - CLI framework