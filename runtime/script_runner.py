"""按需执行scripts/目录中的Python脚本"""
import subprocess
import sys
from pathlib import Path

from runtime.skill import SkillRegistry


class ScriptRunner:
    """
    SKill Python脚本执行器

    负责安全的定位并执行 skill scripts 目录中的Python脚本
    """
    def __init__(self,
                 registry: SkillRegistry,
                 timeout: int = 10, #脚本执行的超时时间
                 max_output_chars: int = 10000 #截取后10000个字符串
                 ):
        self.registry = registry
        self.timeout = timeout
        self.max_output_chars = max_output_chars


    def run_script(
            self,
            skill_name: str,
            script_path: str,
            arguments: list[str] | None = None,) -> str:
        """
        执行指定 Skill 中的Python脚本

        script_path 相对于skill的scripts目录。
        argument 是传递给脚本的命令行参数
        """
        #1.获取Skill元数据
        metadata = self.registry.get(skill_name)
        #2.获取scripts 根目录
        scripts_dir = (
            metadata.skill_dir / "scripts"
        ).resolve()
        if not scripts_dir.is_dir():
            raise FileNotFoundError(
                f"Scripts文件夹没有找到:{scripts_dir} "
            )
        #3.校验脚本路径
        if not isinstance(script_path,str) or not script_path.strip():
            raise ValueError("Script路径不能被解析")

        relative_path = Path(script_path)

        if relative_path.is_absolute():
            raise ValueError(
                f"相对路径不符合规范:{relative_path} "
            )
        if relative_path.suffix.lower() != ".py":
            raise ValueError(
                f"仅仅Python脚本才被允许：{script_path}"
            )
        #4.解析目标路径
        target_path = (
            scripts_dir / relative_path
        ).resolve()

        #5.防止路径穿越和符号链接逃逸
        if not target_path.is_relative_to(scripts_dir):
            raise ValueError(
                f"Script 路径是在scripts文件夹之外：{script_path}"
            )
        #6.确认脚本存在
        if not target_path.is_file():
            raise FileNotFoundError(
                f"Script没有找到:{target_path} "
            )

        #7.校验参数,满足subprocess命令列表接口，不是因为Python脚本本身只能接受List[str]
        if arguments is None:
            arguments = []
        if not isinstance(arguments,list):
            raise ValueError("Arguments必须是list")

        if not all(isinstance(arg,str)for arg in arguments):
            raise ValueError("所有的参数必须是字符串")

        #8.构建命令，也可以传字符串设置shell=True,有注入风险不推荐
        command = [
            sys.executable, #使用当前项目的python解释器
            str(target_path),
            *arguments #传入的参数必须和脚本的参数顺序严格对齐，sys拿到的参数全部都是字符串，由脚本自己做类型转换
        ]
        #9.执行脚本
        try:
            result = subprocess.run(
                command,#要执行的命令
                cwd=scripts_dir,#指定子进程的工作目录
                capture_output=True,#捕获子进程的标准输出和标准错误
                text=True,#让stdout/stderr返回字符串str,而不是原始bytes字节流
                encoding="utf-8",#用utf-8编码把字节流解码成字符串
                errors="replace",#解码的时候出现错误的策略
                timeout=self.timeout,#脚本执行的超时时间
                check=False#不抛异常
            )
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(
                f"脚本执行超时:{script_path}"
            ) from e
        #10.检查执行结果
        # result.returncode 退出码：0=成功，非0=失败
        # result.stdout       命令正常输出
        # result.stderr        命令错误输出

        if result.returncode != 0:
            error_message = result.stderr.strip()

            raise RuntimeError(
                f"脚本执行失败"
                f"(exit code:{result.returncode}):\n"
                f"{error_message[:self.max_output_chars]}"
            )

        #11.限制返回给上层的输出长度
        return result.stdout[:self.max_output_chars]
