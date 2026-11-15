"""定义 Skill 元数据的数据结构"""
from dataclasses import dataclass
from pathlib import Path

#对象创建之后不能修改属性，相当于lombok
@dataclass(frozen=True)
class SkillMetadata:
    """
    Skill 元数据对象。

    用于描述一个 Skill 的基本信息和文件位置。
    """

    name: str #skill名字
    description: str #skill功能描述后续会提供给LLM
    skill_dir: Path #Skill所在的目录
    skill_file: Path #Skill.md的完整目录
