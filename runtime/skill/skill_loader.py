"""发现 Skill、解析 Frontmatter、加载完整内容"""
from pathlib import Path
from typing import Any

import yaml

from runtime.skill import SkillRegistry, SkillMetadata


class SkillLoader:
    """
    Skill 加载器

    负责发现Skill,解析元数据并加载完整Skill内容
    """
    def __init__(self, skill_dir: Path):
        self._skill_dir = Path(skill_dir)
        self.registry = SkillRegistry()

    def discover_skills(self) -> list[SkillMetadata]:
        """
        扫描skill 根目录，发现并注册所有skill

        目前只解析SKILL.md中的YAML Frontmatter
        不加载完整MarkDown正文
        """
        if not self._skill_dir.is_dir():
            raise FileNotFoundError(
                f"没有找到skill路径:{self._skill_dir}"
            )
        # 使用临时注册表，避免扫描失败留下不完整的注册表
        new_registry = SkillRegistry()
        discovered_skills = []

        for skill_dir in sorted(self._skill_dir.iterdir()):
            #只处理目录
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"

            #没有SKILL.md 的目录不视为有效Skill
            if not skill_file.is_file():
                continue

            metadata = self._parse_skill_metadata(
                skill_dir,
                skill_file
            )
            new_registry.register(metadata)
            discovered_skills.append(metadata)

            # 全部扫描成功后再替换注册表
        self.registry = new_registry

        return discovered_skills
    def _parse_skill_metadata(
            self,
            skill_dir: Path,
            skill_file: Path
    )-> SkillMetadata:
        """
        解析单个SKILL.md的YAML Frontmatter
        """
        frontmatter = self._read_frontmatter(skill_file)

        try:
            data : Any = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            raise ValueError(
                f"无效的YAML Frontmatter{skill_file}:{e}"
            )
        if not isinstance(data, dict):
            raise ValueError(
                f"解析结果必须是字典:{skill_file}"
            )
        name = data.get("name")
        description = data.get("description")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"缺少或无效‘name’ {skill_file}"
            )

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                f"缺少或无效 'description' {skill_file}"
            )
        return SkillMetadata(
            name=name,
            description=description,
            skill_dir=skill_dir,
            skill_file=skill_file
        )

    @staticmethod
    def _read_frontmatter(skill_file: Path) -> str:
        """
        只读取YAML Frontmatter ,不读取Markdown正文
        """
        with skill_file.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            first_line = file.readline()

            if first_line.strip() != "---":
                raise ValueError(
                    f"元数据的格式错误: {skill_file}"
                )
            lines = []
            for line in file:
                if line.strip() == "---":
                    return "".join(lines)

                lines.append(line)

            raise ValueError(
                f"元数据的格式错误: {skill_file}"
            )


    def load_skill(self,name: str) -> str:
        """
        根据SKill名称加载完整的SKILL.md内容
        """
        #1.从注册表中获取skill元数据
        metadata = self.registry.get(name)
        #2.根据元数据中的文件路径读取完整内容
        content = metadata.skill_file.read_text(
            encoding="utf-8-sig",
        )

        return content





