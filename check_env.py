"""
环境检测脚本

检测:
- Python版本
- 核心Python依赖是否安装
- 系统依赖(tesseract, poppler)

使用方法:
python check_env.py
"""

import importlib
import shutil
import sys
from pathlib import Path


def check_python_version():
    """检查Python版本 >= 3.10"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"[FAIL] Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print(f"       需要 Python 3.10+")
        return False
    print(f"[PASS] Python版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_python_package(name: str) -> bool:
    """检查Python包是否已安装"""
    try:
        importlib.import_module(name)
        print(f"[PASS] {name} 已安装")
        return True
    except ImportError:
        print(f"[FAIL] {name} 未安装")
        return False


def check_system_binary(name: str) -> bool:
    """检查系统二进制是否在PATH中,同时也检查常见安装路径"""
    path = shutil.which(name)
    if path:
        print(f"[PASS] {name} 已安装: {path}")
        return True

    # 检查常见安装路径
    common_paths = {
        "tesseract": [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ],
        "pdftoppm": [
            r"C:\Program Files\Poppler\poppler\Library\bin\pdftoppm.exe",
            r"C:\Program Files (x86)\Poppler\poppler\Library\bin\pdftoppm.exe",
            r"C:\ProgramData\chocolatey\bin\pdftoppm.exe",
        ],
        "pdfinfo": [
            r"C:\Program Files\Poppler\poppler\Library\bin\pdfinfo.exe",
            r"C:\Program Files (x86)\Poppler\poppler\Library\bin\pdfinfo.exe",
            r"C:\ProgramData\chocolatey\bin\pdfinfo.exe",
        ],
    }

    if name in common_paths:
        for cp in common_paths[name]:
            if Path(cp).exists():
                print(f"[PASS] {name} 已安装(非PATH): {cp}")
                return True

    print(f"[WARN] {name} 未安装 (可选,用于PDF heavy模式)")
    return False


def main():
    print("=" * 50)
    print("Any2MD 环境检测")
    print("=" * 50)
    print()

    all_passed = True

    # 1. Python版本
    print("[1] 检查Python版本...")
    if not check_python_version():
        all_passed = False
    print()

    # 2. 核心依赖
    print("[2] 检查核心Python依赖...")
    core_packages = [
        "filetype",
        "typer",
        "yaml",  # pyyaml
    ]
    for pkg in core_packages:
        if not check_python_package(pkg):
            all_passed = False
    print()

    # 3. 质量通道(可选)
    print("[3] 检查质量通道依赖(可选)...")
    quality_packages = [
        "pypandoc",
        "mammoth",
        "markdownify",
    ]
    quality_ok = True
    for pkg in quality_packages:
        if not check_python_package(pkg):
            quality_ok = False
    if quality_ok:
        print("[INFO] 质量通道已就绪")
    else:
        print("[INFO] 质量通道未完整安装,将以fast模式运行")
    print()

    # 4. 快速通道
    print("[4] 检查快速通道依赖...")
    if not check_python_package("markitdown"):
        all_passed = False
    print()

    # 5. PDF重型依赖(可选)
    print("[5] 检查PDF重型依赖(可选)...")
    check_system_binary("tesseract")
    check_system_binary("pdftoppm")  # poppler-utils
    # Python包检查(动态导入)
    # 注意: marker 与 Python 3.13 不兼容(cgi模块已移除)
    try:
        importlib.import_module("marker")
        print("[PASS] marker 已安装")
    except ImportError as e:
        if "cgi" in str(e):
            print("[WARN] marker 与 Python 3.13 不兼容 (cgi模块已移除)")
        else:
            print("[WARN] marker 未安装 (PDF heavy模式将降级到docling)")

    try:
        importlib.import_module("docling")
        print("[PASS] docling 已安装")
    except ImportError:
        print("[WARN] docling 未安装")
    print()

    # 6. 工程基建
    print("[6] 检查工程基建...")
    if not check_python_package("tenacity"):
        all_passed = False
    print()

    # 总结
    print("=" * 50)
    if all_passed:
        print("环境检测通过! 可以开始开发.")
    else:
        print("环境检测未完全通过,请安装缺失依赖.")
        print("运行: pip install -r requirements.txt")
    print("=" * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
