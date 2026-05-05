"""
Any2MD 配置加载模块

支持:
- 默认值填充
- 类型校验
- 友好的错误提示

配置项:
- output_mode: quality | fast
- pdf_engine: light | heavy
- max_file_size: int (MB)
- concurrency: int
- retry_count: int
- output_dir: str | null
- log_level: debug | info | warning | error
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

import yaml


# ========== 类型别名 ==========
OutputMode = Literal["quality", "fast"]
PdfEngine = Literal["light", "heavy"]
LogLevel = Literal["debug", "info", "warning", "error"]


# ========== 配置数据类 ==========
@dataclass
class Config:
    """Any2MD 配置"""

    output_mode: OutputMode = "fast"
    pdf_engine: PdfEngine = "light"
    max_file_size: int = 50  # MB
    concurrency: int = 4
    retry_count: int = 3
    output_dir: Optional[str] = None
    log_level: LogLevel = "info"

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """从YAML文件加载配置"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        return cls._from_dict(raw)

    @classmethod
    def _from_dict(cls, data: dict) -> "Config":
        """从字典创建配置,带默认值和校验"""
        return cls(
            output_mode=_validate_output_mode(data.get("output_mode", "fast")),
            pdf_engine=_validate_pdf_engine(data.get("pdf_engine", "light")),
            max_file_size=_validate_positive_int(
                data.get("max_file_size", 50), "max_file_size"
            ),
            concurrency=_validate_positive_int(
                data.get("concurrency", 4), "concurrency"
            ),
            retry_count=_validate_positive_int(
                data.get("retry_count", 3), "retry_count"
            ),
            output_dir=data.get("output_dir"),
            log_level=_validate_log_level(data.get("log_level", "info")),
        )

    def to_dict(self) -> dict:
        """导出为字典(用于调试)"""
        return {
            "output_mode": self.output_mode,
            "pdf_engine": self.pdf_engine,
            "max_file_size": self.max_file_size,
            "concurrency": self.concurrency,
            "retry_count": self.retry_count,
            "output_dir": self.output_dir,
            "log_level": self.log_level,
        }


# ========== 校验函数 ==========
def _validate_output_mode(value: any) -> OutputMode:
    """校验输出模式"""
    valid = {"quality", "fast"}
    if value not in valid:
        raise ValueError(
            f"output_mode 必须为 {valid} 之一, 收到: {value!r}"
        )
    return value


def _validate_pdf_engine(value: any) -> PdfEngine:
    """校验PDF引擎"""
    valid = {"light", "heavy"}
    if value not in valid:
        raise ValueError(
            f"pdf_engine 必须为 {valid} 之一, 收到: {value!r}"
        )
    return value


def _validate_positive_int(value: any, field_name: str) -> int:
    """校验正整数"""
    if not isinstance(value, int):
        raise TypeError(
            f"{field_name} 必须为整数, 收到: {type(value).__name__}"
        )
    if value <= 0:
        raise ValueError(f"{field_name} 必须大于0, 收到: {value}")
    return value


def _validate_log_level(value: any) -> LogLevel:
    """校验日志级别"""
    valid = {"debug", "info", "warning", "error"}
    if value not in valid:
        raise ValueError(
            f"log_level 必须为 {valid} 之一, 收到: {value!r}"
        )
    return value


# ========== 全局配置实例 ==========
_config: Optional[Config] = None


def load_config(config_path: str | Path | None = None) -> Config:
    """
    加载配置(全局单例)

    Args:
        config_path: 配置文件路径,默认查找 config.yaml

    Returns:
        Config实例
    """
    global _config

    if _config is not None:
        return _config

    if config_path is None:
        # 查找 config.yaml
        config_path = Path("config.yaml")
        if not config_path.exists():
            # 尝试上级目录
            config_path = Path(__file__).parent.parent / "config.yaml"

    if not Path(config_path).exists():
        # 使用默认配置
        _config = Config()
        return _config

    _config = Config.from_yaml(config_path)
    return _config


def get_config() -> Config:
    """获取已加载的配置,未加载则使用默认配置"""
    global _config
    if _config is None:
        return load_config()
    return _config


def reset_config() -> None:
    """重置配置(用于测试)"""
    global _config
    _config = None
