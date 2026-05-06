# Any2MD Wheels 使用指南

## 安装

### 从源码安装（开发模式）

```bash
cd Any2MD
pip install -e .
```

### 从 PyPI 安装（待发布）

```bash
pip install any2md
```

## 编程调用

### 基本用法

```python
from any2md import convert_to_markdown

# 转换文件
md_text = convert_to_markdown("document.pdf")
print(md_text[:100])  # 打印前100个字符
```

### 指定转换模式

```python
# 快速模式（默认）- 使用 markitdown，速度快
md = convert_to_markdown("document.pdf", mode="fast")

# 质量模式 - 使用专业转换器，输出更优质
md = convert_to_markdown("document.docx", mode="quality")
```

### 指定 PDF 引擎

```python
# 轻量引擎（默认）- 使用 markitdown，无需额外依赖
md = convert_to_markdown("document.pdf", pdf_engine="light")

# 重型引擎 - 使用 MarkItDown + pypdfium2，表格/布局识别更强
# 需要安装: apt install tesseract-ocr poppler-utils (Linux)
md = convert_to_markdown("document.pdf", mode="quality", pdf_engine="heavy")
```

### 异常处理

```python
from any2md import convert_to_markdown
from any2md import (
    FileNotFoundError,
    FileTooLargeError,      # 文件超过 50MB
    UnsupportedFormatError,  # 不支持的格式
    ConversionError,         # 转换失败
    Any2MDRuntimeError,     # 所有异常的基类
)

try:
    md = convert_to_markdown("document.pdf")
except FileNotFoundError:
    print("文件不存在")
except FileTooLargeError:
    print("文件超过 50MB 限制")
except UnsupportedFormatError:
    print("不支持的文件格式")
except ConversionError:
    print("转换失败")
except Any2MDRuntimeError:
    # 捕获所有 Any2MD 相关异常
    print("Any2MD 错误")
```

### 向后兼容

由于所有自定义异常都继承自 `RuntimeError`，原有代码可以继续使用：

```python
try:
    md = convert_to_markdown("document.pdf")
except RuntimeError as e:
    # 仍然可以捕获所有 Any2MD 异常
    print(f"转换失败: {e}")
```

## CLI 使用

### 单文件转换

```bash
any2md -i document.pdf
any2md -i document.docx --mode quality
any2md -i document.pdf --pdf-engine heavy
```

### 文件夹批量转换

```bash
any2md -i ./documents/
# 输出到 documents_converted/ 目录
```

### 查看帮助

```bash
any2md --help
```

## BAT 拖拽使用（Windows）

将文件或文件夹拖拽到 `bat/run.bat` 即可转换。

## 支持的格式

| 格式 | 质量模式 | 快速模式 |
|------|---------|---------|
| PDF | MarkItDown/pypdfium2 | markitdown |
| DOCX | pypandoc | markitdown |
| PPTX | pypandoc | markitdown |
| XLSX | pypandoc | markitdown |
| HTML | markdownify | markitdown |
| MD/TXT | 直接传递 | 直接传递 |

## 配置

在项目根目录创建 `config.yaml`：

```yaml
output_mode: fast        # 或 quality
pdf_engine: light        # 或 heavy
max_file_size: 50        # MB
concurrency: 4
retry_count: 3
log_level: info          # debug, info, warning, error
```

## Python API 参考

### `convert_to_markdown(file_path, mode='fast', pdf_engine='light') -> str`

将文档转换为 Markdown 文本字符串。

**参数：**
- `file_path`: 输入文件路径（str 或 Path）
- `mode`: 转换模式 - `"fast"` 或 `"quality"`
- `pdf_engine`: PDF 引擎 - `"light"` 或 `"heavy"`

**返回：**
- Markdown 文本字符串

**异常：**
- `FileNotFoundError`: 文件不存在
- `FileTooLargeError`: 文件超过 50MB
- `UnsupportedFormatError`: 不支持的格式
- `ConversionError`: 转换失败

**示例：**

```python
from pathlib import Path
from any2md import convert_to_markdown

# 字符串路径
md1 = convert_to_markdown("document.pdf")

# Path 对象
md2 = convert_to_markdown(Path("document.docx"), mode="quality")

# 指定所有参数
md3 = convert_to_markdown(
    "document.pdf",
    mode="quality",
    pdf_engine="heavy"
)
```
