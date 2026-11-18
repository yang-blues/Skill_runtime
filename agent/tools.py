from langchain.tools import tool

from runtime.resource_reader import ResourceReader
from runtime.script_runner import ScriptRunner
from runtime.skill import SkillLoader


def create_runtime_tools(skill_loader:SkillLoader,
                         resource_reader:ResourceReader,
                         script_runner:ScriptRunner) :
    @tool
    def load_skill(skill_name:str) -> str:
        """
        加载指定 Skill 的完整说明文档。

        Args:
            skill_name: Skill 的名称，必须是已注册的 Skill 名称。

        Returns:
            Skill 的完整 SKILL.md 内容，包括 Frontmatter 和 Markdown 正文。
        """
        return skill_loader.load_skill(skill_name)

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

    return [load_skill, read_resource, run_script]

