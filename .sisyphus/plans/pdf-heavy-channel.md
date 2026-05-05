# Phase 3: PDF Heavy Channel - 动态导入机制

## TL;DR

> **Quick Summary**: Create `converter_pdf.py` with dynamic import mechanism for PDF conversion - light mode uses markitdown (zero deps), heavy mode attempts marker then falls back to docling.
>
> **Deliverables**:
> - `wheels/converters/converter_pdf.py` - New PDF converter with dynamic import
> - Updated `wheels/dispatcher.py` - Route .pdf to new converter based on config
>
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential (base → integration)
> **Critical Path**: Create converter → Update dispatcher → Integration test

---

## Context

### Original Request
Phase 3 implementation of PDF heavy channel with dynamic import mechanism. PDF conversion is the most complex part - marker and docling easily cause ImportError if hardcoded at file header, which would kill the entire program.

### Requirements (from user)
1. **light mode**: markitdown basic PDF parsing, zero external deps, no crash
2. **heavy mode**: marker succeeds → marker conversion (quality > light)
3. **heavy mode**: marker fails → correct fallback to docling
4. **both fail**: clear exception with install instructions
5. **startup speed**: no delay when marker not installed (dynamic import only when convert() called)

### Architecture Decision
**Who owns pdf_engine logic**: `converter_pdf.py` internal dynamic import (per architecture doc section 6.1)

**NOT** modifying `FastLaneConverter` - that handles .docx/.xlsx/.pptx/.html in fast mode. PDF gets its own dedicated converter.

**Route**: Dispatcher (mode + suffix) → converter_pdf.py (dynamic import based on pdf_engine config)

---

## Work Objectives

### Core Objective
Implement dynamic import mechanism for PDF conversion that gracefully handles missing optional dependencies (marker, docling) without crashing the program.

### Concrete Deliverables
- `wheels/converters/converter_pdf.py` - New PDF converter class
- `wheels/dispatcher.py` - Updated to route .pdf to new converter based on mode + config

### Definition of Done
- [ ] `python -c "from wheels.converters.converter_pdf import PdfConverter; c = PdfConverter(); print(c.supported_extensions)"` → `[".pdf"]`
- [ ] `pdf_engine=light` mode: markitdown used, no marker/docling imports attempted
- [ ] `pdf_engine=heavy` mode: marker attempted first, docling fallback on failure
- [ ] Both engines fail: clear RuntimeError with install instructions
- [ ] No startup delay when marker/docling not installed

### Must Have
- Dynamic import using `importlib.import_module` (NOT at module load time)
- `pdf_engine` config respected (light vs heavy)
- Proper exception handling with user-friendly error messages
- Graceful degradation when optional deps missing

### Must NOT Have
- Hardcoded `import marker` or `import docling` at file header
- Blocking imports during application startup
- Changes to non-PDF converter behavior (.docx/.xlsx/.pptx remain unchanged)
- Changes to FastLaneConverter

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: NO
- **Agent-Executed QA**: YES (mandatory - see QA scenarios below)

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

**Environment assumptions for QA**:
- Test machine has markitdown installed (checked via `which markitdown`)
- marker and docling may or may not be installed - test both states

---

## Execution Strategy

### Sequential Waves (NO parallelism - small task)

```
Wave 1 (Foundation - can start immediately):
└── Task 1: Create converter_pdf.py with dynamic import mechanism

Wave 2 (Integration - after Task 1):
└── Task 2: Update dispatcher.py to route .pdf to new converter

Wave FINAL (After ALL tasks):
└── Task F1: Integration QA - verify light/heavy modes work correctly
```

---

## TODOs

