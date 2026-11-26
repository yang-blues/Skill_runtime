
from typing import Mapping, Sequence

from runtime.tool.tool_policy import ToolPolicy


class ToolPolicyRegistry:
    """
    Tool 策略注册表。

    负责管理工具名称与执行策略之间的映射关系。
    """

    def __init__(self):
        self._tools_policy: dict[str, ToolPolicy] = {}

    def register(self, tool_name: str, tool_policy: ToolPolicy) -> None:
        """注册单个工具策略。"""
        self._validate_entry(tool_name, tool_policy)

        if tool_name in self._tools_policy:
            raise KeyError(f"Tool {tool_name} 不允许重复注册")

        self._tools_policy[tool_name] = tool_policy

    def register_all(
        self,
        policies: Mapping[str, ToolPolicy]
    ) -> None:
        """
        批量增量注册。

        全部验证成功后才提交，失败时保留原有数据。
        """
        new_policies = {}

        # 第一阶段：验证并构建临时字典
        for tool_name, tool_policy in policies.items():
            self._validate_entry(tool_name, tool_policy)

            if tool_name in new_policies:
                raise KeyError(f"批量注册中存在重复工具: {tool_name}")

            if tool_name in self._tools_policy:
                raise KeyError(f"Tool {tool_name} 不允许重复注册")

            new_policies[tool_name] = tool_policy

        # 第二阶段：提交
        self._tools_policy.update(new_policies)

    
    def get_policy(self, tool_name: str) -> ToolPolicy:
        """获取指定工具的执行策略。"""
        if tool_name not in self._tools_policy:
            raise KeyError(f"Tool {tool_name} 没有注册")

        return self._tools_policy[tool_name]

    def has_policy(self, tool_name: str) -> bool:
        """判断工具是否注册。"""
        return tool_name in self._tools_policy


    def list_tools(self) -> list[str]:
        """返回已注册工具名称。"""
        return list(self._tools_policy.keys())

    def __len__(self) -> int:
        return len(self._tools_policy)

    @staticmethod
    def _validate_entry(
        tool_name: str,
        tool_policy: ToolPolicy
    ) -> None:
        """验证注册数据。"""
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("tool_name 必须是非空字符串")

        if not isinstance(tool_policy, ToolPolicy):
            raise TypeError("tool_policy 必须是 ToolPolicy 类型")

    def _get_tool_name(self,tool) -> str:
        """
        获取工具名称

        兼容Langchain BaseTool 和普通Python Callable
        """
        tool_name = getattr(tool, "name", None)
        if tool_name is None:
            tool_name = getattr(tool, "__name__", None)

        if not isinstance(tool_name,str) or not tool_name.strip():
            raise ValueError(
                f"无法获取有效的工具名称:{tool!r}"
            )
        return tool_name

    def initialize_tool_policy_registry(self,
        tools: Sequence,
        policy_config: Mapping[str, ToolPolicy]) :
        """
        根据实际工具列表和策略配置初始化 ToolPolicyRegistry。

        初始化过程：
        1. 获取实际工具名称
        2. 检查工具名称重复
        3. 检查缺失策略和多余策略
        4. 批量注册策略

        Args:
            tools: 当前 Agent 实际使用的工具列表。
            policy_config: 工具名称与执行策略的映射。

        """
        #1.参数检查
        if not isinstance(policy_config, Mapping):
            raise TypeError("policy_config 必须是 Mapping")

        #2.获取实际工具名称，并检查重复
        tool_names = []
        for tool in tools:
            tool_name = self._get_tool_name(tool)
            if tool_name in tool_names:
                raise ValueError(
                    f"实际工具列表存在重复工具: {tool_name}"
                )
            tool_names.append(tool_name)
        #3.获取配置中的工具名称
        policy_names = set(policy_config.keys())
        actual_names = set(tool_names)
        # 4. 检查策略缺失和多余
        missing_policies = actual_names - policy_names
        unknown_policies = policy_names - actual_names

        if missing_policies or unknown_policies:
            raise ValueError(
                "工具与策略配置不匹配: "
                f"缺失策略={sorted(missing_policies)}, "
                f"多余策略={sorted(unknown_policies)}"
            )
        #5.批量注册策略
        self.register_all(policy_config)


