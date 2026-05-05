"""CLI entry point for Any2MD conversion tool."""

from pathlib import Path

import typer

from pipeline import convert_file

app = typer.Typer()


@app.command()
def main(
    input_file: Path,
    mode: str = typer.Option("fast", help="Conversion mode: 'fast' or 'quality'"),
):
    """Convert a file to markdown.

    Args:
        input_file: Path to the file to convert.
        mode: Conversion mode - 'fast' (default) or 'quality'.
    """
    if mode not in ("quality", "fast"):
        raise typer.BadParameter("Mode must be 'quality' or 'fast'", param_name="mode")

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