- [x] 1. Create converter_pdf.py with dynamic import mechanism

  **What to do**:
  - Create `wheels/converters/converter_pdf.py`
  - Class `PdfConverter(BaseConverter)` with `supported_extensions = [".pdf"]`
  - `convert(input_path)` method with logic:
    1. Read `pdf_engine` from config via `get_config().pdf_engine`
    2. If `light`: use markitdown (subprocess or import)
    3. If `heavy`: try `importlib.import_module("marker")` → if fail, try `importlib.import_module("docling")` → if fail, raise RuntimeError with install instructions
  - Dynamic import MUST happen inside `convert()`, not at class/module load time
  - Catch all Exceptions, log warning, and attempt fallback or raise clear error

  **Must NOT do**:
  - No `import marker` or `import docling` at top of file
  - No blocking startup imports
  - Don't modify FastLaneConverter

  **Recommended Agent Profile**:
  > - **Category**: `deep`
  >   Reason: Converter needs understanding of dynamic import, exception handling, config access, subprocess pattern
  > - **Skills**: `[]`
  >   No specific skills needed - standard Python patterns

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (single task)
  - **Blocks**: Task 2 (dispatcher update depends on converter existing)
  - **Blocked By**: None

  **References**:

  **Pattern References** (existing code to follow):
  - `wheels/converters/converter_pandoc.py:1-14` - Converter structure (import at top is OK for required deps, but we need dynamic import for optional)
  - `wheels/converters/converter_mammoth.py:9-13` - Try/except import pattern with RuntimeError
  - `wheels/fast_lane.py:11-41` - Markitdown subprocess execution pattern (subprocess.run with capture_output)

  **Config References** (how to access pdf_engine):
  - `wheels/config.py:41` - `pdf_engine: PdfEngine = "light"` field definition
  - `wheels/config.py:169-174` - `get_config()` function to read config

  **Test References** (testing patterns to follow):
  - `check_env.py:131-144` - How to check marker/docling availability via importlib

  **WHY Each Reference Matters**:
  - `converter_mammoth.py:9-13`: Shows the try/except import pattern we should emulate for dynamic imports
  - `fast_lane.py:11-41`: Shows how to execute markitdown subprocess - use this for light mode
  - `check_env.py:131-144`: Shows importlib.import_module pattern for checking optional deps
  - `config.py:get_config()`: How to access pdf_engine at runtime

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY**

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Light mode - markitdown used, no marker/docling import attempted
    Tool: Bash
    Preconditions: pdf_engine=light in config.yaml, markitdown available
    Steps:
      1. Set config.yaml pdf_engine=light
      2. Run: python -c "from wheels.converters.converter_pdf import PdfConverter; c = PdfConverter(); print(c.supported_extensions)"
    Expected Result: Output is [".pdf"]
    Evidence: .sisyphus/evidence/task-1-light-mode-basic.json

  Scenario: Light mode - PDF conversion works via markitdown
    Tool: Bash
    Preconditions: pdf_engine=light, markitdown available, test PDF file exists
    Steps:
      1. Create test PDF: echo "test" > /tmp/test.pdf (or use existing test file)
      2. Run: python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from wheels.converters.converter_pdf import PdfConverter
c = PdfConverter()
result = c.convert(Path('/tmp/test.pdf'))
print(result[:100] if result else 'empty')
"
    Expected Result: Output contains markdown text (not error)
    Failure Indicators: ImportError, AttributeError on pdf_engine
    Evidence: .sisyphus/evidence/task-1-light-convert.json

  Scenario: Heavy mode - marker attempted first
    Tool: Bash
    Preconditions: pdf_engine=heavy in config.yaml
    Steps:
      1. Set config.yaml pdf_engine=heavy
      2. Run: python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from wheels.converters.converter_pdf import PdfConverter
c = PdfConverter()
try:
    result = c.convert(Path('/tmp/test.pdf'))
    print('conversion succeeded')
except RuntimeError as e:
    print(f'RuntimeError: {e}')
except Exception as e:
    print(f'Exception type: {type(e).__name__}, msg: {e}')
