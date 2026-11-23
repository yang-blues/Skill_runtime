"""从内存中读取当前的skill注册表
每次程序启动只加载一次磁盘加载到我们的内存中
如果skill目录刷新才会更新内存数据"""
from runtime.skill import SkillRegistry


def build_skill_catalog(registry: SkillRegistry) -> str:
    """
    根据当前SkillRegistry构建Skill Catalog
    Args:
        registry: 当前Runtime的skill注册表
    Returns:
        供LLM阅读的Skill目录文本
    """

    skills = registry.list_skills()

    if not skills:
        return "当前没有可用的 SKill"
    catalog = [
        "## Available Skills",
        "以下是当前Runtime中可用的SKill："
    ]
    for index, metadata in enumerate(skills,start=1):
        catalog.append(
            f"{index}.{metadata.name}\n"
            f"描述：{metadata.description}"
        )
    return "\n\n".join(catalog)
