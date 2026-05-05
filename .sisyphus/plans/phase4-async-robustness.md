# Phase 4: 并发调度与健壮性

## TL;DR

> **Quick Summary**: 升级 pipeline.py 为 asyncio 高并发模式 + tenacity 重试机制 + 文件夹批量处理。
>
> **Deliverables**:
> - `pipeline.py` - 重构为 async/await 异步模式
> - `wheels/converters/*.py` - 集成 tenacity 重试装饰器
> - `cli.py` - 支持文件夹输入
> - `config.yaml` - concurrency 参数生效
>
> **Estimated Effort**: Medium-Large (重构 + 新功能，8-10 小时)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: pipeline.py async 重构 → tenacity 装饰器 → 文件夹批量处理 → 集成测试

---

## Context

### Original Request
Phase 4 实现并发调度与健壮性：
1. asyncio 高并发流水线 - 同步改异步
2. Tenacity 重试机制 - 临时错误重试
3. 文件夹批量处理 - 递归遍历目录
4. 验收标准确认

### 已知约束 (from Phase 1-3)
- 同步单文件处理是当前瓶颈
- 50MB 文件大小限制存在
- 名称冲突处理已有 `_get_unique_output_path()`
- 日志输出到 stderr (print/f"{...}")
- config.yaml 有 `concurrency: 4` 字段但未使用

### 技术前提
- Python 3.10+ asyncio 支持
- tenacity 已安装 (requirements.txt)
- 所有转换器返回 string (markdown)，不涉及 async

---

## Work Objectives

### Core Objective
将 Any2MD 从单文件同步处理升级为多文件并发处理，同时保持错误恢复能力和日志清晰度。

### Concrete Deliverables
- `pipeline.py` - `async_convert_file()` + `async_convert_batch()`
- `wheels/converters/converter_*.py` - tenacity 装饰器
- `cli.py` - 支持文件夹路径输入 + `--concurrency` 参数
- `config.yaml` - concurrency 参数实际生效

### Definition of Done
- [ ] `python cli.py file1.pdf file2.docx --concurrency 2` 并发处理成功
- [ ] 3 个文件并发时，Semaphore 确保同时最多 2 个
- [ ] 超大文件转换失败时，重试 3 次后报告最终错误
- [ ] `python cli.py ./input_folder` 递归处理所有文件
- [ ] 日志输出不交叉混乱，每文件状态清晰

### Must Have
- asyncio.gather 并行处理多个文件
- asyncio.Semaphore 控制最大并发数
- tenacity 装饰器 (max_attempts=3, exponential backoff)
- 文件夹递归遍历 (rglob)
- 日志包含 file path + status + timestamp

### Must NOT Have (Guardrails)
- 不破坏现有单文件处理逻辑
- 不重试配置错误 (如 missing converter)
- 不并发处理超过 concurrency 限制
- 不修改 converter 接口 (保持返回 string)
- 不添加 --batch 或 --async 标志 (直接支持文件夹)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - 4 tasks, 依赖关系少，可并行):
├── Task 1: pipeline.py async 重构 (core)
├── Task 2: tenacity 装饰器 (各 converter)
├── Task 3: cli.py 文件夹支持
└── Task 4: 日志增强 (file path + timestamp)

Wave 2 (Integration - 3 tasks, 依赖 Wave 1):
├── Task 5: Async pipeline + folder 无缝集成
├── Task 6: Semaphore 并发控制验证
└── Task 7: 重试策略验证

Wave FINAL (1 task):
└── Task F1: End-to-end integration QA

Critical Path: T1 → T5 → F1
Parallel Speedup: ~60% with Wave 1 parallelization
Max Concurrent: 4 (Wave 1), 3 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| T1 (pipeline async) | None | T5, T7 |
| T2 (tenacity) | None | T7 |
| T3 (cli folder) | None | T5 |
| T4 (logging) | None | T5 |
| T5 (integration) | T1, T3, T4 | F1 |
| T6 (semaphore) | T1 | F1 |
| T7 (retry verify) | T1, T2 | F1 |

---

## TODOs

### Wave 1 (Foundation - 4 tasks, parallel)

- [x] 1. **pipeline.py - async 重构**
- [x] 2. **tenacity 装饰器集成**
- [x] 3. **cli.py - 文件夹支持**
- [x] 4. **日志增强** (integrated in T1 - _async_log function)

  **What to do**:
  - 每个文件的日志包含: `[timestamp] [file path] status: message`
  - 使用 `asyncio.Lock` 保护 print 避免交叉
  - 输出格式: `[2026-05-05 12:00:00] [file.pdf] Converting...`
  - 最终状态: `SUCCESS` / `FAILED: {error}`

  **Must NOT do**:
  - 不改变日志级别 (保持 info)
  - 不添加文件日志 (stdout/stderr only)

---

### Wave 2 (Integration - 3 tasks)

- [x] 5. **Async pipeline + folder 无缝集成** - T5 PASS
- [x] 6. **Semaphore 并发控制验证** - T6 PASS
- [x] 7. **重试策略验证** - T7 PASS (fixed FileNotFoundError check)

  **What to do**:
  - 模拟 MemoryError 触发重试
  - 验证最多重试 3 次
  - 验证指数退避 (1s, 2s, 4s)
  - 验证非临时错误不重试

---

## Final Verification Wave

- [x] F1. **End-to-end Integration QA** — `unspecified-high`
  测试完整流程:
  1. 单文件处理 (回归测试)
  2. 多文件并发处理 (3 文件，concurrency=2)
  3. 文件夹批量处理 (递归子目录)
  4. Semaphore 限制验证 (并发数检查)
  5. 重试机制验证 (模拟失败)
  6. 日志清晰度验证 (每文件状态可追踪)
  Output: `Single [PASS/FAIL] | Concurrent [PASS/FAIL] | Folder [PASS/FAIL] | Semaphore [PASS/FAIL] | Retry [PASS/FAIL] | Logging [PASS/FAIL]`

---

## Commit Strategy

- **Wave 1**: `feat(phase4): add async pipeline with semaphore control`
  - Files: pipeline.py (async functions)
- **Wave 1**: `feat(phase4): add tenacity retry for transient errors`
  - Files: converters with tenacity decorators
- **Wave 1**: `feat(phase4): add folder batch processing support`
  - Files: cli.py, pipeline.py (folder detection)
- **Wave 1**: `feat(phase4): enhance logging with per-file tracking`
  - Files: pipeline.py (logging improvements)
- **Final**: `feat(phase4): add integration verification`

---

## Success Criteria

### Verification Commands
```bash
# Single file (regression)
python cli.py sample.pdf && echo "Single: OK"

# Multi-file concurrent
python cli.py f1.pdf f2.docx f3.html --concurrency 2 && echo "Concurrent: OK"

# Folder batch
python cli.py ./test_folder && echo "Folder: OK"

# Check logs for timestamp + path
python cli.py sample.pdf 2>&1 | grep -E "\[.*\] \[.*\]"
```

### Final Checklist
- [ ] async_convert_batch 并发处理多个文件
- [ ] Semaphore 确保 concurrency 不超标
- [ ] tenacity 重试临时错误 (MemoryError, Timeout)
- [ ] 文件夹递归遍历正常工作
- [ ] 日志包含 timestamp + file path + status
- [ ] 单文件处理无回归