" 2>&1
    Expected Result: Either conversion succeeds OR RuntimeError with marker/docling mention
    Failure Indicators: Unexpected AttributeError, KeyError on config access
    Evidence: .sisyphus/evidence/task-1-heavy-marker-attempt.json

  Scenario: Heavy mode - marker fails, docling fallback (simulated)
    Tool: Bash
    Preconditions: pdf_engine=heavy, marker installed but broken
    Steps:
      1. Temporarily break marker by setting PYTHONPATH to empty dir
      2. Run same conversion test
      3. Check if docling was attempted
    Expected Result: Error message mentions docling OR conversion succeeds via docling
    Failure Indicators: No fallback attempted, error doesn't mention docling
    Evidence: .sisyphus/evidence/task-1-heavy-docling-fallback.json

  Scenario: Both engines fail - clear error message
    Tool: Bash
    Preconditions: pdf_engine=heavy, neither marker nor docling installed
    Steps:
      1. Ensure marker and docling are not importable
      2. Run conversion test
      3. Capture error message
    Expected Result: RuntimeError with clear install instructions (pip install marker or pip install docling)
    Failure Indicators: Generic Python traceback instead of user-friendly message
    Evidence: .sisyphus/evidence/task-1-both-fail-error.json
  ```

  **Commit**: YES
  - Message: `feat(converter): add PdfConverter with dynamic import mechanism`
  - Files: `wheels/converters/converter_pdf.py`
  - Pre-commit: N/A (no tests)

---

- [x] 2. Update dispatcher.py to route .pdf to PdfConverter

  **What to do**:
  - In `wheels/dispatcher.py`:
    1. Add `from wheels.converters.converter_pdf import PdfConverter`
    2. Add `self._pdf_converter: Optional[PdfConverter] = None` to `__init__`
    3. Add `_get_pdf_converter()` method (lazy init pattern)
    4. Update `get_converter()`:
       - In `quality` mode: Route `.pdf` to `self._get_pdf_converter()` (NOT throw ValueError)
       - In `fast` mode: Route `.pdf` to `self._get_pdf_converter()` instead of `self._fastlane_converter`
  - Keep FastLaneConverter for .docx/.xlsx/.pptx (don't touch)

  **Must NOT do**:
  - Don't remove or modify FastLaneConverter (still used for other formats)
  - Don't change quality mode routing for other file types
  - Don't add pdf_engine check here - let converter_pdf.py handle it internally

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   Reason: Simple routing change following existing patterns
  > - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task F1 (integration QA)
  - **Blocked By**: Task 1 (converter must exist first)

  **References**:

  **Pattern References** (existing code to follow):
  - `wheels/dispatcher.py:66-79` - Lazy init pattern `_get_pandoc_converter()`
  - `wheels/dispatcher.py:81-105` - `get_converter()` routing logic
  - `wheels/dispatcher.py:84-97` - Quality mode routing (use as template for PDF routing)

  **WHY Each Reference Matters**:
  - `_get_pandoc_converter()`: Shows the exact lazy init pattern to follow
  - `get_converter()`: Shows how to route based on suffix and mode
  - Line 96-97: Shows current error throw for PDF in quality mode - replace with converter call

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY**

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Quality mode routes .pdf to PdfConverter (not error)
    Tool: Bash
    Preconditions: config.yaml has quality mode
    Steps:
      1. Run: python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from wheels.dispatcher import Dispatcher
d = Dispatcher(mode='quality')
c = d.get_converter(Path('test.pdf'))
print(f'Converter type: {type(c).__name__}')
print(f'Extensions: {c.supported_extensions}')
"
    Expected Result: Converter type is PdfConverter, extensions include .pdf
    Failure Indicators: ValueError about "PDF quality conversion planned"
    Evidence: .sisyphus/evidence/task-2-quality-pdf-route.json

  Scenario: Fast mode routes .pdf to PdfConverter (not FastLaneConverter)
    Tool: Bash
    Preconditions: config.yaml has fast mode
    Steps:
      1. Run: python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from wheels.dispatcher import Dispatcher
d = Dispatcher(mode='fast')
c = d.get_converter(Path('test.pdf'))
print(f'Converter type: {type(c).__name__}')
"
    Expected Result: Converter type is PdfConverter (NOT FastLaneConverter)
    Failure Indicators: FastLaneConverter returned instead
    Evidence: .sisyphus/evidence/task-2-fast-pdf-route.json

  Scenario: Other formats still route correctly (regression check)
    Tool: Bash
    Preconditions: config.yaml has fast mode
    Steps:
      1. Run: python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from wheels.dispatcher import Dispatcher
d = Dispatcher(mode='fast')
for ext in ['.docx', '.xlsx', '.pptx', '.html']:
    c = d.get_converter(Path(f'test{ext}'))
    print(f'{ext} -> {type(c).__name__}')
"
    Expected Result: .docx/.xlsx/.pptx/.html -> FastLaneConverter (unchanged behavior)
    Failure Indicators: Any other format returns different converter
    Evidence: .sisyphus/evidence/task-2-other-formats.json
  ```

  **Commit**: YES
  - Message: `feat(dispatcher): route .pdf to PdfConverter in both modes`
  - Files: `wheels/dispatcher.py`
  - Pre-commit: N/A (no tests)

---

## Final Verification Wave

> 1 review agent runs. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Integration QA** — `unspecified-high`
  Test the full pipeline:
  1. Light mode: PDF conversion works via markitdown
  2. Heavy mode: marker attempted first (if installed)
  3. Heavy fallback: docling used if marker fails
  4. Error case: Both fail shows clear install instructions
  5. No startup delay (dynamic import only when convert() called)
  6. Non-PDF files (docx/xlsx/pptx) still work via FastLaneConverter
  Output: `Light [PASS/FAIL] | Heavy [PASS/FAIL] | Fallback [PASS/FAIL] | Error [PASS/FAIL] | Startup [PASS/FAIL] | Regression [PASS/FAIL]`

---

## Commit Strategy

- **1**: `feat(converter): add PdfConverter with dynamic import mechanism` - converter_pdf.py
- **2**: `feat(dispatcher): route .pdf to PdfConverter in both modes` - dispatcher.py

---

## Success Criteria

### Verification Commands
```bash
# Basic import test
python -c "from wheels.converters.converter_pdf import PdfConverter; print(PdfConverter().supported_extensions)"
# Expected: [".pdf"]

# Dispatcher routing test
python -c "from wheels.dispatcher import Dispatcher; d=Dispatcher(mode='quality'); print(type(d.get_converter(__import__('pathlib').Path('test.pdf'))).__name__)"
# Expected: PdfConverter
```

### Final Checklist
- [ ] converter_pdf.py created with dynamic import
- [ ] dispatcher.py updated to route .pdf to PdfConverter
- [ ] light mode works (markitdown, no crash)
- [ ] heavy mode attempts marker (if installed)
- [ ] heavy mode falls back to docling (if marker fails)
- [ ] Both fail shows clear RuntimeError with install instructions
- [ ] No startup delay when marker/docling not installed
- [ ] Non-PDF files unchanged (FastLaneConverter still used for docx/xlsx/pptx/html)