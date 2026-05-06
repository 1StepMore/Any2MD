"""CLI entry point for Any2MD conversion tool."""

import asyncio
from pathlib import Path
from typing import Optional

import typer

from pipeline import convert_file, async_convert_batch
from wheels.config import get_config
from wheels.logger import logger, setup_logger

app = typer.Typer()


@app.command()
def main(
    input_file: Path = typer.Option(..., "--input", "-i", help="Input file or folder"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory (default: same as input)"),
    mode: Optional[str] = typer.Option(None, "--mode", help="Conversion mode: 'fast' or 'quality' (default: from config)"),
    pdf_engine: Optional[str] = typer.Option(None, "--pdf-engine", help="PDF engine: 'light' or 'heavy' (default: from config)"),
    concurrency: Optional[int] = typer.Option(None, "--concurrency", help="Max concurrent conversions"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """Convert a file to markdown.

    Args:
        input_file: Path to the file or folder to convert.
        output_dir: Output directory (default: same as input).
        mode: Conversion mode - 'fast' or 'quality' (default from config.yaml).
        pdf_engine: PDF engine - 'light' or 'heavy' (default from config.yaml).
        concurrency: Maximum concurrent conversions (default from config.yaml).
        config: Path to config file.
        verbose: Enable verbose logging.
    """
    # Setup logger with verbose flag
    setup_logger(verbose)

    # Load config for defaults
    cfg = get_config()
    mode = mode if mode is not None else cfg.output_mode
    pdf_engine = pdf_engine if pdf_engine is not None else cfg.pdf_engine

    logger.info(f"Starting conversion: mode={mode}, pdf_engine={pdf_engine}")

    if mode not in ("quality", "fast"):
        logger.error(f"Invalid mode: {mode}")
        raise typer.BadParameter("Mode must be 'quality' or 'fast'", param_name="mode")

    # Directory handling
    if input_file.is_dir():
        files = []
        supported_exts = ['.pdf', '.docx', '.xlsx', '.pptx', '.html', '.htm', '.md', '.txt']
        for ext in supported_exts:
            for f in input_file.rglob(f'*{ext}'):
                if not f.name.startswith('.'):
                    files.append(f)

        if not files:
            logger.warning(f"No supported files found in: {input_file}")
            typer.echo(f"No supported files found in: {input_file}")
            return

        concurrency_limit = concurrency if concurrency is not None else get_config().concurrency

        output_dir = input_file.parent / f"{input_file.name}_converted"
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Batch mode: {len(files)} files, concurrency={concurrency_limit}, output={output_dir}")
        typer.echo(f"Found {len(files)} files, converting to {output_dir}...")
        results = asyncio.run(async_convert_batch(files, mode, concurrency_limit, pdf_engine, output_dir))
        success_count = sum(1 for r in results if r is not None)
        fail_count = sum(1 for r in results if r is None)
        logger.info(f"Batch completed: {success_count} succeeded, {fail_count} failed")
        typer.echo(f"\nCompleted: {success_count} succeeded, {fail_count} failed")
        return

    # Single file handling
    logger.info(f"Converting: {input_file} (mode={mode})")
    try:
        output_path = convert_file(input_file, mode=mode, pdf_engine=pdf_engine)
        logger.info(f"Success: {input_file} -> {output_path}")
        typer.echo(f"Converted: {output_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {input_file}")
        typer.echo(f"Error: File not found: {input_file}", err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        msg = str(e)
        if "50MB" in msg:
            logger.warning(f"File too large: {input_file}")
            typer.echo("Error: File exceeds 50MB limit", err=True)
        else:
            logger.error(f"Unsupported format: {input_file.suffix}")
            typer.echo(f"Error: Unsupported format: {input_file.suffix}", err=True)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        logger.error(f"Conversion failed: {input_file}: {e}")
        typer.echo(f"Error: Conversion failed: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        logger.exception(f"Unexpected error: {input_file}: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
