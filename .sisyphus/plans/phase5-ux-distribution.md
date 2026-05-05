# Phase 5: 用户体验与分发

## TL;DR

> **Quick Summary**: 完善用户体验 - BAT 拖拽入口、完整 CLI 参数、logging 日志体系。
>
> **Deliverables**:
> - `bat/run.bat` - 拖拽式 BAT 入口
> - `cli.py` - 完整参数接口
> - `wheels/logger.py` - 标准 logging 模块
>
> **Estimated Effort**: Medium (3-4 小时)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: logger.py → cli.py → bat/run.bat → Integration

---

## Context

### Original Request
Phase 5 实现用户体验与分发：
1. BAT 拖拽入口 - 傻瓜式操作
2. CLI 参数完善 - 完整参数接口
3. 日志体系 - logging 模块
4. 阶段验收标准确认

### 已知约束 (from Phase 1-4)
- 当前 CLI 只有 `input_file` 和 `mode` 参数
- 当前日志使用 `print()` 直接输出
- 无 `--output`, `--pdf-engine`, `--concurrency`, `--config`, `--verbose` 参数
- 无 `--input/-i`, `--output/-o` 短选项
- 批处理中单个文件失败会 raise 异常中断整个流程

### 技术前提
- Python standard library `logging` 模块
- Windows BAT 批处理语法
- Typer 支持短选项 (`-i`, `-o`)

---

## Work Objectives

### Core Objective
提升用户体验，让非技术用户也能轻松使用 Any2MD。

### Concrete Deliverables
- `bat/run.bat` - 拖拽式 BAT 入口
- `cli.py` - 完整参数 (`-i`, `-o`, `--mode`, `--pdf-engine`, `--concurrency`, `--config`, `--verbose`)
- `wheels/logger.py` - 标准 logging 配置

### Definition of Done
- [ ] `python cli.py --help` 显示所有参数，含短选项
- [ ] `python cli.py -i input.pdf -o output_dir` 正常工作
- [ ] `bat/run.bat file.pdf` 拖拽执行成功
- [ ] 日志输出: `[INFO] processing file.pdf`, `[WARNING] fallback to markitdown`, `[ERROR] conversion failed`
- [ ] 单个文件失败不中断整个批处理 (异常被捕获)

### Must Have
- BAT 支持拖拽文件和文件夹
- BAT 激活虚拟环境
- CLI 所有新参数可用
- logging 模块替换 print()
- 三个日志级别 (INFO/WARNING/ERROR)
- 单文件异常不中断批处理

### Must NOT Have (Guardrails)
- 不改变核心转换逻辑
- 不删除现有功能
- 不添加非必要参数
- BAT 不支持多文件选择 (仅拖拽单文件/文件夹)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - 2 tasks, 可并行):
├── Task 1: wheels/logger.py - logging 模块配置
└── Task 2: cli.py - 完整参数接口

Wave 2 (Integration - 2 tasks, 依赖 Wave 1):
├── Task 3: bat/run.bat - 拖拽入口
└── Task 4: 异常处理完善 - 单文件失败不中断

Wave FINAL (1 task):
└── Task F1: Integration QA
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| T1 (logger.py) | None | T4, F1 |
| T2 (cli.py) | T1 (logging) | T3, F1 |
| T3 (bat/run.bat) | T2 (cli.py) | F1 |
| T4 (exception handling) | T1 (logger) | F1 |

---

## TODOs

### Wave 1 (Foundation - 2 tasks, parallel)

- [x] 1. **wheels/logger.py - logging 模块配置**

  **What to do**:
  - 创建 `wheels/logger.py`
  - 配置 `logging.basicConfig` 使用标准库
  - 定义三个日志级别:
    - `logger.info()` - 每个文件处理状态
    - `logger.warning()` - 降级和重试信息
    - `logger.error()` - 处理失败和环境缺失
  - 配置格式: `[时间戳] [级别] 消息`
  - 支持 `--verbose` 开关控制日志级别 (`logging.DEBUG` vs `logging.INFO`)

  **代码结构**:
  ```python
  import logging

  def setup_logger(verbose: bool = False) -> logging.Logger:
      level = logging.DEBUG if verbose else logging.INFO
      logging.basicConfig(
          format='[%(asctime)s] [%(levelname)s] %(message)s',
          datefmt='%Y-%m-%d %H:%M:%S',
          level=level
      )
      return logging.getLogger('any2md')

  # 全局 logger
  logger = setup_logger()
  ```

  **Must NOT do**:
  - 不使用第三方 logging 库 (用标准库)
  - 不改变现有 print() 行为 (重构为 logger.info())

