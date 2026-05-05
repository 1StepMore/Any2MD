# Any2MD MVP Phase 1 Implementation Plan

## TL;DR

> **Quick Summary**: Implement minimal end-to-end pipeline to convert files to Markdown via markitdown fast lane only.
>
> **Deliverables**:
> - `cli.py` - Typer CLI entry point with --input parameter
> - `pipeline.py` - Synchronous orchestration pipeline
> - `wheels/dispatcher.py` - File format sniffing and routing
> - `wheels/converters/base_converter.py` - Abstract converter interface
> - `wheels/converters/converter_passthrough.py` - Direct copy for .md/.txt
> - `wheels/fast_lane.py` - markitdown subprocess wrapper
> - `wheels/cleaner.py` - Regex post-processing (normalize line endings, collapse blank lines)
> - Working end-to-end flow: file input → format sniff → convert → clean → output
>
> **Estimated Effort**: Short (3-5 hours of Vibe Coding)
> **Parallel Execution**: YES - 2 waves of 4 tasks each
> **Critical Path**: cli.py → pipeline.py → dispatcher.py → fast_lane.py → cleaner.py → integration test

---

## Context

### Original Request
MVP Phase 1 implementation per user's specification:
- Single file CLI input
- File magic number sniffing (filetype)
- All formats go through markitdown fast lane (no quality channel)
- .md/.txt passthrough (no conversion needed)
- Light regex post-processing (clean consecutive blank lines, normalize line endings)
- Deterministic file naming (auto-remove suffix, increment on conflict)
- Basic Typer CLI with --input parameter

### Metis Review Findings

**Identified Gaps (addressed in plan)**:
- Exit code scheme not defined → Resolved: 0=success, 1=error, 2=markitdown missing
- Overwrite behavior ambiguous → Resolved: Always overwrite (MVP simplicity)
- markitdown missing handling unclear → Resolved: Clear error with install instructions
- Max file size not enforced → Resolved: 50MB limit before conversion
- Timeout not specified → Resolved: 60-second timeout on markitdown subprocess
- BOM handling undefined → Resolved: Strip UTF-8 BOM in cleaner.py

### Assumptions (Auto-Resolved)
- markitdown works on Windows (pip install markitdown is cross-platform)
- Extension-based dispatch is sufficient for MVP (no magic bytes needed)
- Output goes to same directory as input
- UTF-8 encoding for all file I/O
- Python 3.8+ target

---

## Work Objectives

### Core Objective
Build minimal viable pipeline that: accepts a file path → sniffs format → routes to markitdown → post-processes → outputs .md file

### Concrete Deliverables
- `cli.py` - Typer app with `any2md <input>` signature
- `pipeline.py` - `convert_file(file_path) -> output_path` function
- `wheels/dispatcher.py` - `Dispatcher.dispatch(file_path) -> converter`
- `wheels/converters/base_converter.py` - `BaseConverter` abstract class
- `wheels/converters/converter_passthrough.py` - PassthroughConverter for .md/.txt
- `wheels/fast_lane.py` - `FastLane.convert(file_path) -> markdown_text`
- `wheels/cleaner.py` - `Cleaner.clean(text) -> cleaned_text`

### Definition of Done
- [ ] `any2md document.docx` produces `document.md`
- [ ] `any2md document.md` produces unchanged `document.md` (passthrough)
- [ ] `any2md nonexistent.docx` exits with code 1 and error message
- [ ] `any2md` without arguments shows help text

### Must Have
- Typer CLI with --input argument
- markitdown subprocess wrapper with 60s timeout
- Passthrough for .md and .txt files
- Regex post-processing (collapse 3+ blank lines to 2, normalize CRLF to LF)
- 50MB file size check before conversion
- Clear error messages (exit codes + stderr)

### Must NOT Have (Guardrails)
- No batch processing / multiple files
- No quality channel / pypandoc / mammoth
- No directory recursion
- No --verbose, --quiet, --log-level flags
- No progress bars or spinners
- No stdin/stdout support
- No configuration file changes (config.yaml is "done")

