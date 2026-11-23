from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def merge_loaded_skills(
        old:list[str],
        new:list[str]
) -> list[str] :
    """保序去重"""
    result = list(old)

    for skill_name in new:
        if skill_name not in result:
            result.append(skill_name)
    return result

def merge_skill_context(
    old: dict[str, str],
    new: dict[str, str]
) -> dict[str, str]:
    """Python字典解包合并，后面字典优先级更高"""
    old_dict = old if old is not None else {}
    new_dict = new if new is not None else {}
    return {**old_dict, **new_dict}

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    # 当前已加载的 Skill 名称
    loaded_skills: Annotated[list[str], merge_loaded_skills]

    # 当前已加载的 Skill 完整内容
    skill_context: Annotated[dict[str, str], merge_skill_context]


