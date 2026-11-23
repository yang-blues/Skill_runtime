from pathlib import Path

from langchain_core.messages import HumanMessage

from agent.graph import create_agent_graph
from agent.tools import create_runtime_tools
from llm_model.all_llm import llm
from runtime.resource_reader import ResourceReader
from runtime.script_runner import ScriptRunner
from runtime.skill import  SkillLoader

skill_dir = Path(r"D:\ipython\Skill_runtime\skills")
#创建SkillLoader实例
skill_loader = SkillLoader(skill_dir)
#发现并且注册skill
skill_loader.discover_skills()
# 创建其他 Runtime 模块
resource_reader = ResourceReader(skill_loader.registry)
script_runner = ScriptRunner(skill_loader.registry)

#创建工具
tools = create_runtime_tools(skill_loader, resource_reader, script_runner)


graph = create_agent_graph(llm, tools,skill_loader.registry)

res = graph.invoke({"messages":[HumanMessage(content="查询一下你有哪些技能")],"loaded_skills":" "})

print(res)