---

## Verification Strategy

### Test Infrastructure
- **Infrastructure exists**: NO - creating from scratch
- **Automated tests**: None (Vibe Coding style - manual per-module testing)
- **Framework**: None (simple print-based verification)

### QA Policy (MANDATORY)
Every task includes agent-executed QA scenarios. Verification is manual through:
- CLI invocation tests
- File existence checks
- Content comparison

Evidence saved to `.sisyphus/evidence/task-{N}-{scenario}.txt`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - 4 tasks, can run in parallel):
├── Task 1: base_converter.py - Abstract interface (quick)
├── Task 2: converter_passthrough.py - Passthrough implementation (quick)
├── Task 3: fast_lane.py - markitdown wrapper (quick)
└── Task 4: cleaner.py - Regex post-processing (quick)

Wave 2 (Orchestration - 4 tasks, depends on Wave 1):
├── Task 5: dispatcher.py - Format routing (depends: base_converter)
├── Task 6: pipeline.py - Pipeline orchestration (depends: dispatcher, fast_lane, cleaner)
├── Task 7: cli.py - Typer CLI entry (depends: pipeline)
└── Task 8: Integration test - End-to-end verification (depends: all)

Critical Path: T1 → T5 → T6 → T7 → T8
Parallel Speedup: ~50% faster with Wave 1 parallelization
Max Concurrent: 4 (Wave 1), 4 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| T1 (base_converter.py) | None | T5 |
| T2 (converter_passthrough.py) | T1 | T5 |
| T3 (fast_lane.py) | None | T6 |
| T4 (cleaner.py) | None | T6 |
| T5 (dispatcher.py) | T1, T2 | T6 |
| T6 (pipeline.py) | T3, T4, T5 | T7 |
| T7 (cli.py) | T6 | T8 |
| T8 (Integration test) | T7 | Final verification |

---

## TODOs

### Wave 1 (Foundation - 4 tasks, parallel execution)

