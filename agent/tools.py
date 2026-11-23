import json

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

from agent.state import AgentState
from runtime.resource_reader import ResourceReader
from runtime.script_runner import ScriptRunner
from runtime.skill import SkillLoader


def create_runtime_tools(skill_loader:SkillLoader,
                         resource_reader:ResourceReader,
                         script_runner:ScriptRunner) :
    @tool
    def load_skill(skill_name:str,runtime:ToolRuntime) -> Command :
        """
        加载指定 Skill 的完整说明文档。

        Args:
            skill_name: Skill 的名称，必须是已注册的 Skill 名称。

        Returns:
            更新AgentState,并返回简短的工具执行结果
        """
        #1.记载Skill 完整文档
        content = skill_loader.load_skill(skill_name)
        #2.返回Command 更新AgentState
        return Command(
            update={
                "loaded_skills":[skill_name],
                "skill_context":{
                    skill_name: content
                },
                "messages":ToolMessage(
                    content=f"Skill'{skill_name}'已加载成功",
                    tool_call_id=runtime.tool_call_id,
                )

            }
        )

    @tool
    def read_resource(skill_name :str,resource_path :str)-> str:
        """
        读取指定 Skill 的参考资料文件。

        Args:
            skill_name: Skill 的名称，必须是已注册的 Skill 名称。
            resource_path: 相对于该 Skill 的 references 目录的文件路径，
                支持子目录，例如 examples/demo.md。

        Returns:
            读取到的文件文本内容。
        """
        return resource_reader.read_resource(skill_name, resource_path)

    @tool
    def run_script(skill_name: str,
            script_path: str,
            arguments: list[str] | None = None,):
        """
        执行指定 Skill 中的 Python 脚本。

        Args:
            skill_name: Skill 的名称，必须是已注册的 Skill 名称。
            script_path: 相对于该 Skill 的 scripts 目录的 Python 脚本路径。
            arguments: 传递给脚本的命令行参数列表，每个参数必须是字符串。
                不需要传递参数时可以省略。

        Returns:
            脚本标准输出内容。
        """
        return script_runner.run_script(skill_name, script_path, arguments)

    @tool
    def list_skills() -> str :
        """
        获取当前Runtime中所有已经注册的Skill

        Returns:
            已注册Skill的名称和描述
        """
        skills = skill_loader.registry.list_skills()

        if not skills:
            return "当前没有已经注册的skill。"
        result = [
            {
                "name": skill.name,
                "description": skill.description,
            }
            for skill in skills
        ]
        #Tool的返回值会被封装成为ToolMessage.这里将数据序列化为JSON字符串，模型更容易理解结构信息
        return json.dumps(result,ensure_ascii=False,indent=2)

    return [load_skill, read_resource, run_script, list_skills]

