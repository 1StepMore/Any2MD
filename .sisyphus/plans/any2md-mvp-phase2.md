# Any2MD MVP Phase 2 Implementation Plan

## TL;DR

> **Quick Summary**: Add quality channel converters (pypandoc, mammoth, markdownify) with --mode {quality|fast} dual-mode dispatch.
>
> **Deliverables**:
> - `wheels/converters/converter_pandoc.py` - pypandoc-binary for docx/pptx/xlsx
> - `wheels/converters/converter_mammoth.py` - mammoth for complex DOCX (fallback)
> - `wheels/converters/converter_html.py` - markdownify for HTML files
> - `wheels/dispatcher.py` - Mode-aware routing (quality vs fast)
> - `cli.py` - `--mode` flag (default: fast)
> - `pipeline.py` - Mode parameter propagation
>
> **Estimated Effort**: Medium (6-8 hours of Vibe Coding)
> **Parallel Execution**: YES - 2 waves (Wave 1: converters + dispatcher, Wave 2: CLI + pipeline + integration)
> **Critical Path**: base_converter (Phase1) → converter_pandoc → dispatcher (upgrade) → cli (upgrade) → integration

---

## Context

### Original Request
Phase 2 quality channel integration per user's specification:
- Add quality converters: pypandoc, mammoth, markdownify
- Dual-mode dispatch: --mode {quality|fast}
- Quality priority with markitdown fallback
- Passthrough for .md/.txt unchanged

### Routing Table (Confirmed)

| File Type | Quality Mode | Fast Mode |
|-----------|--------------|-----------|
| .docx | pypandoc → mammoth (fallback) | markitdown |
| .pptx / .xlsx | pypandoc | markitdown |
| .html / .htm | markdownify | markitdown |
| .pdf | Phase 3 error | markitdown |
| .epub / other | markitdown | markitdown |
| .md / .txt | passthrough | passthrough |

### Decisions Made
- **Q1**: Mammoth fallback (pypandoc first, mammoth for .docx on pypandoc failure)
- **Q2**: Clear error message on missing library (exit 1 + install instructions)
- **Q3**: Log mammoth.messages as warnings to stderr
- **Q4**: Clear error for .pdf quality (Phase 3 handles it)
- **Q5**: Default --mode fast (backward compatible)
- **Q6**: `--mode {quality|fast}` CLI flag

### Library API Findings
- `pypandoc.convert_file(input, 'gfm')` returns markdown string
- `mammoth.convert_to_html(file)` returns `result.value` (HTML) + `result.messages`
- `markdownify(html, heading_style=ATX)` returns markdown string

---

## Work Objectives

### Core Objective
Extend the MVP to support quality conversion with mode-aware dispatcher routing.

### Concrete Deliverables
- `wheels/converters/converter_pandoc.py` - PandocConverter class
- `wheels/converters/converter_mammoth.py` - MammothConverter class
- `wheels/converters/converter_html.py` - HtmlConverter class
- `wheels/dispatcher.py` - Mode-aware get_converter(file_path, mode)
- `cli.py` - --mode flag with quality/fast choices
- `pipeline.py` - mode parameter to dispatcher

### Definition of Done
- [ ] `any2md input.docx --mode quality` uses pypandoc (or mammoth fallback)
- [ ] `any2md input.docx --mode fast` uses markitdown (existing behavior)
- [ ] `any2md input.html --mode quality` uses markdownify
- [ ] `any2md input.pdf --mode quality` shows Phase 3 error
- [ ] `any2md input.md --mode quality` passthrough unchanged

### Must Have
- --mode flag in CLI (default: fast)
- Mode-aware dispatcher routing
- All three quality converters
- Clear error messages for missing libraries
- Clear error for .pdf quality mode
- mammoth.messages logged as warnings

### Must NOT Have (Guardrails)
- NO automatic library installation
- NO batch processing
- NO config file changes
- NO changes to existing converter interfaces
- NO changes to output file naming/conflict resolution
- NO quality mode for .pdf (Phase 3 only)
- NO retry logic
- NO per-converter mode overrides

---

## Verification Strategy

### Test Infrastructure
- **Infrastructure exists**: NO - creating from scratch
- **Automated tests**: None (Vibe Coding style)
- **Framework**: None (manual print-based verification)

### QA Policy (MANDATORY)
Every task includes agent-executed QA scenarios. Verification is manual through CLI invocation tests.

