"""
静态组件：Runnable、LLM、工具绑定，在 Graph 创建时初始化。
动态数据：Catalog、已加载 Skill、Skill Context，在每次节点执行时读取。
"""

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from runtime.skill import SkillRegistry
from runtime.context.context_builder import ContextBuilder


def create_agent_graph(llm, runtime_tools,skill_registry:SkillRegistry):
    # 初始化 Runnable，只执行一次
    llm_with_tools = llm.bind_tools(runtime_tools)
    agent_runnable = SYSTEM_PROMPT | llm_with_tools
    context_builder = ContextBuilder(skill_registry)
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
    builder.add_node("tools",ToolNode(runtime_tools))

    builder.add_edge(START,"agent")
    builder.add_conditional_edges(
        "agent",
        tools_condition,)
    builder.add_edge("tools","agent")

    return builder.compile()




