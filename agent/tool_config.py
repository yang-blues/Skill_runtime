from runtime.tool.tool_policy import ToolPolicy, ToolType


TOOL_POLICY_CONFIG = {
    "load_skill": ToolPolicy(
        tool_type=ToolType.SAFE,
        timeout=10,
        max_attempts=3,
        retryable=True,
    ),

    "read_resource": ToolPolicy(
        tool_type=ToolType.SAFE,
        timeout=20,
        max_attempts=3,
        retryable=True,
    ),

    "run_script": ToolPolicy(
        tool_type=ToolType.SENSITIVE,
        timeout=15,
        max_attempts=1,
        retryable=False,
    ),
    "list_skills": ToolPolicy(
        tool_type=ToolType.SAFE,
        timeout=10,
        max_attempts=3,
        retryable=True,
    ),

    "refresh_skills": ToolPolicy(
        tool_type=ToolType.SAFE,
        timeout=20,
        max_attempts=3,
        retryable=True,
    ),
    "unload_skill": ToolPolicy(
        tool_type=ToolType.SENSITIVE,
        timeout=15,
        max_attempts=1,
        retryable=False,
    ),
    "reload_skill": ToolPolicy(
        tool_type=ToolType.SENSITIVE,
        timeout=15,
        max_attempts=1,
        retryable=False,
    ),

}