Evidence saved to `.sisyphus/evidence/phase2/`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Converters + Dispatcher - 4 tasks, can run in parallel):
├── Task 1: converter_pandoc.py (depends: base_converter)
├── Task 2: converter_mammoth.py (depends: base_converter)
├── Task 3: converter_html.py (depends: base_converter)
└── Task 4: dispatcher.py upgrade (depends: converters created)

Wave 2 (CLI + Pipeline + Integration - 3 tasks, depends on Wave 1):
├── Task 5: cli.py --mode flag (depends: dispatcher)
├── Task 6: pipeline.py mode parameter (depends: dispatcher)
└── Task 7: Integration test (depends: all)

Critical Path: T1,T2,T3 → T4 → T5,T6 → T7
Parallel Speedup: ~40% faster with Wave 1 parallelization
Max Concurrent: 4 (Wave 1), 3 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| T1 (converter_pandoc.py) | None (base_converter exists) | T4 |
| T2 (converter_mammoth.py) | None | T4 |
| T3 (converter_html.py) | None | T4 |
| T4 (dispatcher.py upgrade) | T1, T2, T3 | T5, T6 |
| T5 (cli.py --mode) | T4 | T7 |
| T6 (pipeline.py mode) | T4 | T7 |
| T7 (Integration test) | T5, T6 | Final verification |

---

## TODOs

### Wave 1 (Converters + Dispatcher - 4 tasks, parallel execution)

