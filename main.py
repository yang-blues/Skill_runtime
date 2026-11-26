from langchain_core.messages import HumanMessage

from agent.graph import create_agent_graph





graph = create_agent_graph()

res = graph.invoke({"messages":[HumanMessage(content="查询一下你有哪些技能")],"loaded_skills":" "})

print(res)
