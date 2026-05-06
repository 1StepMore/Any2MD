"""Pipeline orchestration for single file conversion."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from wheels.dispatcher import Dispatcher
from wheels.cleaner import Cleaner
from wheels.logger import logger

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
_log_lock = asyncio.Lock()


def convert_file(input_path: Path, mode: str = "fast", pdf_engine: str = "light", output_dir: Optional[Path] = None) -> Path:
    """Convert a file to markdown.

    Args:
        input_path: Path to input file
        mode: Conversion mode - "fast" (default) or "quality"
        pdf_engine: PDF engine - "light" (default) or "heavy"
        output_dir: Output directory (default: same as input)

    Returns:
        Path to output markdown file

    Raises:
        FileNotFoundError: If input file does not exist
        ValueError: If file exceeds 50MB or format unsupported
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    size = input_path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds 50MB limit: {input_path}")

    dispatcher = Dispatcher(mode=mode, pdf_engine=pdf_engine)
    converter = dispatcher.get_converter(input_path)

    markdown_text = converter.convert(input_path)
    cleaned_text = Cleaner.clean(markdown_text)

    output_path = _get_unique_output_path(input_path, output_dir)

    output_path.write_text(cleaned_text, encoding='utf-8')

    return output_path


def _get_unique_output_path(input_path: Path, output_dir: Optional[Path] = None) -> Path:
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = input_path.stem
        output_path = output_dir / f"{stem}.md"
        counter = 1
        while output_path.exists():
            output_path = output_dir / f"{stem}_{counter}.md"
            counter += 1
        return output_path

    if not input_path.exists():
        return input_path.with_suffix('.md')

    stem = input_path.stem
    parent = input_path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}.md"
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
    input_path: Path, mode: str, pdf_engine: str, output_dir: Optional[Path], semaphore: asyncio.Semaphore
) -> Path:
    async with semaphore:
        await _async_log(input_path, "started")
        try:
            result = convert_file(input_path, mode, pdf_engine, output_dir)
            await _async_log(input_path, f"completed -> {result}")
            return result
        except Exception as e:
            await _async_log(input_path, f"failed: {e}")
            return None


async def async_convert_batch(
    paths: List[Path], mode: str, concurrency: int, pdf_engine: str = "light", output_dir: Optional[Path] = None
) -> List[Path]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [_async_convert_single(p, mode, pdf_engine, output_dir, semaphore) for p in paths]
    results = await asyncio.gather(*tasks)
    return list(results)