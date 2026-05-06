# BAT Edge Case Test Plan

## Test Location
```
D:\贯维\Any2MD\bat\test_batch_edge_cases\
```

## Current Config Settings
```yaml
concurrency: 4        # Max 4 files processed in parallel
max_file_size: 50MB   # Files >50MB skipped
retry_count: 3         # Transient failures retry 3 times
```

---

## Test Case Matrix

| # | File | Size | Purpose | Expected Result |
|---|------|------|---------|-----------------|
| 01 | `01_pdf_quality.pdf` | 7.4 MB | PDF quality mode | ✅ Success - MarkItDown |
| 02 | `02_docx_quality.docx` | 1.6 MB | DOCX quality mode | ✅ Success - Pandoc/Mammoth |
| 03 | `03_html_quality.html` | 145 B | HTML quality mode | ✅ Success - markdownify |
| 04 | `04_txt_passthrough.txt` | 19 B | TXT passthrough | ✅ Success - no conversion |
| 05 | `05_unsupported.xyz` | 20 B | Unsupported format | ❌ Error logged, skipped |
| 06 | `06_duplicate_a.txt` | 17 B | Filename conflict test | ✅ Success |
| 07 | `06_duplicate_b.txt` | 17 B | Duplicate name base | ✅ Success |
| 08 | `07_empty.txt` | 11 B | Empty content | ✅ Success |
| 09 | `08_really_empty.txt` | 1 B | Empty file | ✅ Success |
| 10 | `09_markdown.md` | 16 B | MD passthrough | ✅ Success - no conversion |
| 11 | `.hidden_skip.txt` | 7 B | Hidden file (starts with .) | ✅ Skipped - not converted |
| 12 | `subfolder/10_nested.txt` | 19 B | Recursive subfolder | ✅ Success - recursive |

---

## Expected Log Output

```
Found 11 files, converting with concurrency=4...
[01_pdf_quality.pdf] started
[02_docx_quality.docx] started
[03_html_quality.html] started
[04_txt_passthrough.txt] started
[01_pdf_quality.pdf] completed -> 01_pdf_quality.md
[05_unsupported.xyz] ERROR: Unsupported format: .xyz
[02_docx_quality.docx] completed -> 02_docx_quality.md
[06_duplicate_a.txt] completed -> 06_duplicate_a.md
[03_html_quality.html] completed -> 03_html_quality.md
[06_duplicate_b.txt] completed -> 06_duplicate_b.md
[04_txt_passthrough.txt] completed -> 04_txt_passthrough.md
[07_empty.txt] completed -> 07_empty.md
[08_really_empty.txt] completed -> 08_really_empty.md
[09_markdown.md] completed -> 09_markdown.md
[.hidden_skip.txt] SKIPPED (hidden file)
[subfolder/10_nested.txt] completed -> subfolder/10_nested.md

Batch completed: 10 succeeded, 1 failed
```

---

## Edge Cases Covered

### 1. Mixed Format Routing (PDF, DOCX, HTML, TXT, MD)
Tests that dispatcher correctly routes each format to the right converter.

### 2. Passthrough Formats (TXT, MD)
Tests that .txt and .md files are copied without conversion.

### 3. Unsupported Format (.xyz)
Tests graceful error handling - file is logged but doesn't crash batch.

### 4. Hidden Files (.hidden_skip.txt)
Tests that files starting with `.` are filtered out and not processed.

### 5. Filename Conflicts (duplicate base names)
Tests conflict resolution - files don't overwrite each other.

### 6. Empty Files
Tests handling of empty or near-empty files.

### 7. Recursive Subfolder Processing
Tests that files in subfolders are also processed.

### 8. Large File (NOT TESTED)
Current max file is 7.4 MB. To test 50MB boundary, need a file >50MB.
Limitation: Cannot easily create a 45+ MB file for testing.

---

## How to Run

1. Open File Explorer
2. Navigate to: `D:\贯维\Any2MD\bat\`
3. **Drag `test_batch_edge_cases` folder onto `run.bat`**
4. Watch the command window for progress
5. Check log file for results

---

## Verification

After running, check:
1. Log file in `logs/` directory
2. MD files created next to each source file
3. Hidden files NOT converted
4. Unsupported format ERROR logged (but batch continues)
5. Subfolder files converted