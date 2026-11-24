"""定义一次模型请求所需的上下文数据结构"""
from dataclasses import dataclass

from langchain_core.messages import AnyMessage

#frozen=True 表示不能重新给快照字段赋值。
@dataclass(frozen=True)
class ContextSnapshot:
    """
    一次模型请求所需的上下文快照
    """
    #当前模型请求需要的对话消息。这里先使用 tuple，而不是直接返回原始 list，表达这是本轮构建完成的消息序列，不希望后续随意修改它。
    messages: tuple[AnyMessage,...]
    #格式化后的已加载 Skill 名称。
    loaded_skills :str
    #格式化后的 Skill 完整文档。
    skill_context :str
    #当前 Runtime 中可用的 Skill 目录。
    skill_catalog :str

