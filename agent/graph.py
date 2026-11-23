"""
静态组件：Runnable、LLM、工具绑定，在 Graph 创建时初始化。
动态数据：Catalog、已加载 Skill、Skill Context，在每次节点执行时读取。
"""

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT
from runtime.skill import SkillRegistry
from runtime.skill.skill_catalog import build_skill_catalog


def create_agent_graph(llm, runtime_tools,skill_registry:SkillRegistry):
    # 初始化 Runnable，只执行一次
    llm_with_tools = llm.bind_tools(runtime_tools)
    agent_runnable = SYSTEM_PROMPT | llm_with_tools
    # Agent 决策节点
    def agent_node(state: AgentState):
        #1.获取当前已经加载的skill名称
        loaded_skills = state.get("loaded_skills",[])
        #2.获取当前已经加载的skill完整内容
        skill_context = state.get("skill_context",{})

        # 3. 动态构建当前 Skill Catalog
        skill_catalog = build_skill_catalog(skill_registry)
        # 4.格式化skill名称
        loaded_skills_text = (
            "\n".join(f"-{name}" for name in loaded_skills)
            if loaded_skills
            else "当前没有已加载的Skill"
        )
        # 5.格式化Skill文档
        skill_context_text = (
            "\n\n".join(
                f"## Skill:{name}\n{content}"
                for name, content in skill_context.items()
            )
            if skill_context
            else "当前没有已加载的skill指令"
        )

        response = agent_runnable.invoke({
            "messages": state["messages"],
            "loaded_skills": loaded_skills_text,
            "skill_context": skill_context_text,
            "skill_catalog": skill_catalog,
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




