"""从State和Runtime获取数据，构建上下文快照"""
from agent.state import AgentState
from runtime.context.context_snapshot import ContextSnapshot
from runtime.skill import SkillRegistry
from runtime.skill.skill_catalog import build_skill_catalog

#构造函数注入的是对象长期工作所依赖的服务，普通方法参数传入的是本次操作需要处理的数据。
class ContextBuilder:
    def __init__(self,skill_registry:SkillRegistry):
        self.skill_registry = skill_registry

    def build(self,state:AgentState) -> ContextSnapshot:
        # 1.获取当前已经加载的skill名称
        loaded_skills = state.get("loaded_skills", [])
        # 2.获取当前已经加载的skill完整内容
        skill_context = state.get("skill_context", {})
        # 3. 动态构建当前 Skill Catalog
        skill_catalog = build_skill_catalog(self.skill_registry)
        messages = tuple(state.get("messages", []))
        loaded_skills_text = self._format_loaded_skills(loaded_skills)
        skill_context_text = self._format_skill_context(skill_context)
        return ContextSnapshot(
            messages=messages,
            loaded_skills=loaded_skills_text,
            skill_context=skill_context_text,
            skill_catalog=skill_catalog,
        )


    def _format_loaded_skills(self,loaded_skills:list[str]) -> str:
        """ 格式化已加载的Skill名称"""
        loaded_skills_text = (
            "\n".join(f"-{name}" for name in loaded_skills)
            if loaded_skills
            else "当前没有已加载的Skill"
        )
        return loaded_skills_text


    def _format_skill_context(self,skill_context:dict[str, str]) -> str:
        """格式化Skill文档"""
        skill_context_text = (
            "\n\n".join(
                f"## Skill:{name}\n{content}"
                for name, content in skill_context.items()
            )
            if skill_context
            else "当前没有已加载的skill指令"
        )
        return skill_context_text

