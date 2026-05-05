"""Pipeline orchestration for single file conversion."""

from pathlib import Path

from wheels.dispatcher import Dispatcher
from wheels.cleaner import Cleaner

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def convert_file(input_path: Path, mode: str = "fast") -> Path:
    """Convert a file to markdown and save alongside the original.

    Args:
        input_path: Path to input file
        mode: Conversion mode - "fast" (default) or "quality"

    Returns:
        Path to output markdown file

    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If file exceeds 50MB or format unsupported
    """
    # 1. Check file exists
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    # 2. Check file size
    size = input_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds 50MB limit: {input_path}")

    # 3. Get converter
    dispatcher = Dispatcher(mode=mode)
    converter = dispatcher.get_converter(input_path)

    # 4. Convert (get markdown text)
    markdown_text = converter.convert(input_path)

    # 5. Clean the text
    cleaned_text = Cleaner.clean(markdown_text)

    # 6. Determine output path with conflict resolution
    output_path = _get_unique_output_path(input_path.with_suffix('.md'))

    # 7. Write output
    output_path.write_text(cleaned_text, encoding='utf-8')

    return output_path


def _get_unique_output_path(path: Path) -> Path:
    """Get unique output path by incrementing suffix if file exists."""
    if not path.exists():
        return path

    stem = path.stem
    parent = path.parent
    suffix = path.suffix

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1