- [x] 1. **base_converter.py - Abstract converter interface**

  **What to do**:
  - Create `wheels/converters/base_converter.py`
  - Define abstract class `BaseConverter` with:
    - Abstract method `convert(input_path: Path) -> str`
    - Abstract property `supported_extensions: List[str]`
  - Include docstring explaining interface contract
  - Use `from abc import ABC, abstractmethod`
  - Use `from pathlib import Path`

  **Must NOT do**:
  - No concrete implementations here
  - No markitdown imports
  - No file I/O operations

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple interface definition, no complex logic
  - **Skills**: None required
  - **Justification**: Single file with pure abstract class, no business logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T2, T3, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 5 (dispatcher.py)
  - **Blocked By**: None

  **References**:
  - `wheels/converters/__init__.py:1-5` - Empty package structure to follow
  - `wheels/config.py:1-30` - Use same `from pathlib import Path` pattern

  **Acceptance Criteria**:
  - [ ] File created: `wheels/converters/base_converter.py`
  - [ ] `from wheels.converters.base_converter import BaseConverter` succeeds
  - [ ] `BaseConverter` has abstract `convert` method
  - [ ] `BaseConverter` has abstract `supported_extensions` property

  **QA Scenarios**:

  ```
  Scenario: Import verification
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.base_converter import BaseConverter; print('OK')"
    Expected Result: Output "OK" with exit code 0
    Failure Indicators: ImportError, TypeError on abstract method
    Evidence: .sisyphus/evidence/task-1-import.txt

  Scenario: Abstract class enforcement
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.base_converter import BaseConverter; c = BaseConverter()"
    Expected Result: TypeError: Can't instantiate abstract class
    Failure Indicators: Class instantiated successfully (should fail)
    Evidence: .sisyphus/evidence/task-1-abstract.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-import.txt - Import success proof
  - [ ] task-1-abstract.txt - Abstract enforcement proof

  **Commit**: YES
  - Message: `feat(mvp): add base converter abstract interface`
  - Files: `wheels/converters/base_converter.py`

- [x] 2. **converter_passthrough.py - Passthrough converter**

  **What to do**:
  - Create `wheels/converters/converter_passthrough.py`
  - Implement `PassthroughConverter(BaseConverter)`:
    - `supported_extensions = ['.md', '.txt']`
    - `convert(input_path: Path) -> str`: Read file as text, return content
  - Use UTF-8 encoding for reading
  - Use `pathlib.Path.read_text(encoding='utf-8')`

  **Must NOT do**:
  - No conversion logic (just return file contents)
  - No writing to output

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple file read operation
  - **Skills**: None required
  - **Justification**: Simple subclass with one method, follows established pattern

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T3, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 5 (dispatcher.py)
  - **Blocked By**: Task 1 (needs base class)

  **References**:
  - `wheels/converters/base_converter.py` - Inherit from this
  - `wheels/config.py:15-20` - UTF-8 encoding pattern

  **Acceptance Criteria**:
  - [ ] File created: `wheels/converters/converter_passthrough.py`
  - [ ] `PassthroughConverter` inherits from `BaseConverter`
  - [ ] `supported_extensions` returns `['.md', '.txt']`
  - [ ] `convert()` returns file contents as string

  **QA Scenarios**:

  ```
  Scenario: Basic passthrough for .md file
    Tool: Bash
    Preconditions: Create test.md with "# Hello World\n\nThis is a test."
    Steps:
      1. Run: python -c "from wheels.converters.converter_passthrough import PassthroughConverter; p = PassthroughConverter(); print(p.convert(Path('test.md')))" > evidence.txt
    Expected Result: File content printed, exit 0
    Failure Indicators: FileNotFoundError, empty output
    Evidence: .sisyphus/evidence/task-2-passthrough-md.txt

  Scenario: Passthrough for .txt file
    Tool: Bash
    Preconditions: Create test.txt with "Plain text content"
    Steps:
      1. Run: python -c "from wheels.converters.converter_passthrough import PassthroughConverter; p = PassthroughConverter(); print(p.convert(Path('test.txt')))" > evidence.txt
    Expected Result: "Plain text content" printed, exit 0
    Failure Indicators: FileNotFoundError, empty output
    Evidence: .sisyphus/evidence/task-2-passthrough-txt.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-passthrough-md.txt - .md passthrough proof
  - [ ] task-2-passthrough-txt.txt - .txt passthrough proof

  **Commit**: YES (grouped with T1)
  - Message: `feat(mvp): add base converter interface and passthrough`
  - Files: `wheels/converters/base_converter.py`, `wheels/converters/converter_passthrough.py`