- [x] 1. **converter_pandoc.py - Pandoc quality converter**

  **What to do**:
  - Create `wheels/converters/converter_pandoc.py`
  - Implement `PandocConverter(BaseConverter)`:
    - `supported_extensions = ['.docx', '.pptx', '.xlsx']`
    - `convert(input_path: Path) -> str`: Use `pypandoc.convert_file(str(input_path), 'gfm')`
  - Handle exceptions: `RuntimeError` on failure, `OSError` if pandoc missing
  - If pandoc missing, raise `RuntimeError("pypandoc-binary not installed. Install: pip install pypandoc-binary")`

  **Must NOT do**:
  - No file I/O beyond reading input_path
  - No output file writing (return string only)
  - No markitdown imports

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Converter wrapper, straightforward
  - **Skills**: None required
  - **Justification**: Simple wrapper around pypandoc API, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T2, T3, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (dispatcher.py)
  - **Blocked By**: None

  **References**:
  - `wheels/converters/base_converter.py:1-41` - Interface to implement
  - `wheels/converters/converter_passthrough.py:1-33` - Example implementation pattern

  **Acceptance Criteria**:
  - [ ] File created: `wheels/converters/converter_pandoc.py`
  - [ ] `PandocConverter` inherits from `BaseConverter`
  - [ ] `supported_extensions` returns `['.docx', '.pptx', '.xlsx']`
  - [ ] `convert('sample.docx')` returns markdown string
  - [ ] Raises `RuntimeError` on conversion failure
  - [ ] Raises `RuntimeError` with install message if pypandoc not available

  **QA Scenarios**:

  ```
  Scenario: Import verification
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_pandoc import PandocConverter; print('OK')"
    Expected Result: Output "OK" with exit code 0
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/phase2/task-1-import.txt

  Scenario: Abstract class enforcement
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_pandoc import PandocConverter; c = PandocConverter()"
    Expected Result: Works (no abstract methods to fail)
    Failure Indicators: TypeError (should not happen - no abstract methods)
    Evidence: .sisyphus/evidence/phase2/task-1-instantiate.txt

  Scenario: Supported extensions check
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_pandoc import PandocConverter; print(PandocConverter().supported_extensions)"
    Expected Result: ['.docx', '.pptx', '.xlsx']
    Failure Indicators: Wrong extensions, no extensions
    Evidence: .sisyphus/evidence/phase2/task-1-extensions.txt

  Scenario: pypandoc missing error
    Tool: Bash
    Preconditions: None (pypandoc likely not installed)
    Steps:
      1. Run: python -c "from wheels.converters.converter_pandoc import PandocConverter; from pathlib import Path; PandocConverter().convert(Path('test.docx'))" 2>&1
    Expected Result: RuntimeError with install instructions
    Failure Indicators: No error, or wrong error type
    Evidence: .sisyphus/evidence/phase2/task-1-missing-lib.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-import.txt - Import success proof
  - [ ] task-1-instantiate.txt - Instantiation proof
  - [ ] task-1-extensions.txt - Extensions check
  - [ ] task-1-missing-lib.txt - Missing lib error proof

  **Commit**: YES (grouped with T2, T3)
  - Message: `feat(phase2): add quality converters (pandoc, mammoth, html)`
  - Files: `wheels/converters/converter_pandoc.py`, `wheels/converters/converter_mammoth.py`, `wheels/converters/converter_html.py`

- [x] 2. **converter_mammoth.py - Mammoth DOCX converter**

  **What to do**:
  - Create `wheels/converters/converter_mammoth.py`
  - Implement `MammothConverter(BaseConverter)`:
    - `supported_extensions = ['.docx']`
    - `convert(input_path: Path) -> str`:
      1. Open file as binary: `with open(input_path, 'rb') as f:`
      2. Call `mammoth.convert_to_html(f)` → returns `result`
      3. If `result.messages` not empty, log each at WARNING level to stderr
      4. Use `markdownify(result.value, heading_style=ATX)` to convert HTML to markdown
      5. Return markdown string
  - Handle exceptions: `RuntimeError` on failure
  - If mammoth missing, raise `RuntimeError("mammoth not installed. Install: pip install mammoth")`

  **Must NOT do**:
  - No `mammoth.convert_to_markdown()` (deprecated)
  - No ignoring result.messages (must log as warnings)
  - No HTML parsing with BeautifulSoup

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Converter wrapper, straightforward
  - **Skills**: None required
  - **Justification**: Chain of existing libraries, no custom logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T3, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (dispatcher.py)
  - **Blocked By**: None

  **References**:
  - `wheels/converters/base_converter.py:1-41` - Interface to implement
  - `wheels/converters/converter_passthrough.py:1-33` - Example pattern
  - Library research: mammoth.convert_to_html() returns result.value + result.messages
  - Library research: markdownify(html, heading_style=ATX) for final conversion

  **Acceptance Criteria**:
  - [ ] File created: `wheels/converters/converter_mammoth.py`
  - [ ] `MammothConverter` inherits from `BaseConverter`
  - [ ] `supported_extensions` returns `['.docx']`
  - [ ] Uses HTML intermediate + markdownify (not convert_to_markdown)
  - [ ] `result.messages` logged to stderr at WARNING level
  - [ ] Raises `RuntimeError` on conversion failure

  **QA Scenarios**:

  ```
  Scenario: Import verification
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_mammoth import MammothConverter; print('OK')"
    Expected Result: Output "OK" with exit code 0
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/phase2/task-2-import.txt

  Scenario: Supported extensions check
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_mammoth import MammothConverter; print(MammothConverter().supported_extensions)"
    Expected Result: ['.docx']
    Failure Indicators: Wrong extensions
    Evidence: .sisyphus/evidence/phase2/task-2-extensions.txt

  Scenario: mammoth missing error
    Tool: Bash
    Preconditions: mammoth likely not installed
    Steps:
      1. Run: python -c "from wheels.converters.converter_mammoth import MammothConverter; from pathlib import Path; MammothConverter().convert(Path('test.docx'))" 2>&1
    Expected Result: RuntimeError with install instructions
    Failure Indicators: No error, or wrong error type
    Evidence: .sisyphus/evidence/phase2/task-2-missing-lib.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-import.txt - Import success proof
  - [ ] task-2-extensions.txt - Extensions check
  - [ ] task-2-missing-lib.txt - Missing lib error proof

  **Commit**: YES (grouped with T1, T3)
  - Message: `feat(phase2): add quality converters (pandoc, mammoth, html)`
  - Files: `wheels/converters/converter_pandoc.py`, `wheels/converters/converter_mammoth.py`, `wheels/converters/converter_html.py`

