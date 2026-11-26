from langchain_core.runnables import RunnableLambda
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
        awrap_tool_call=interceptor.async_tool_call_interceptor,)

    return tool_node.with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def handle_tool_error(state) -> dict:
    """
    处理工具调用时发生错误，根据tool_call_id手动封装一条toolMessage
    参数:
        state (dict): 当前状态，含 error 与 messages。
    返回:
        dict: 新的消息列表。
    """
    error = state.get("error")
    tool_calls = state['messages'][-1].tool_calls
    from langchain_core.messages import ToolMessage
    return {
        "messages":[
            ToolMessage(
                content=f"错误：{repr(error)}\n工具执行错误，根据错误信息判断是否再次执行还是直接响应用户",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }