"""管理 Skill 元数据注册表"""
from typing import Dict

from runtime.skill.skill_metadata import SkillMetadata


class SkillRegistry:
    """
    skill元数据注册表

    负责管理Runtime中已发现的skill(说明这时候skill的元数据已经加载了)
    """
    def __init__(self):
        self._skills: Dict[str,SkillMetadata]= {}

    def register(self,metadata: SkillMetadata) -> None:
        """
        注册一个skill
        """
        if metadata.name in self._skills:
            raise ValueError(
                f"Skill已经注册:{metadata.name}"
            )
        self._skills[metadata.name] = metadata


    def get(self,name: str) -> SkillMetadata:
        """
        根据名称获取skill元数据
        """
        if name not in self._skills:
            raise KeyError(f"没有找到:{name}skill")
        return self._skills[name]

    def contains(self,name: str) -> bool:
        """判断skill是否已经注册"""
        return name in self._skills
    def list_skills(self)->list[SkillMetadata]:
        """获取所有已注册的skill"""
        return list(self._skills.values())

    def _len_(self)->int:
        """获取已注册skill的数量"""
        return len(self._skills)

    def replace_all(self,skills: list[SkillMetadata]) -> None:
        """
        原子替换当前注册表中全部的skill元数据
        """
        new_skills = {}
        for metadate in skills:
            if metadate.name  in new_skills:
                raise ValueError(f"Skill已经注册:{metadate.name}")
            new_skills[metadate.name] = metadate

        self._skills = new_skills