- [x] 3. **converter_html.py - Markdownify HTML converter**

  **What to do**:
  - Create `wheels/converters/converter_html.py`
  - Implement `HtmlConverter(BaseConverter)`:
    - `supported_extensions = ['.html', '.htm']`
    - `convert(input_path: Path) -> str`:
      1. Read HTML file: `html_content = input_path.read_text(encoding='utf-8')`
      2. Call `markdownify(html_content, heading_style=ATX)`
      3. Return markdown string
  - Handle exceptions: `RuntimeError` on failure
  - If markdownify missing, raise `RuntimeError("markdownify not installed. Install: pip install markdownify")`

  **Must NOT do**:
  - No HTML parsing with BeautifulSoup or lxml
  - No HTML manipulation or cleaning (just pass through markdownify)
  - No external CSS/JS processing

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple wrapper, straightforward
  - **Skills**: None required
  - **Justification**: Simple chain of read + markdownify call

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T2, T4)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (dispatcher.py)
  - **Blocked By**: None

  **References**:
  - `wheels/converters/base_converter.py:1-41` - Interface to implement
  - Library research: markdownify(html, heading_style=ATX)

  **Acceptance Criteria**:
  - [ ] File created: `wheels/converters/converter_html.py`
  - [ ] `HtmlConverter` inherits from `BaseConverter`
  - [ ] `supported_extensions` returns `['.html', '.htm']`
  - [ ] Uses markdownify with ATX heading style
  - [ ] Raises `RuntimeError` on conversion failure

  **QA Scenarios**:

  ```
  Scenario: Import verification
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_html import HtmlConverter; print('OK')"
    Expected Result: Output "OK" with exit code 0
    Failure Indicators: ImportError
    Evidence: .sisyphus/evidence/phase2/task-3-import.txt

  Scenario: Supported extensions check
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.converters.converter_html import HtmlConverter; print(HtmlConverter().supported_extensions)"
    Expected Result: ['.html', '.htm']
    Failure Indicators: Wrong extensions
    Evidence: .sisyphus/evidence/phase2/task-3-extensions.txt

  Scenario: markdownify missing error
    Tool: Bash
    Preconditions: markdownify likely not installed
    Steps:
      1. Run: python -c "from wheels.converters.converter_html import HtmlConverter; from pathlib import Path; HtmlConverter().convert(Path('test.html'))" 2>&1
    Expected Result: RuntimeError with install instructions
    Failure Indicators: No error, or wrong error type
    Evidence: .sisyphus/evidence/phase2/task-3-missing-lib.txt
  ```

  **Evidence to Capture**:
  - [ ] task-3-import.txt - Import success proof
  - [ ] task-3-extensions.txt - Extensions check
  - [ ] task-3-missing-lib.txt - Missing lib error proof

  **Commit**: YES (grouped with T1, T2)
  - Message: `feat(phase2): add quality converters (pandoc, mammoth, html)`
  - Files: `wheels/converters/converter_pandoc.py`, `wheels/converters/converter_mammoth.py`, `wheels/converters/converter_html.py`

