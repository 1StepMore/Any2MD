"""Pipeline orchestration for single file conversion."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from wheels.dispatcher import Dispatcher
from wheels.cleaner import Cleaner
from wheels.logger import logger

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
_log_lock = asyncio.Lock()


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


async def _async_log(file_path: Path, status: str) -> None:
    """Thread-safe logging via shared lock."""
    async with _log_lock:
        if "completed" in status:
            logger.info(f"[{file_path}] {status}")
        elif "failed" in status:
            logger.error(f"[{file_path}] {status}")
        else:
            logger.info(f"[{file_path}] {status}")


async def _async_convert_single(
    input_path: Path, mode: str, semaphore: asyncio.Semaphore
) -> Path:
    """Async wrapper for single file conversion with semaphore control.

    Args:
        input_path: Path to input file
        mode: Conversion mode - "fast" or "quality"
        semaphore: Semaphore to limit concurrency

    Returns:
        Path to output markdown file
    """
    async with semaphore:
        await _async_log(input_path, "started")
        try:
            result = convert_file(input_path, mode)
            await _async_log(input_path, f"completed -> {result}")
            return result
        except Exception as e:
            await _async_log(input_path, f"failed: {e}")
            return None  # Don't re-raise - let batch continue


async def async_convert_batch(
    paths: List[Path], mode: str, concurrency: int
) -> List[Path]:
    """Convert multiple files concurrently with semaphore-based concurrency control.

    Args:
        paths: List of input file paths
        mode: Conversion mode - "fast" (default) or "quality"
        concurrency: Maximum number of concurrent conversions

    Returns:
        List of output markdown file paths
    """
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [_async_convert_single(p, mode, semaphore) for p in paths]
    results = await asyncio.gather(*tasks)
    return list(results)