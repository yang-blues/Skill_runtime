"""工具增强"""
import asyncio
import logging
import random
import time

from runtime.tool.tool_registy import ToolPolicyRegistry

logger = logging.getLogger(__name__)

# 允许自动重试的异常白名单
RETRYABLE_TOOL_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
)
class ToolInterceptor:
    """工具拦截器"""
    def __init__(self,tool_policy_registry: ToolPolicyRegistry):
        self._tool_policy_registry = tool_policy_registry

        #指数退避配置
        self.initial_delay = 0.5
        self.max_delay = 4.0

    def _calculate_retry_delay(self,attempt:int) -> float:
        """
        计算指数退避+随机抖动等待时间
        Args:
            attempt:当前已经失败的尝试次数
        Return:
            本次重试前需要等待的秒数
        """
        cap = min(
            self.initial_delay * (2** (attempt - 1)),
            self.max_delay
        )

        return random.uniform(0,cap)



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
        start_time = time.perf_counter()
        #retryable=False时,策略模型保证max_attempts = 1
        max_attempts = (
            tool_policy.max_attempts
            if tool_policy.retryable
            else 1
        )
        try:
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(
                        "工具开始 | 工具名称=%s | 执行次数 = %s",
                        tool_name,
                        attempt,
                    )
                    #2.执行原始工具
                    result = execute(request)
                    logger.info(
                        "工具执行成功 | 工具名称=%s | 执行次数=%s",
                        tool_name,
                        attempt,
                    )
                    return result

                except RETRYABLE_TOOL_EXCEPTIONS as e:
                    #满足重试条件时继续循环
                    if attempt >= max_attempts:
                        logger.exception(
                            "工具重试次数用尽 | 工具名称=%s |尝试次数=%s |异常类型=%s",
                            tool_name,
                            attempt,
                            type(e).__name__,
                        )
                        #重试次数耗尽跳出循环抛出异常
                        raise
                    #4.计算指数退避 + 司机抖动时间
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        "工具尝试重试 | 工具名称=%s | 尝试次数=%s | 异常类型=%s",
                        tool_name,
                        attempt,
                        type(e).__name__,
                    )
                    #5.等待
                    time.sleep(delay)
                except Exception as e:
                    # 其他异常直接抛出，不再重试
                    logger.exception(
                        "工具执行失败 | 工具名称=%s | 尝试次数=%s | 异常类型=%s",
                        tool_name,
                        attempt,
                        type(e).__name__,
                    )
                    raise
        finally:
                duration_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                logger.info(
                    "工具调用结束 | 工具名称=%s | duration_ms=%.2f",
                    tool_name,
                    duration_ms,
                )

    async def async_tool_call_interceptor(self, request, execute):
        """
        异步工具调用拦截器
        """
        tool_name = request.tool_call["name"]
        # 1.获取当前工具对应的执行策略
        tool_policy = self._tool_policy_registry.get_policy(tool_name)
        start_time = time.perf_counter()
        # retryable=False时，策略模型保证max_attempts = 1
        max_attempts = (
            tool_policy.max_attempts
            if tool_policy.retryable
            else 1
        )
        try:
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(
                        "工具开始 | 工具名称=%s | 执行次数=%s",
                        tool_name,
                        attempt,
                    )
                    # 2.执行原始工具
                    # 进入execute函数，从头到尾执行里面代码，没有await，这个协程不会主动让出时间循环
                    # 同步逻辑会阻塞当前事件循环，直到函数返回。回到wait_for，在判断是否超时
                    # 如果有await协程会在await点出事件循环，事件循环可以调度其他任务。超时事件到了就会取消这个任务
                    result = await asyncio.wait_for(
                        execute(request),
                        timeout=tool_policy.timeout,
                    )
                    logger.info(
                        "工具执行成功 | 工具名称=%s | 执行次数=%s",
                        tool_name,
                        attempt,
                    )

                    return result
                except RETRYABLE_TOOL_EXCEPTIONS as e:
                    # 满足重试条件时继续循环
                    if attempt >= max_attempts:
                        logger.exception(
                            "工具重试次数用尽 | 工具名称=%s | 尝试次数=%s |异常类型=%s",
                            tool_name,
                            attempt,
                            type(e).__name__,
                        )
                        # 重试次数耗尽跳出循环抛出异常
                        raise
                    # 4.计算指数退避 + 随机抖动时间
                    delay = self._calculate_retry_delay(attempt)

                    logger.warning(
                        "工具尝试重试 | 工具名称=%s | 尝试次数=%s | 异常类型=%s",
                        tool_name,
                        attempt,
                        type(e).__name__,
                    )
                    # 5.异步等待，不阻塞事件循环
                    await asyncio.sleep(delay)
                except Exception as e:
                    # 其他异常直接抛出，不再重试
                    logger.exception(
                        "工具执行失败 | 工具名称=%s | 尝试次数=%s | 异常类型=%s",
                        tool_name,
                        attempt,
                        type(e).__name__,
                    )
                    raise
        finally:
            duration_ms = (
                                  time.perf_counter() - start_time
                          ) * 1000

            logger.info(
                "工具调用结束 | 工具名称=%s | duration_ms=%.2f",
                tool_name,
                duration_ms,
            )