- [x] 3. **fast_lane.py - markitdown wrapper**

  **What to do**:
  - Create `wheels/fast_lane.py`
  - Implement `FastLane` class:
    - `convert(input_path: Path, output_path: Path) -> bool`: Run `markitdown {input} -o {output}`
    - Timeout: 60 seconds
    - Capture stderr for error reporting
    - Return True on success, False on failure
  - Handle `FileNotFoundError` when markitdown not found
  - Implement `_check_markitdown_available() -> bool` private method

  **Must NOT do**:
  - No direct file content reading (subprocess only)
  - No quality fallback

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Wrapper code, straightforward subprocess call
  - **Skills**: None required
  - **Justification**: Simple subprocess wrapper, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T2, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6 (pipeline.py)
  - **Blocked By**: None

  **References**:
  - `subprocess.run()` documentation - Use `capture_output=True`, `timeout=60`
  - Windows command: `markitdown {input} -o {output}`

  **Acceptance Criteria**:
  - [ ] File created: `wheels/fast_lane.py`
  - [ ] `FastLane.convert()` returns True on success
  - [ ] `FastLane.convert()` returns False when markitdown missing
  - [ ] Timeout works (60 seconds max)
  - [ ] stderr is captured

  **QA Scenarios**:

  ```
  Scenario: markitdown available - success case
    Tool: Bash
    Preconditions: Create small.docx with content
    Steps:
      1. Run: python -c "from wheels.fast_lane import FastLane; f = FastLane(); result = f.convert(Path('small.docx'), Path('small.md')); print('SUCCESS' if result else 'FAILED')"
    Expected Result: "SUCCESS" printed, small.md created
    Failure Indicators: False returned, file not created
    Evidence: .sisyphus/evidence/task-3-markitdown-success.txt

  Scenario: markitdown not available - error case
    Tool: Bash
    Preconditions: None
    Steps:
      1. Modify PATH temporarily to exclude markitdown
      2. Run: python -c "from wheels.fast_lane import FastLane; f = FastLane(); f.convert(Path('test.docx'), Path('test.md'))"
    Expected Result: False returned, error message printed to stderr
    Failure Indicators: Exception raised, no error message
    Evidence: .sisyphus/evidence/task-3-markitdown-missing.txt
  ```

  **Evidence to Capture**:
  - [ ] task-3-markitdown-success.txt - Success case proof
  - [ ] task-3-markitdown-missing.txt - Missing tool proof

  **Commit**: YES
  - Message: `feat(mvp): add fast lane markitdown wrapper`
  - Files: `wheels/fast_lane.py`

