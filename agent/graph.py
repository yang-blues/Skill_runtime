from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from agent.state import AgentState
from agent.prompts import SYSTEM_PROMPT



def create_agent_graph(llm, runtime_tools):
    # 初始化 Runnable，只执行一次
    llm_with_tools = llm.bind_tools(runtime_tools)
    agent_runnable = SYSTEM_PROMPT | llm_with_tools

    # Agent 决策节点
    def agent_node(state: AgentState):
        response = agent_runnable.invoke({
            "messages": state["messages"],
            "loaded_skills": state["loaded_skills"]
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




