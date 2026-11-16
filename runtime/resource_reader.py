"""阅读资源文件"""
from pathlib import Path

from runtime.skill import SkillRegistry


class ResourceReader:
    """
    skill参考资料读取器

    负责按需读取skill references目录中的文件
    """
    def __init__(self,registry:SkillRegistry):
        self.registry = registry

    def read_resource(
            self,
            skill_name :str,
            resource_path :str)-> str:
        """
        根据skill名称和相对路径读取参考资料

        resource_path 相对于skill的references目录
        """
        #1.获取Skill元数据
        metadata = self.registry.get(skill_name)

        #2.获取reference根目录
        references_dir = (metadata.skill_dir / "references").resolve()

        if not references_dir.is_dir():
            raise FileNotFoundError(f"当前skill没有 {references_dir} 这个文件夹")
        #3.校验传入路径是否为空格或者绝对路径

        relative_path = Path(resource_path)
        if not resource_path.strip() or relative_path.is_absolute():
            raise ValueError(
                f"传入的资源路径不符合规范:{relative_path}"
            )

        #4.解析完整路径 path.resolve()将路径转换为规范的绝对路径
        target_path = (
            references_dir / relative_path
        ).resolve()

        #5.防止路径穿越和符号链接逃逸
        if not target_path.is_relative_to(references_dir):
            raise ValueError(
                f"资源路径{target_path}没有在我们的 references目录之下"
            )
        #6.确认目标是文件
        if not target_path.is_file():
            raise FileNotFoundError(
                f"资源文件没有找到:{target_path}"
            )
        #7.读取完整文本
        return target_path.read_text(
            encoding="utf-8"
        )