- [x] 4. **cleaner.py - Regex post-processing**

  **What to do**:
  - Create `wheels/cleaner.py`
  - Implement `Cleaner` class with static `clean(text: str) -> str`:
    - Remove UTF-8 BOM if present (`\ufeff` at start)
    - Normalize line endings: `\r\n` → `\n`, `\r` → `\n`
    - Collapse consecutive blank lines: `\n{3,}` → `\n\n`
    - Strip trailing whitespace on lines
    - Preserve code blocks (don't collapse blank lines inside ```)
  - Use `re.sub()` for all transformations

  **Must NOT do**:
  - No file I/O (text only)
  - No markdown-specific logic beyond whitespace

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple regex operations
  - **Skills**: None required
  - **Justification**: Pure text transformation, no complex business logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T2, T3)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6 (pipeline.py)
  - **Blocked By**: None

  **References**:
  - `re.sub()` pattern: `\r\n|\r|\n` for line ending normalization
  - Unicode BOM: `\ufeff`

  **Acceptance Criteria**:
  - [ ] File created: `wheels/cleaner.py`
  - [ ] `Cleaner.clean()` removes BOM
  - [ ] `Cleaner.clean()` normalizes CRLF to LF
  - [ ] `Cleaner.clean()` collapses 3+ blank lines to 2
  - [ ] Code blocks (```) are preserved (not stripped)

  **QA Scenarios**:

  ```
  Scenario: BOM removal
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.cleaner import Cleaner; text = '\ufeff# Hello'; result = Cleaner.clean(text); print('BOM_REMOVED' if not result.startswith('\ufeff') else 'BOM_STILL_PRESENT')"
    Expected Result: "BOM_REMOVED"
    Failure Indicators: BOM still in output
    Evidence: .sisyphus/evidence/task-4-bom.txt

  Scenario: Line ending normalization
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.cleaner import Cleaner; text = 'Line1\r\nLine2\r\n\r\n\r\nLine3'; result = Cleaner.clean(text); print('NORMALIZED' if '\r' not in result else 'STILL_HAS_CR')"
    Expected Result: "NORMALIZED", no '\r' in output
    Failure Indicators: Carriage returns still present
    Evidence: .sisyphus/evidence/task-4-lineendings.txt

  Scenario: Blank line collapse
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.cleaner import Cleaner; text = 'Para1\n\n\n\n\nPara2'; result = Cleaner.clean(text); print('COLLAPSED' if result == 'Para1\n\n\nPara2' else f'WRONG: {repr(result)}')"
    Expected Result: "COLLAPSED" with exactly 2 consecutive newlines
    Failure Indicators: More than 2 newlines, or less than 2
    Evidence: .sisyphus/evidence/task-4-blanklines.txt

  Scenario: Code block preservation
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.cleaner import Cleaner; text = '# Header\n\n```\n\n\n\n```'; result = Cleaner.clean(text); print('PRESERVED' if '\n\n\n\n' in result else 'CORRUPTED')"
    Expected Result: "PRESERVED" - blank lines inside code blocks NOT collapsed
    Failure Indicators: Blank lines collapsed inside code block
    Evidence: .sisyphus/evidence/task-4-codeblock.txt
  ```

  **Evidence to Capture**:
  - [ ] task-4-bom.txt - BOM removal proof
  - [ ] task-4-lineendings.txt - Line ending normalization proof
  - [ ] task-4-blanklines.txt - Blank line collapse proof
  - [ ] task-4-codeblock.txt - Code block preservation proof

  **Commit**: YES (grouped with T3)
  - Message: `feat(mvp): add fast lane and cleaner`
  - Files: `wheels/fast_lane.py`, `wheels/cleaner.py`

---

### Wave 2 (Orchestration - 4 tasks, sequential per group)

- [x] 5. **dispatcher.py - Format routing**

  **What to do**:
  - Create `wheels/dispatcher.py`
  - Implement `Dispatcher` class:
    - `get_converter(file_path: Path) -> BaseConverter`: Return appropriate converter based on extension
    - Extension mapping:
      - `.md`, `.txt` → `PassthroughConverter`
      - `.docx`, `.xlsx`, `.pptx`, `.pdf` → `FastLane` (via markitdown)
      - Unknown → raise `ValueError(f"Unsupported format: {suffix}")
  - Use `file_path.suffix.lower()` for extension check
  - Lazy-load converter instances

  **Must NOT do**:
  - No direct conversion logic (delegate to converters)
  - No magic number sniffing (extension only for MVP)

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple routing logic
  - **Skills**: None required
  - **Justification**: Simple dispatch table, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO (after Wave 1)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 6 (pipeline.py)
  - **Blocked By**: Tasks 1, 2 (base_converter, passthrough)

  **References**:
  - `wheels/converters/base_converter.py` - Converter interface
  - `wheels/converters/converter_passthrough.py` - Passthrough reference
  - `wheels/fast_lane.py` - FastLane reference

  **Acceptance Criteria**:
  - [ ] File created: `wheels/dispatcher.py`
  - [ ] `Dispatcher.get_converter('.md')` returns PassthroughConverter
  - [ ] `Dispatcher.get_converter('.txt')` returns PassthroughConverter
  - [ ] `Dispatcher.get_converter('.docx')` raises error (FastLane not a converter)
  - [ ] `Dispatcher.get_converter('.unknown')` raises ValueError

  **QA Scenarios**:

  ```
  Scenario: .md extension routing
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(); c = d.get_converter(Path('test.md')); print(type(c).__name__)"
    Expected Result: "PassthroughConverter"
    Failure Indicators: Wrong converter type, exception raised
    Evidence: .sisyphus/evidence/task-5-md-routing.txt

  Scenario: .txt extension routing
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(); c = d.get_converter(Path('test.txt')); print(type(c).__name__)"
    Expected Result: "PassthroughConverter"
    Failure Indicators: Wrong converter type, exception raised
    Evidence: .sisyphus/evidence/task-5-txt-routing.txt

  Scenario: Unknown extension error
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(); d.get_converter(Path('test.xyz'))" 2>&1
    Expected Result: ValueError with "Unsupported format: .xyz"
    Failure Indicators: No exception, wrong exception type
    Evidence: .sisyphus/evidence/task-5-unknown-routing.txt
  ```

  **Evidence to Capture**:
  - [ ] task-5-md-routing.txt - .md routing proof
  - [ ] task-5-txt-routing.txt - .txt routing proof
  - [ ] task-5-unknown-routing.txt - Unknown extension error proof

  **Commit**: YES (grouped with T6, T7)
  - Message: `feat(mvp): add dispatcher, pipeline, and CLI`
  - Files: `wheels/dispatcher.py`

- [x] 6. **pipeline.py - Pipeline orchestration**

  **What to do**:
  - Create `pipeline.py` (root level, not in wheels/)
  - Implement `convert_file(input_path: Path) -> Path` function:
    - Check file exists, raise `FileNotFoundError` if not
    - Check file size (≤50MB), raise `ValueError` if exceeds
    - Get converter via `Dispatcher.get_converter()`
    - If PassthroughConverter: read content directly
    - If FastLane: call `FastLane.convert()`
    - Apply `Cleaner.clean()` to result
    - Write output to `{stem}.md` (same directory as input)
    - Handle naming conflicts: `{stem}_1.md`, `{stem}_2.md`, etc.
    - Return `Path` to output file
  - Implement `_get_unique_output_path(path: Path) -> Path` helper
  - 60-second timeout on FastLane conversion

  **Must NOT do**:
  - No batch processing (single file only)
  - No directory traversal

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Orchestration logic, straightforward
  - **Skills**: None required
  - **Justification**: Coordination code, no complex business logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7 (cli.py)
  - **Blocked By**: Tasks 3, 4, 5 (fast_lane, cleaner, dispatcher)

  **References**:
  - `wheels/dispatcher.py` - Dispatcher usage
  - `wheels/fast_lane.py` - FastLane usage
  - `wheels/cleaner.py` - Cleaner usage

  **Acceptance Criteria**:
  - [ ] File created: `pipeline.py`
  - [ ] `convert_file()` returns Path to output .md file
  - [ ] File size check rejects >50MB files
  - [ ] Naming conflict resolution works (increments suffix)
  - [ ] Cleaner applied to passthrough content
  - [ ] FastLane output is cleaned

  **QA Scenarios**:

  ```
  Scenario: Passthrough pipeline (existing .md file)
    Tool: Bash
    Preconditions: Create test.md with content
    Steps:
      1. Run: python -c "from pipeline import convert_file; result = convert_file(Path('test.md')); print(result)"
    Expected Result: Path to test.md (same file, passthrough)
    Failure Indicators: FileNotFoundError, wrong output path
    Evidence: .sisyphus/evidence/task-6-passthrough-pipeline.txt

  Scenario: Conversion pipeline (.docx via markitdown)
    Tool: Bash
    Preconditions: Create sample.docx
    Steps:
      1. Run: python -c "from pipeline import convert_file; result = convert_file(Path('sample.docx')); print(result)"
    Expected Result: Path to sample.md
    Failure Indicators: File not created, wrong extension
    Evidence: .sisyphus/evidence/task-6-conversion-pipeline.txt

  Scenario: File size check (>50MB)
    Tool: Bash
    Preconditions: Create fake 60MB file (truncate)
    Steps:
      1. Run: python -c "from pipeline import convert_file; convert_file(Path('huge.docx'))"
    Expected Result: ValueError with "exceeds 50MB"
    Failure Indicators: No exception, or wrong message
    Evidence: .sisyphus/evidence/task-6-filesize-check.txt

  Scenario: Naming conflict resolution
    Tool: Bash
    Preconditions: Create existing.md, run convert_file on another file that would become existing.md
    Steps:
      1. Run: python -c "from pipeline import convert_file; result = convert_file(Path('doc.docx')); print(result)"
    Expected Result: Path to existing_1.md (conflict resolved)
    Failure Indicators: Overwrote existing.md without conflict resolution
    Evidence: .sisyphus/evidence/task-6-naming-conflict.txt
  ```

  **Evidence to Capture**:
  - [ ] task-6-passthrough-pipeline.txt - Passthrough pipeline proof
  - [ ] task-6-conversion-pipeline.txt - Conversion pipeline proof
  - [ ] task-6-filesize-check.txt - File size check proof
  - [ ] task-6-naming-conflict.txt - Naming conflict resolution proof

  **Commit**: YES (grouped with T5)
  - Message: `feat(mvp): add dispatcher, pipeline, and CLI`
  - Files: `pipeline.py`

- [x] 7. **cli.py - Typer CLI entry point**

  **What to do**:
  - Create `cli.py` (root level)
  - Implement Typer app with:
    - `@app.command()` with `input_file: Path` argument
    - `@app.command()` with `--help` showing usage
    - Exit codes: 0=success, 1=error, 2=markitdown not found
    - Clear error messages to stderr
    - Call `convert_file()` and print output path on success
  - Error handling:
    - FileNotFoundError → "Error: File not found: {path}"
    - ValueError (file too large) → "Error: File exceeds 50MB limit"
    - ValueError (unsupported format) → "Error: Unsupported format: {suffix}"
    - Exception (markitdown failed) → "Error: Conversion failed: {details}"
  - No --verbose, --quiet, or other flags

  **Must NOT do**:
  - No batch file support
  - No directory input
  - No flags beyond help

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple CLI wrapping
  - **Skills**: None required
  - **Justification**: Straightforward Typer wrapper, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8 (integration test)
  - **Blocked By**: Task 6 (pipeline.py)

  **References**:
  - `pipeline.py` - `convert_file()` function to wrap
  - Typer documentation - Basic app structure

  **Acceptance Criteria**:
  - [ ] File created: `cli.py`
  - [ ] `python cli.py --help` shows usage text
  - [ ] `python cli.py input.docx` produces output.md and exit 0
  - [ ] `python cli.py nonexistent.docx` exits with code 1 and error
  - [ ] `python cli.py input.md` produces unchanged input.md (exit 0)

  **QA Scenarios**:

  ```
  Scenario: Help command
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py --help
    Expected Result: Usage text shown, exit 0
    Failure Indicators: Error, no usage text
    Evidence: .sisyphus/evidence/task-7-help.txt

  Scenario: Successful conversion
    Tool: Bash
    Preconditions: Create sample.docx
    Steps:
      1. Run: python cli.py sample.docx
    Expected Result: sample.md created, exit 0, path printed to stdout
    Failure Indicators: Exit non-zero, file not created
    Evidence: .sisyphus/evidence/task-7-conversion.txt

  Scenario: File not found error
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py nonexistent.docx 2>&1; echo "EXIT_CODE: $?"
    Expected Result: "Error: File not found: nonexistent.docx" to stderr, exit code 1
    Failure Indicators: Exit code 0, or no error message
    Evidence: .sisyphus/evidence/task-7-file-not-found.txt

  Scenario: Passthrough .md file
    Tool: Bash
    Preconditions: Create test.md with "# Test"
    Steps:
      1. Run: python cli.py test.md && cat test.md
    Expected Result: Content unchanged, exit 0
    Failure Indicators: File modified, exit non-zero
    Evidence: .sisyphus/evidence/task-7-passthrough.txt
  ```

  **Evidence to Capture**:
  - [ ] task-7-help.txt - Help text proof
  - [ ] task-7-conversion.txt - Conversion success proof
  - [ ] task-7-file-not-found.txt - File not found error proof
  - [ ] task-7-passthrough.txt - Passthrough proof

  **Commit**: YES (grouped with T5)
  - Message: `feat(mvp): add dispatcher, pipeline, and CLI`
  - Files: `cli.py`

- [x] 8. **Integration test - End-to-end verification**

  **What to do**:
  - Create test files: .docx, .md, .txt
  - Run full CLI commands and verify:
    - .docx → .md conversion works end-to-end
    - .md passthrough works
    - .txt passthrough works
    - File size check triggers on >50MB
    - Naming conflict creates incremented suffix
  - Capture evidence to `.sisyphus/evidence/integration/`

  **Must NOT do**:
  - No automated test framework (manual verification)
  - No pytest/unittest

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Integration verification
  - **Skills**: None required
  - **Justification**: Manual end-to-end verification, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification
  - **Blocked By**: Task 7 (cli.py)

  **References**:
  - All previous task QA scenarios
  - Use `python cli.py` for all tests

  **Acceptance Criteria**:
  - [ ] .docx converts to valid .md file
  - [ ] .md passthrough preserves content exactly
  - [ ] .txt passthrough works
  - [ ] File size >50MB shows error
  - [ ] Naming conflict resolution works

  **QA Scenarios**:

  ```
  Scenario: Full pipeline .docx conversion
    Tool: Bash
    Preconditions: Create real.docx (or sample.docx from prior test)
    Steps:
      1. Run: python cli.py real.docx
      2. Check: real.md exists and has content
    Expected Result: real.md created with markdown content
    Failure Indicators: File not created, empty content
    Evidence: .sisyphus/evidence/integration/docx-to-md.txt

  Scenario: Full pipeline .md passthrough
    Tool: Bash
    Preconditions: Create content.md with "## Title\n\nParagraph"
    Steps:
      1. Run: python cli.py content.md
      2. Check: content.md content is "## Title\n\nParagraph"
    Expected Result: Content unchanged (passthrough)
    Failure Indicators: Content modified
    Evidence: .sisyphus/evidence/integration/md-passthrough.txt

  Scenario: Naming conflict resolution
    Tool: Bash
    Preconditions: Create existing.md, run cli.py on file that would become existing.md
    Steps:
      1. Run: python cli.py another.docx (when another.md might conflict with existing.md)
      2. Check: Output is existing_1.md or similar
    Expected Result: Unique filename with increment
    Failure Indicators: Overwrote existing.md
    Evidence: .sisyphus/evidence/integration/naming-conflict.txt
  ```

  **Evidence to Capture**:
  - [ ] integration/docx-to-md.txt - Full conversion proof
  - [ ] integration/md-passthrough.txt - Passthrough proof
  - [ ] integration/txt-passthrough.txt - .txt passthrough proof
  - [ ] integration/naming-conflict.txt - Conflict resolution proof

  **Commit**: YES
  - Message: `feat(mvp): add integration verification`
  - Files: Integration evidence only (no new code)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — oracle
- [x] F2. **Code Quality Review** — unspecified-high
- [x] F3. **Real Manual QA** — unspecified-high
- [x] F4. **Scope Fidelity Check** — deep

---

## Commit Strategy

- **Wave 1 (base + converters)**:
  - `feat(mvp): add base converter interface and passthrough`
  - Files: `wheels/converters/base_converter.py`, `wheels/converters/converter_passthrough.py`
- **Wave 2 (orchestration)**:
  - `feat(mvp): add fast lane and cleaner`
  - Files: `wheels/fast_lane.py`, `wheels/cleaner.py`
- **Wave 3 (pipeline + cli)**:
  - `feat(mvp): add dispatcher, pipeline, and CLI`
  - Files: `wheels/dispatcher.py`, `pipeline.py`, `cli.py`

---

## Success Criteria

### Verification Commands
```bash
# Help works
python cli.py --help

# Passthrough works
echo "# Hello" > test.md && python cli.py test.md && type test.md  # Shows "# Hello"

# Conversion works
python cli.py sample.docx && type sample.md  # Shows markdown content

# Error handling works
python cli.py nonexistent.docx  # Exit 1, error message

# File size check works
python cli.py huge.docx  # Exit 1, "exceeds 50MB"
```

### Final Checklist
- [ ] All Must Have items implemented
- [ ] All Must NOT Have items absent
- [ ] End-to-end flow works for .docx → .md
- [ ] Passthrough works for .md/.txt
- [ ] Error messages are clear
- [ ] Exit codes are correct