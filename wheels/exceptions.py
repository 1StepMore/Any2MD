"""Any2MD 异常层次结构 - 继承自内置类型保证向后兼容"""

class Any2MDRuntimeError(RuntimeError):
    """Any2MD 异常基类 - 继承自 RuntimeError 保证 cli.py 兼容"""
    pass

class FileTooLargeError(Any2MDRuntimeError):
    """文件超过 50MB 限制"""
    pass

class UnsupportedFormatError(Any2MDRuntimeError):
    """不支持的文件格式"""
    pass

class ConversionError(Any2MDRuntimeError):
    """转换过程失败"""
    pass

class ConfigError(Any2MDRuntimeError):
    """配置错误"""
    pass