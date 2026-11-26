"""工具配置的策略模型"""
import math
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    SAFE = "safe"
    SENSITIVE = "sensitive"

@dataclass(frozen=True)
class ToolPolicy:
    tool_type: ToolType   #标识工具类别
    timeout: float        #单次工具执行的超时时间
    max_attempts: int     #最大执行次数，包含首次执行
    retryable: bool       #是否允许自动重试

    def __post_init__(self):
        """对象创建时执行参数校验"""

        if not isinstance(self.tool_type, ToolType):
            raise TypeError("tool_type 必须是 ToolType 类型")

        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError("timeout 必须是有限且大于 0 的数字")

        if self.max_attempts < 1:
            raise ValueError("max_attempts 必须大于等于 1")

        if not self.retryable and self.max_attempts != 1:
            raise ValueError("禁止重试的工具 max_attempts 必须为 1")

        if self.tool_type == ToolType.SENSITIVE and self.retryable:
            raise ValueError("敏感工具不允许自动重试")

