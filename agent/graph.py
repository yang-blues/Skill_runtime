"""
静态组件：Runnable、LLM、工具绑定，在 Graph 创建时初始化。
动态数据：Catalog、已加载 Skill、Skill Context，在每次节点执行时读取。
"""
from pathlib import Path

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from agent.tool_config import TOOL_POLICY_CONFIG
from agent.tools import create_runtime_tools
from llm_model.all_llm import llm
from runtime.resource_reader import ResourceReader
from runtime.script_runner import ScriptRunner
from runtime.skill import SkillLoader
from runtime.context.context_builder import ContextBuilder
from runtime.tool.tool_node_factory import create_tool_node
from runtime.tool.tool_registy import ToolPolicyRegistry


def create_agent_graph():
    # 初始化，只执行一次
    skill_dir = Path(r"D:\ipython\Skill_runtime\skills")
    #1.skill的初始化操作
    #1.1创建SkillLoader实例
    skill_loader = SkillLoader(skill_dir)
    #1.2发现并且注册skill
    skill_loader.discover_skills()
    #1.3初始化其他 Skill 模块
    resource_reader = ResourceReader(skill_loader.registry)
    script_runner = ScriptRunner(skill_loader.registry)
    # 创建工具
    runtime_tools = create_runtime_tools(skill_loader, resource_reader, script_runner)

    #2.初始化Runnable
    llm_with_tools = llm.bind_tools(runtime_tools)
    agent_runnable = SYSTEM_PROMPT | llm_with_tools

    #3.初始化上下文构造器
    context_builder = ContextBuilder(skill_loader.registry)

    #4.初始化工具策略注册表
    tool_policy_registry = ToolPolicyRegistry()
    #4.1将工具和对应策略注册到注册表
    tool_policy_registry.initialize_tool_policy_registry(runtime_tools,TOOL_POLICY_CONFIG)


    # Agent 决策节点
    def agent_node(state: AgentState):
        snapshot = context_builder.build(state)

        response = agent_runnable.invoke({
            "messages": list(snapshot.messages),
            "loaded_skills": snapshot.loaded_skills,
            "skill_context": snapshot.skill_context,
            "skill_catalog": snapshot.skill_catalog,
        })

        return {"messages": [response]}

    # 构建图
    builder = StateGraph(AgentState)

    builder.add_node("agent",agent_node)
    builder.add_node("tools",create_tool_node(runtime_tools,tool_policy_registry))

    builder.add_edge(START,"agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,)
    builder.add_edge("tools","agent")

    return builder.compile()




