"""CLI entry point for Any2MD conversion tool."""

import asyncio
from pathlib import Path
from typing import Optional

import typer

from pipeline import convert_file, async_convert_batch
from wheels.config import get_config

app = typer.Typer()


@app.command()
def main(
    input_file: Path = typer.Option(..., "--input", "-i", help="Input file or folder"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory (default: same as input)"),
    mode: str = typer.Option("fast", "--mode", help="Conversion mode: 'fast' or 'quality'"),
    pdf_engine: str = typer.Option("light", "--pdf-engine", help="PDF engine: 'light' or 'heavy'"),
    concurrency: Optional[int] = typer.Option(None, "--concurrency", help="Max concurrent conversions"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """Convert a file to markdown.

    Args:
        input_file: Path to the file or directory to convert.
        output_dir: Output directory (default: same as input).
        mode: Conversion mode - 'fast' (default) or 'quality'.
        pdf_engine: PDF engine - 'light' (default) or 'heavy'.
        concurrency: Maximum concurrent conversions (default from config.yaml).
        config: Path to config file.
        verbose: Enable verbose logging.
    """
    if mode not in ("quality", "fast"):
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
            typer.echo(f"No supported files found in: {input_file}")
            return

        concurrency_limit = concurrency if concurrency is not None else get_config().concurrency

        typer.echo(f"Found {len(files)} files, converting with concurrency={concurrency_limit}...")
        results = asyncio.run(async_convert_batch(files, mode, concurrency_limit))
        success_count = sum(1 for r in results if r is not None)
        fail_count = sum(1 for r in results if r is None)
        typer.echo(f"\nCompleted: {success_count} succeeded, {fail_count} failed")
        return

    # Single file handling
    try:
        output_path = convert_file(input_file, mode=mode)
        typer.echo(f"Converted: {output_path}")
    except FileNotFoundError:
        typer.echo(f"Error: File not found: {input_file}", err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        msg = str(e)
        if "50MB" in msg:
            typer.echo("Error: File exceeds 50MB limit", err=True)
        else:
            typer.echo(f"Error: Unsupported format: {input_file.suffix}", err=True)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        typer.echo(f"Error: Conversion failed: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
