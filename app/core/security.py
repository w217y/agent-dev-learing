from app.config import settings

DANGEROUS_KEYWORDS = [
    "删除所有",
    "清空",
    "drop table",
    "truncate",
    "修改所有",
    "把所有",
    "绕过审批",
    "不用审批",
    "直接发送",
    "伪造",
    "关闭日志",
    "禁用 trace",
    "api key",
    "secret key",
    "数据库密码",
    "身份证号",
    "银行卡",
    "登录 token",
    "管理员权限",
]

ALLOWED_FILE_TYPES = {"pdf", "txt", "md", "markdown"}


def validate_user_input(text: str) -> None:
    if not text or not text.strip():
        raise ValueError("输入不能为空")
    
    if len(text) > settings.max_input_length:
        raise ValueError("输入过长。")
    
    lowered = text.lower()

    for keyword in DANGEROUS_KEYWORDS:
        if keyword.lower() in lowered:
            raise ValueError("检测到高风险操作，已拒绝执行。")
        

def validate_file_type(filename: str) -> None:
    file_type = filename.split(".")[-1].lower()

    if file_type not in ALLOWED_FILE_TYPES:
        raise ValueError(f"不支持的文件类型：{file_type}")