- [x] 2. **cli.py - 完整参数接口**

  **What to do**:
  - 更新 `cli.py` main() 参数:
    ```python
    @app.command()
    def main(
        input_file: Path = typer.Option(..., "--input", "-i"),
        output_dir: Path = typer.Option(None, "--output", "-o"),
        mode: str = typer.Option("fast", "--mode"),
        pdf_engine: str = typer.Option("light", "--pdf-engine"),
        concurrency: int = typer.Option(None, "--concurrency"),
        config: Path = typer.Option(None, "--config"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ):
    ```
  - `--input/-i`: 输入文件或文件夹 (必需)
  - `--output/-o`: 输出目录 (默认为源文件所在目录)
  - `--mode`: quality/fast (默认 fast)
  - `--pdf-engine`: light/heavy (默认 light)
  - `--concurrency`: 最大并发数 (默认从 config 读取)
  - `--config`: 指定配置文件路径
  - `--verbose/-v`: 详细日志输出

  **Must NOT do**:
  - 不改变现有 `input_file` 位置参数 (保持向后兼容)
  - 不删除 `mode` 参数 (保留)
  - 不添加非文档化参数

---

### Wave 2 (Integration - 2 tasks)

- [x] 3. **bat/run.bat - 拖拽入口**
- [x] 4. **异常处理完善 - 单文件失败不中断**

  **What to do**:
  - 在 `async_convert_batch` 中捕获单个文件的异常
  - 当前异常会导致整个 batch 失败
  - 修改逻辑:
    ```python
    async def _async_convert_single(...):
        try:
            result = convert_file(input_path, mode)
            await _async_log(input_path, f"completed -> {result}")
            return result
        except Exception as e:
            await _async_log(input_path, f"failed: {e}")
            # 不 raise，让 batch 继续处理其他文件
            return None  # 返回 None 表示失败
    ```

  - 在 `cli.py` 文件夹模式中:
    - 收集所有成功和失败的文件
    - 最后显示汇总: `成功: 5, 失败: 2`

  **Must NOT do**:
  - 不吞掉所有异常 (致命错误仍需退出)
  - 不改变单文件模式的错误行为

---

## Final Verification Wave

- [x] F1. **Integration QA** — `unspecified-high`
  测试完整流程:
  1. BAT 拖拽单文件执行
  2. BAT 拖拽文件夹执行
  3. CLI --help 显示所有参数
  4. CLI -i/-o 短选项正常
  5. --verbose 日志详细输出
  6. 日志级别 INFO/WARNING/ERROR 正确
  7. 单文件失败不中断批处理
  Output: `BAT_File [PASS/FAIL] | BAT_Folder [PASS/FAIL] | CLI_Help [PASS/FAIL] | Short_Opts [PASS/FAIL] | Verbose [PASS/FAIL] | Log_Levels [PASS/FAIL] | NonFatal [PASS/FAIL]`

---

## Commit Strategy

- **Wave 1**: `feat(phase5): add logging module and complete CLI parameters`
  - Files: `wheels/logger.py`, `cli.py`
- **Wave 2**: `feat(phase5): add BAT drag-drop and exception handling`
  - Files: `bat/run.bat`, `pipeline.py` (exception handling)
- **Final**: `feat(phase5): add integration verification`

---

## Success Criteria

### Verification Commands
```bash
# CLI help
python cli.py --help

# Short options
python cli.py -i sample.pdf -o output/

# BAT test (manual)
# drag sample.pdf to run.bat

# Verbose mode
python cli.py -i sample.pdf --verbose

# Folder batch with failures
python cli.py ./test_folder 2>&1 | grep -E "\[INFO\]|\[WARNING\]|\[ERROR\]"
```

### Final Checklist
- [ ] BAT 拖拽文件正常执行
- [ ] BAT 拖拽文件夹正常执行
- [ ] CLI --help 显示所有参数
- [ ] CLI -i/-o 短选项正常工作
- [ ] --verbose 切换日志级别
- [ ] 日志输出 [INFO]/[WARNING]/[ERROR] 格式正确
- [ ] 单文件失败不中断批处理
- [ ] 批处理汇总显示成功/失败数量