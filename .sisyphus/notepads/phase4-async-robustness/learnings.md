# Phase 4 Async Robustness - Learnings

## Task
Refactor `pipeline.py` to add async/await support with asyncio.Semaphore concurrency control

## Key Patterns Learned

### 1. asyncio.Semaphore for Concurrency Control
```python
semaphore = asyncio.Semaphore(concurrency)
async with semaphore:
    # Only `concurrency` tasks can run this block simultaneously
```

### 2. asyncio.gather for Parallel Execution
```python
tasks = [_async_convert_single(p, mode, semaphore) for p in paths]
results = await asyncio.gather(*tasks)
```

### 3. Thread-safe Logging with asyncio.Lock
```python
_log_lock = asyncio.Lock()

async def _async_log(file_path: Path, status: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with _log_lock:
        print(f"[{timestamp}] [{file_path}] status: {status}")
```

### 4. Module-level asyncio.Lock Initialization
- `_log_lock = asyncio.Lock()` at module level works because asyncio.Lock() is created in the main thread before any event loop runs
- Alternative: use `async with Lock()` inside async functions

## Design Decisions

1. **Preserved sync `convert_file()`** - Backward compatibility for CLI single-file usage
2. **Async batch for programmatic usage** - When processing multiple files programmatically
3. **Lock for thread-safe logging** - Multiple coroutines printing simultaneously won't interleave

## Implementation Summary

- Added imports: `asyncio`, `datetime`, `from typing import List`
- Created `_async_log()` - Thread-safe logging with timestamp format `[timestamp] [file_path] status: message`
- Created `_async_convert_single()` - Wraps sync `convert_file()` with semaphore + logging
- Created `async_convert_batch()` - Uses `asyncio.Semaphore(concurrency)` + `asyncio.gather()`
- Original `convert_file()` unchanged - Preserved for backward compatibility

## CLI Folder Input Support

### Task
Add folder input support with recursive processing to `cli.py`

### Key Changes

1. **Imports added**: `asyncio`, `async_convert_batch`, `get_config`
2. **New parameter**: `concurrency: int = typer.Option(None)` - None means use config default
3. **Directory detection**: `input_file.is_dir()` triggers recursive file finding
4. **File discovery**: Uses `Path.rglob()` with extension filtering and hidden file exclusion
5. **Batch processing**: Calls `asyncio.run(async_convert_batch(files, mode, concurrency_limit))`

### Implementation Pattern

```python
if input_file.is_dir():
    files = []
    for ext in extensions:
        for f in input_file.rglob(f'*{ext}'):
            if not f.name.startswith('.'):
                files.append(f)
    
    concurrency_limit = concurrency if concurrency is not None else get_config().concurrency
    results = asyncio.run(async_convert_batch(files, mode, concurrency_limit))
    return
```

### Supported Extensions
`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.html`, `.htm`, `.md`, `.txt`

### Design Decisions

1. **No --batch flag** - Folder detection is automatic based on `is_dir()`
2. **Preserved single file handling** - Uses existing `convert_file()` for non-directory inputs
3. **Graceful handling** - Shows message if no files found in directory

## Tenacity Retry Decorator for Transient Errors

### Task
Add tenacity retry decorator to `converter_pdf.py` for transient error handling

### Key Implementation

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def _retry_on_transient(exception):
    if isinstance(exception, (subprocess.TimeoutExpired, MemoryError)):
        return True
    if isinstance(exception, OSError):
        if hasattr(exception, 'errno') and exception.errno in (11, 12):
            return False
        return True
    return False

class PdfConverter(BaseConverter):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_retry_on_transient),
    )
    def convert(self, input_path: Path) -> str:
        ...
```

### Retry Strategy
- **max_attempts=3** with exponential backoff (multiplier=1, min=1, max=10)
- **Retry on**: `subprocess.TimeoutExpired`, `MemoryError`, `OSError` (except EAGAIN/ENOMEM)
- **Do NOT retry on**: `ValueError`, `FileNotFoundError`, `ImportError`

### OSError errno codes
- EAGAIN = 11 (resource temporarily unavailable - don't retry)
- ENOMEM = 12 (out of memory - don't retry, install problem not transient)
