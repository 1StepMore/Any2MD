# PDF Heavy Channel - QA Results

## Test Results Summary

| Test | Result | Notes |
|------|--------|-------|
| Light mode (markitdown) | PASS | supported_extensions = ['.pdf'] |
| Heavy mode (marker attempted) | PASS | RuntimeError with proper install hints when marker/docling not available |
| Both engines fail | PASS | RuntimeError mentions marker, docling, pip install, tesseract |
| No startup delay | PASS | Import and instantiation succeed without blocking imports |
| Regression (non-PDF) | PASS | FastLaneConverter/FastLane structure intact |

## Key Findings

1. **pdf_engine config**: Currently set to 'light' by default
2. **Light mode**: Uses markitdown subprocess - fails with clear install instructions
3. **Heavy mode**: Dynamically imports marker/docling - fails with clear install instructions for both
4. **Dispatcher**: Correctly routes .pdf to PdfConverter in both 'fast' and 'quality' modes
5. **FastLaneConverter**: Still includes .pdf in supported_extensions but Dispatcher overrides this for .pdf

## Code Structure Verified

- `PdfConverter._convert_light()`: Uses markitdown subprocess
- `PdfConverter._convert_heavy()`: Attempts marker first, then docling fallback
- `PdfConverter.convert()`: Raises FileNotFoundError for missing files, RuntimeError for conversion failures
- Dynamic import pattern confirmed - no blocking imports at module load time

## Edge Cases Confirmed

- Non-existent PDF: FileNotFoundError with path
- Existing PDF without heavy deps: RuntimeError with install instructions
- Existing PDF with light mode (default): RuntimeError with markitdown install instructions