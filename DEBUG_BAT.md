# BAT 调试记录

## 问题现象

用户拖拽文件到 `run.bat` 时报错：
```
python: can't open file 'D:\\贯维\\Any2MD\\bat\\cli.py': [Errno 2] No such file or directory
```

或参数解析错误：
```
Got unexpected extra argument (Global共创教练团.pdf D:\贯维\Any2MD\bat\OPC Global共创教练团.pdf)
```

---

## 根本原因分析

### 1. 工作目录问题 (CWD)

**现象**: 拖拽文件时 Windows 设置工作目录为 `bat\`，而非项目根目录。

**原因**: `python cli.py` 在 `bat\` 目录执行，但 `cli.py` 位于项目根目录。

**修复**:
```batch
cd /d "%~dp0.."  # 切换到项目根目录 (bat 的上级)
```

---

### 2. 中文/Unicode 路径问题

**现象**: 路径含中文时参数解析错误。

**原因**: `EnableDelayedExpansion` 会导致中文路径中的变量被错误展开。

**修复**: 移除 `EnableDelayedExpansion`，直接传递参数。

---

### 3. 引号处理问题

**现象**: 含空格路径被拆分成多个参数。

**原因**: 路径如 `D:\贯维\OPC Global共创教练团.pdf` 被空格分割。

**修复**: 使用 `%*` 直接传递所有参数，保持原始引号。

---

### 4. 路径变量误展开

**现象**: `%~1` 返回带引号或不带引号不一致。

**原因**: 复杂变量操作导致引号处理混乱。

**修复**: 移除中间变量，直接用 `%*` 传递参数。

---

## 修复历程

### 版本 1 (原始版)
```batch
@echo off
setlocal

set "INPUT_PATH=%~1"
python cli.py --input "%INPUT_PATH%" %*
```
**问题**: CWD 是 `bat\`，找不到 `cli.py`

---

### 版本 2 (添加目录切换)
```batch
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
python cli.py --input "%INPUT_PATH%" %*
```
**问题**: `%~dp0` 指向 `bat\`，需要 `..` 上级目录

---

### 版本 3 (使用 %~dp0..)
```batch
cd /d "%~dp0.."
python cli.py --input "%INPUT_PATH%" %*
```
**问题**: 参数中文字符被 `EnableDelayedExpansion` 破坏

---

### 版本 4 (移除 EnableDelayedExpansion)
```batch
setlocal EnableDelayedExpansion
# 移除复杂变量操作
```
**问题**: 仍然有引号处理问题

---

### 版本 5 (简化引号处理)
```batch
set "INPUT_PATH=%~1"
set "INPUT_PATH=%INPUT_PATH:"=%"
python cli.py --input "%INPUT_PATH%" %*
```
**问题**: `%~1` 本身带引号，strip 后丢失

---

### 版本 6 (直接用 %*)
```batch
if "%~1"=="" (
    echo Drag a file...
    pause
    exit /b 1
)

cd /d "%~dp0.."
python cli.py %*
```
**状态**: ✅ 工作

---

## 最终修复代码

```batch
@echo off
chcp 65001 >nul 2>&1

REM 检查参数
if "%~1"=="" (
    echo Drag a file or folder onto this batch file.
    echo Or run from command line: run.bat "path\to\file.pdf"
    pause
    exit /b 1
)

REM 激活虚拟环境
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
)

REM 切换到项目根目录
cd /d "%~dp0.."

REM 运行转换 (直接传递所有参数)
python cli.py %*

REM 暂停显示结果
echo.
echo Conversion complete. Press any key to exit.
pause >nul
```

---

## 关键教训

### 1. Windows BAT 变量展开顺序
- `%~1` = 移除引号的第一个参数
- `%1` = 保留引号
- `%*` = 所有参数，保留原始引号

### 2. 工作目录陷阱
- 拖拽文件时 CWD = 文件所在目录
- 不是 BAT 文件所在目录
- 必须用 `%~dp0` 手动定位

### 3. 中文路径处理
- `EnableDelayedExpansion` 会破坏含特殊字符的路径
- 简单方案: 用 `%*` 直接传递，不做变量操作
- `chcp 65001` 设置 UTF-8 代码页

### 4. 引号处理
- `%~1` 自动移除一对引号
- `%1` 保留引号
- `%*` 传递所有参数，保持原始引号

### 5. 推荐实践
```batch
REM 正确: 直接用 %*
python cli.py %*

REM 错误: 中间变量容易出问题
set "PATH=%~1"
python cli.py --input "%PATH%"
```

---

## 验证方法

### 测试用例
```batch
run.bat "D:\贯维\OPC Global共创教练团.pdf"
```

### 预期结果
- 窗口保持打开
- 显示转换进度
- 产物在 `D:\贯维\OPC Global共创教练团.md`

---

## 相关文件

- `bat/run.bat` - Windows 拖拽入口
- `cli.py` - CLI 入口
- `pipeline.py` - 异步批处理