- [x] 4. **dispatcher.py - Mode-aware routing upgrade**

  **What to do**:
  - Update `wheels/dispatcher.py`:
    1. Import new converters: `from wheels.converters.converter_pandoc import PandocConverter`
    2. Import new converters: `from wheels.converters.converter_mammoth import MammothConverter`
    3. Import new converters: `from wheels.converters.converter_html import HtmlConverter`
    4. Add `__init__(self, mode: str = 'fast')` parameter
    5. Store mode: `self._mode = mode`
    6. Add quality converter instances in `__init__`:
       - `self._pandoc_converter = PandocConverter()`
       - `self._mammoth_converter = MammothConverter()`
       - `self._html_converter = HtmlConverter()`
    7. Update `get_converter(self, file_path: Path) -> BaseConverter`:
       - Get suffix: `suffix = file_path.suffix.lower()`
       - **If mode == 'quality'**:
         - `.docx` → try `PandocConverter`, on RuntimeError fallback to `MammothConverter`
         - `.pptx`, `.xlsx` → `PandocConverter`
         - `.html`, `.htm` → `HtmlConverter`
         - `.pdf` → raise `ValueError("PDF quality conversion planned for Phase 3")`
         - `.md`, `.txt` → `PassthroughConverter`
         - Unknown → raise `ValueError(f"Unsupported format: {suffix}")`
       - **If mode == 'fast'**:
         - `.docx`, `.xlsx`, `.pptx`, `.pdf` → `FastLaneConverter`
         - `.html`, `.htm` → `FastLaneConverter` (use markitdown even for HTML in fast mode)
         - `.md`, `.txt` → `PassthroughConverter`
         - Unknown → raise `ValueError(f"Unsupported format: {suffix}")`
    8. Keep lazy loading pattern (create instances once in `__init__`, reuse)
    9. Handle case-insensitive extension matching

  **Must NOT do**:
  - No creating converter instances on every `get_converter()` call (must reuse)
  - No changing PassthroughConverter behavior
  - No changing FastLaneConverter behavior for fast mode
  - No per-file mode override

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Routing logic, straightforward conditional
  - **Skills**: None required
  - **Justification**: Conditional routing based on mode and suffix, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T1, T2, T3 - they create converters, dispatcher imports them)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 5, 6 (cli.py, pipeline.py)
  - **Blocked By**: Tasks 1, 2, 3 (converters must exist first)

  **References**:
  - `wheels/dispatcher.py:1-79` - Current dispatcher to update
  - `wheels/converters/converter_pandoc.py` - New converter to import
  - `wheels/converters/converter_mammoth.py` - New converter to import
  - `wheels/converters/converter_html.py` - New converter to import

  **Acceptance Criteria**:
  - [ ] `Dispatcher(mode='quality')` routes .docx to PandocConverter
  - [ ] `Dispatcher(mode='quality')` routes .pptx/.xlsx to PandocConverter
  - [ ] `Dispatcher(mode='quality')` routes .html/.htm to HtmlConverter
  - [ ] `Dispatcher(mode='quality')` routes .docx fallback to MammothConverter on pypandoc failure
  - [ ] `Dispatcher(mode='quality')` raises ValueError for .pdf with Phase 3 message
  - [ ] `Dispatcher(mode='fast')` routes all to FastLaneConverter (existing behavior)
  - [ ] `Dispatcher(mode='fast')` routes .md/.txt to PassthroughConverter
  - [ ] Mode-aware routing works for all file types in routing table

  **QA Scenarios**:

  ```
  Scenario: Quality mode .docx routing to PandocConverter
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(mode='quality'); c = d.get_converter(__import__('pathlib').Path('test.docx')); print(type(c).__name__)"
    Expected Result: "PandocConverter"
    Failure Indicators: Wrong converter, wrong type
    Evidence: .sisyphus/evidence/phase2/task-4-quality-docx.txt

  Scenario: Fast mode .docx routing to FastLaneConverter
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(mode='fast'); c = d.get_converter(__import__('pathlib').Path('test.docx')); print(type(c).__name__)"
    Expected Result: "FastLaneConverter"
    Failure Indicators: Wrong converter
    Evidence: .sisyphus/evidence/phase2/task-4-fast-docx.txt

  Scenario: Quality mode .html routing to HtmlConverter
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(mode='quality'); c = d.get_converter(__import__('pathlib').Path('test.html')); print(type(c).__name__)"
    Expected Result: "HtmlConverter"
    Failure Indicators: Wrong converter
    Evidence: .sisyphus/evidence/phase2/task-4-quality-html.txt

  Scenario: Quality mode .pdf raises ValueError with Phase 3 message
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(mode='quality'); d.get_converter(__import__('pathlib').Path('test.pdf'))" 2>&1
    Expected Result: ValueError with "Phase 3" in message
    Failure Indicators: No error, or wrong error type/message
    Evidence: .sisyphus/evidence/phase2/task-4-quality-pdf.txt

  Scenario: .md routing unchanged in both modes
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; dq = Dispatcher(mode='quality'); df = Dispatcher(mode='fast'); cq = dq.get_converter(__import__('pathlib').Path('test.md')); cf = df.get_converter(__import__('pathlib').Path('test.md')); print(type(cq).__name__, type(cf).__name__)"
    Expected Result: "PassthroughConverter PassthroughConverter" (both same)
    Failure Indicators: Different converters
    Evidence: .sisyphus/evidence/phase2/task-4-md-passthrough.txt

  Scenario: Case-insensitive extension matching
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python -c "from wheels.dispatcher import Dispatcher; d = Dispatcher(mode='quality'); c = d.get_converter(__import__('pathlib').Path('test.DOCX')); print(type(c).__name__)"
    Expected Result: "PandocConverter" (.DOCX routes same as .docx)
    Failure Indicators: ValueError "Unsupported format: .DOCX"
    Evidence: .sisyphus/evidence/phase2/task-4-case-insensitive.txt
  ```

  **Evidence to Capture**:
  - [ ] task-4-quality-docx.txt - Quality .docx routing
  - [ ] task-4-fast-docx.txt - Fast .docx routing
  - [ ] task-4-quality-html.txt - Quality .html routing
  - [ ] task-4-quality-pdf.txt - PDF Phase 3 error
  - [ ] task-4-md-passthrough.txt - .md unchanged
  - [ ] task-4-case-insensitive.txt - Case insensitive

  **Commit**: YES (grouped with T1, T2, T3)
  - Message: `feat(phase2): add quality converters (pandoc, mammoth, html)`
  - Files: `wheels/converters/converter_pandoc.py`, `wheels/converters/converter_mammoth.py`, `wheels/converters/converter_html.py`, `wheels/dispatcher.py`

---

### Wave 2 (CLI + Pipeline + Integration - 3 tasks, sequential per group)

