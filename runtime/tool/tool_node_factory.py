from langgraph.prebuilt import ToolNode

from runtime.tool.interceptor import ToolInterceptor
from runtime.tool.tool_registy import ToolPolicyRegistry


def create_tool_node(
        tools:list,
        tool_policy_registry:ToolPolicyRegistry,
):
    """
    创建带执行策略拦截的工具节点。

    Args:
        tools: 当前 Agent 可使用的工具列表。
        tool_policy_registry: 全局工具策略注册表。

    Returns:
        配置了执行策略的 ToolNode。
    """
    interceptor = ToolInterceptor(tool_policy_registry)
    tool_node = ToolNode(
        tools=tools,
        wrap_tool_call=interceptor.tool_call_interceptor,
        awrap_tool_call=interceptor.async_tool_call_interceptor
    )
    return tool_node