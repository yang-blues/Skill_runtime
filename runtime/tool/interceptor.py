"""工具增强"""
from runtime.tool.tool_registy import ToolPolicyRegistry


class ToolInterceptor:
    """工具拦截器"""
    def __init__(self,tool_policy_registry: ToolPolicyRegistry):
        self._tool_policy_registry = tool_policy_registry



    def tool_call_interceptor(self,request,execute):
        """
        同步工具调用拦截器

        Args:
            request:工具的执行请求
            execute:工具的执行器
        Returns:
            工具的执行结果
        """
        tool_name = request.tool_call["name"]
        #1.获取当前工具对应的策略
        tool_policy = self._tool_policy_registry.get_policy(tool_name)

        result = execute(request)

        return result


    async def async_tool_call_interceptor(self, request, execute):
        """
        异步工具调用拦截器
        """
        tool_name = request.tool_call["name"]
        # 1.获取当前工具对应的策略
        tool_policy = self._tool_policy_registry.get_policy(tool_name)

        result = await execute(request)

        return result