- [x] 5. **cli.py - --mode flag upgrade**

  **What to do**:
  - Update `cli.py`:
    1. Add `--mode` parameter to `main()`:
       ```python
       @app.command()
       def main(input_file: Path, mode: str = "fast"):
       ```
    2. Add validation: if mode not in ('quality', 'fast'), raise `typer.BadParameter`
    3. Remove redundant markitdown check (lines 23-31) - let dispatcher handle it
    4. Pass mode to `convert_file()`: `convert_file(input_file, mode=mode)`
    5. Keep error handling: FileNotFoundError → exit 1, ValueError → exit 1, RuntimeError → exit 1
    6. For markitdown-missing error in fast mode (exit code 2), keep same behavior

  **Must NOT do**:
  - No adding --verbose, --output-dir, or other flags (Phase 1 exclusions)
  - No --quality or --fast separate flags (use --mode {quality|fast})
  - No removing existing error handling

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple flag addition
  - **Skills**: None required
  - **Justification**: Adding one parameter to existing function

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7 (integration)
  - **Blocked By**: Task 4 (dispatcher.py)

  **References**:
  - `cli.py:1-55` - Current CLI to update
  - `pipeline.py:1-66` - Function signature to match

  **Acceptance Criteria**:
  - [ ] `python cli.py --help` shows --mode option with default "fast"
  - [ ] `python cli.py sample.docx --mode quality` passes mode='quality' to pipeline
  - [ ] `python cli.py sample.docx --mode fast` passes mode='fast' to pipeline
  - [ ] `python cli.py sample.docx` (no mode) uses default 'fast'
  - [ ] Invalid mode value shows error and exits with code 1

  **QA Scenarios**:

  ```
  Scenario: Help shows --mode option
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py --help
    Expected Result: Help text includes "--mode [QUALITY|FAST]" with default "fast"
    Failure Indicators: --mode not in help, wrong default
    Evidence: .sisyphus/evidence/phase2/task-5-help.txt

  Scenario: Invalid mode raises error
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py sample.docx --mode invalid 2>&1
    Expected Result: BadParameter error with valid options shown
    Failure Indicators: No error, wrong error type
    Evidence: .sisyphus/evidence/phase2/task-5-invalid-mode.txt

  Scenario: Quality mode passed to pipeline
    Tool: Bash
    Preconditions: sample.docx exists, mock pipeline to capture mode
    Steps:
      1. Create test script that imports cli and calls main with mode='quality'
      2. Check that convert_file was called with mode='quality'
    Expected Result: convert_file receives mode='quality'
    Failure Indicators: mode not passed, or wrong value
    Evidence: .sisyphus/evidence/phase2/task-5-mode-passed.txt
  ```

  **Evidence to Capture**:
  - [ ] task-5-help.txt - Help output with --mode
  - [ ] task-5-invalid-mode.txt - Invalid mode error
  - [ ] task-5-mode-passed.txt - Mode passed to pipeline

  **Commit**: YES (grouped with T6)
  - Message: `feat(phase2): add --mode flag and mode-aware dispatch`
  - Files: `cli.py`, `pipeline.py`

