# Any2MD MVP Phase 1 - Notepad

## Conventions
- Use `pathlib.Path` for all file paths
- Use UTF-8 encoding for all file I/O
- Exit codes: 0=success, 1=error, 2=markitdown missing
- 60-second timeout for markitdown subprocess
- 50MB max file size

## Gotchas
- Windows paths - use Path from pathlib
- markitdown command: `markitdown {input} -o {output}`
- BOM character: `\ufeff`

## Architecture Decisions
- Fast lane only (no quality channel/pypandoc)
- Extension-based dispatch (no magic bytes)
- Single file CLI input only
- Output to same directory as input

## [2026-05-05] Task 1: base_converter.py
- Created abstract BaseConverter class with convert() and supported_extensions
- Verify: python -c "from wheels.converters.base_converter import BaseConverter; print('OK')"

## [2026-05-05] Task 2: converter_passthrough.py
- Created PassthroughConverter inheriting from BaseConverter
- supported_extensions = ['.md', '.txt']
- convert() reads file via Path.read_text(encoding='utf-8')

## [2026-05-05] Task 4: cleaner.py
- Created Cleaner class with clean() static method
- Removes BOM (`\ufeff` at start), normalizes line endings (`\r\n`, `\r` -> `\n`)
- Collapses 3+ consecutive blank lines to 2
- Code blocks (```) preserved via placeholder strategy: `<!--CB0-->`, `<!--CB1-->`
- Strip trailing whitespace on lines using `re.MULTILINE` flag
- All transformations use re.sub()

## [2026-05-05] Task 3: fast_lane.py
- Created FastLane class wrapping markitdown subprocess
- convert() runs: markitdown input -o output with 60s timeout
- Returns True on success, False on failure/missing
- _check_markitdown_available() helper checks for markitdown in PATH

## [2026-05-05] Task 5: dispatcher.py
- Created Dispatcher class with get_converter(file_path) method
- .md/.txt → PassthroughConverter (lazy-loaded single instance)
- .docx/.xlsx/.pptx/.pdf → FastLaneConverter (wraps FastLane subprocess)
- Unknown extension → raises ValueError(f"Unsupported format: {suffix}")
- FastLaneConverter uses temp file with .md suffix, cleans up after reading

## [2026-05-05] Task 6: pipeline.py
- Created convert_file(input_path) → Path function
- File size check: 50MB limit
- Naming conflict: stem_1.md, stem_2.md pattern
- Cleaner applied to all output
## [2026-05-05] Task 7: cli.py
- Created Typer CLI with main() command
- Exit codes: 0=success, 1=error, 2=markitdown missing
- Error handling for FileNotFoundError, ValueError, RuntimeError
- Use typer.echo() for output and typer.Exit() for exit codes

## [2026-05-05 09:10] Task 8: Integration test
- Ran end-to-end tests
- Help command: works (exit 0, shows usage)
- .md passthrough: works (exit 0, content preserved)
- .txt passthrough: works (exit 0, content preserved)
- File not found error: works (exit 1, error to stderr)
- File size >50MB: works (exit 1, "exceeds 50MB limit")
- Naming conflict: works (increment suffix pattern)
- Evidence saved to `.sisyphus/evidence/integration/`
- .docx conversion NOT tested (markitdown not available in environment)
