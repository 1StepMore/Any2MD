"""Any2MD 公共 API - convert_to_markdown 返回字符串"""
from pathlib import Path
from typing import Union

from wheels.exceptions import (
    UnsupportedFormatError,
    FileTooLargeError,
    ConversionError,
)


def convert_to_markdown(
    file_path: Union[str, Path],
    mode: str = "fast",
    pdf_engine: str = "light"
) -> str:
    """将文档转换为 Markdown 文本字符串

    Args:
        file_path: 输入文件路径
        mode: 转换模式 - "fast" 或 "quality"
        pdf_engine: PDF 引擎 - "light" (markitdown) 或 "heavy" (MarkItDown + pypdfium2)

    Returns:
        Markdown 文本字符串

    Raises:
        FileNotFoundError: 文件不存在
        UnsupportedFormatError: 不支持的格式
        FileTooLargeError: 文件超过 50MB
        ConversionError: 转换失败

    Example:
        >>> md = convert_to_markdown("document.pdf")
        >>> print(md[:100])
    """
    # 延迟导入避免循环依赖
    from .pipeline import convert_file

    input_path = Path(file_path) if isinstance(file_path, str) else file_path

    # 复用 pipeline.convert_file 获取 Path，然后读取内容
    output_path = convert_file(
        input_path=input_path,
        mode=mode,
        pdf_engine=pdf_engine,
        output_dir=None  # 不指定 output_dir，生成临时文件
    )

    # 返回 Markdown 文本而非文件路径
    return output_path.read_text(encoding='utf-8')