- [x] 6. **pipeline.py - Mode parameter propagation**

  **What to do**:
  - Update `pipeline.py`:
    1. Update `convert_file()` signature: `def convert_file(input_path: Path, mode: str = "fast") -> Path:`
    2. Pass mode to Dispatcher: `dispatcher = Dispatcher(mode=mode)`
    3. All other logic unchanged (file check, size check, cleaner, output path)
    4. Keep `_get_unique_output_path()` helper (no mode needed)

  **Must NOT do**:
  - No changing output path logic (already working)
  - No changing Cleaner calls
  - No adding retry logic

  **Recommended Agent Profile**:
  - **Category**: `quick` - Simple parameter addition
  - **Skills**: None required
  - **Justification**: Adding parameter and passing through, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7 (integration)
  - **Blocked By**: Task 4 (dispatcher.py)

  **References**:
  - `pipeline.py:1-66` - Current pipeline to update
  - `wheels/dispatcher.py` - Dispatcher signature update

  **Acceptance Criteria**:
  - [ ] `convert_file(Path('sample.docx'), mode='quality')` passes mode to Dispatcher
  - [ ] `convert_file(Path('sample.docx'))` uses default mode='fast'
  - [ ] All existing behavior (file check, size check, output naming) unchanged

  **QA Scenarios**:

  ```
  Scenario: Mode parameter passed to Dispatcher
    Tool: Bash
    Preconditions: sample.docx exists
    Steps:
      1. Run: python -c "from pipeline import convert_file; from pathlib import Path; convert_file(Path('sample.docx'), mode='quality')"
    Expected Result: Conversion succeeds (or fails with lib not installed, but mode is passed)
    Failure Indicators: TypeError (mode parameter not accepted)
    Evidence: .sisyphus/evidence/phase2/task-6-mode-param.txt

  Scenario: Default mode is 'fast'
    Tool: Bash
    Preconditions: None (no file needed - just check signature)
    Steps:
      1. Run: python -c "from pipeline import convert_file; import inspect; print(inspect.signature(convert_file))"
    Expected Result: Contains "mode='fast'"
    Failure Indicators: Wrong default, or no default
    Evidence: .sisyphus/evidence/phase2/task-6-default-mode.txt

  Scenario: Passthrough still works with mode
    Tool: Bash
    Preconditions: Create test.md with "# Hello"
    Steps:
      1. Run: python -c "from pipeline import convert_file; from pathlib import Path; r = convert_file(Path('test.md'), mode='quality'); print(r)"
    Expected Result: Path to test.md (or test_1.md if conflict)
    Failure Indicators: FileNotFoundError, wrong behavior
    Evidence: .sisyphus/evidence/phase2/task-6-passthrough-mode.txt
  ```

  **Evidence to Capture**:
  - [ ] task-6-mode-param.txt - Mode parameter accepted
  - [ ] task-6-default-mode.txt - Default is 'fast'
  - [ ] task-6-passthrough-mode.txt - Passthrough with mode

  **Commit**: YES (grouped with T5)
  - Message: `feat(phase2): add --mode flag and mode-aware dispatch`
  - Files: `cli.py`, `pipeline.py`

- [x] 7. **Integration test - End-to-end verification**

  **What to do**:
  - Run full CLI commands to verify:
    1. Quality mode with .docx (if pypandoc available) or check import
    2. Fast mode with .docx (markitdown)
    3. Quality mode with .html (if markdownify available) or check import
    4. Quality mode .pdf error (Phase 3 message)
    5. .md passthrough in both modes
    6. .txt passthrough in both modes
    7. File not found error (unchanged)
    8. Unsupported format error (unchanged)
  - Capture evidence to `.sisyphus/evidence/phase2/integration/`

  **Must NOT do**:
  - No pytest/unittest (Vibe Coding style - manual verification)
  - No automated test framework

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low` - Manual end-to-end verification
  - **Skills**: None required
  - **Justification**: Running CLI commands, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Final verification
  - **Blocked By**: Tasks 5, 6 (cli.py, pipeline.py)

  **References**:
  - All previous task QA scenarios
  - Use `python cli.py` for all tests

  **Acceptance Criteria**:
  - [ ] `--mode quality` with .docx uses quality converter (pypandoc or mammoth)
  - [ ] `--mode fast` with .docx uses markitdown (existing behavior)
  - [ ] `--mode quality` with .html uses markdownify
  - [ ] `--mode quality` with .pdf shows Phase 3 error
  - [ ] `--mode quality` with .md passthrough unchanged
  - [ ] `--mode fast` with .md passthrough unchanged

  **QA Scenarios**:

  ```
  Scenario: Quality mode .docx conversion attempt
    Tool: Bash
    Preconditions: None (pypandoc likely not installed)
    Steps:
      1. Run: python cli.py sample.docx --mode quality 2>&1
    Expected Result: Either success with markdown, OR RuntimeError about pypandoc-binary not installed
    Failure Indicators: No error shown but mode ignored
    Evidence: .sisyphus/evidence/phase2/integration/quality-docx.txt

  Scenario: Fast mode .docx (regression test)
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py sample.docx --mode fast 2>&1
    Expected Result: Either success (markitdown), OR exit 2 with markitdown missing error
    Failure Indicators: Different behavior than before
    Evidence: .sisyphus/evidence/phase2/integration/fast-docx.txt

  Scenario: Quality mode .html
    Tool: Bash
    Preconditions: sample.html with <h1>Test</h1><p>Content</p>
    Steps:
      1. Run: python cli.py sample.html --mode quality 2>&1
    Expected Result: Either success, OR RuntimeError about markdownify not installed
    Failure Indicators: No error shown but mode ignored
    Evidence: .sisyphus/evidence/phase2/integration/quality-html.txt

  Scenario: Quality mode .pdf error
    Tool: Bash
    Preconditions: sample.pdf exists
    Steps:
      1. Run: python cli.py sample.pdf --mode quality 2>&1
    Expected Result: Exit 1 with ValueError containing "Phase 3"
    Failure Indicators: No error, wrong error, exit 0
    Evidence: .sisyphus/evidence/phase2/integration/quality-pdf-error.txt

  Scenario: .md passthrough in quality mode
    Tool: Bash
    Preconditions: sample.md with "# Test Header"
    Steps:
      1. Run: python cli.py sample.md --mode quality 2>&1 && cat sample.md
    Expected Result: Exit 0, content unchanged "# Test Header"
    Failure Indicators: Content modified, exit non-zero
    Evidence: .sisyphus/evidence/phase2/integration/md-quality.txt

  Scenario: .md passthrough in fast mode
    Tool: Bash
    Preconditions: sample.md with "# Test Header"
    Steps:
      1. Run: python cli.py sample.md --mode fast 2>&1 && cat sample.md
    Expected Result: Exit 0, content unchanged "# Test Header"
    Failure Indicators: Content modified, exit non-zero
    Evidence: .sisyphus/evidence/phase2/integration/md-fast.txt

  Scenario: Unsupported format error (unchanged)
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py sample.xyz --mode quality 2>&1
    Expected Result: Exit 1 with ValueError "Unsupported format: .xyz"
    Failure Indicators: Wrong error type, wrong message
    Evidence: .sisyphus/evidence/phase2/integration/unsupported-format.txt

  Scenario: File not found error (unchanged)
    Tool: Bash
    Preconditions: None
    Steps:
      1. Run: python cli.py nonexistent.docx --mode quality 2>&1
    Expected Result: Exit 1 with "File not found: nonexistent.docx"
    Failure Indicators: Wrong error message
    Evidence: .sisyphus/evidence/phase2/integration/file-not-found.txt
  ```

  **Evidence to Capture**:
  - [ ] integration/quality-docx.txt - Quality .docx
  - [ ] integration/fast-docx.txt - Fast .docx
  - [ ] integration/quality-html.txt - Quality .html
  - [ ] integration/quality-pdf-error.txt - PDF Phase 3 error
  - [ ] integration/md-quality.txt - .md in quality mode
  - [ ] integration/md-fast.txt - .md in fast mode
  - [ ] integration/unsupported-format.txt - Unsupported format
  - [ ] integration/file-not-found.txt - File not found

  **Commit**: YES
  - Message: `feat(phase2): add integration verification`
  - Files: Integration evidence only (no new code)

---

## Final Verification Wave

- [x] F1. **Plan Compliance Audit** — oracle
  Read plan end-to-end. For each Must Have: verify implementation exists. For each Must NOT Have: search for forbidden patterns. Check evidence files exist.

- [x] F2. **Code Quality Review** — unspecified-high
  Run `python -m py_compile` on all modified files. Check for: `as any`/`@ts-ignore` (not applicable), empty catches, console.log (not applicable), commented-out code, unused imports.

- [x] F3. **Real Manual QA** — unspecified-high
  Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration.

- [x] F4. **Scope Fidelity Check** — deep
  For each task: read "What to do", read actual diff. Verify 1:1 — no missing, no creep. Check "Must NOT do" compliance.

---

## Commit Strategy

- **Wave 1**: `feat(phase2): add quality converters (pandoc, mammoth, html)`
  - Files: `wheels/converters/converter_pandoc.py`, `wheels/converters/converter_mammoth.py`, `wheels/converters/converter_html.py`, `wheels/dispatcher.py`
- **Wave 2**: `feat(phase2): add --mode flag and mode-aware dispatch`
  - Files: `cli.py`, `pipeline.py`
- **Final**: `feat(phase2): add integration verification`

---

## Success Criteria

### Verification Commands
```bash
# Help shows --mode option
python cli.py --help

# Fast mode (default) works
python cli.py sample.docx

# Quality mode works
python cli.py sample.docx --mode quality

# .md passthrough in both modes
python cli.py sample.md --mode quality
python cli.py sample.md --mode fast
```

### Final Checklist
- [ ] All Must Have items implemented
- [ ] All Must NOT Have items absent
- [ ] --mode flag works for quality and fast
- [ ] Quality converters (pypandoc, mammoth, markdownify) implemented
- [ ] Mode-aware dispatcher routing working
- [ ] Clear errors for missing libraries
- [ ] Clear error for .pdf quality mode (Phase 3)
- [ ] .md/.txt passthrough unchanged in both modes