import os
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env(filename: str = ".env") -> None:
    """将项目根目录下的 .env 读入环境变量（已存在的同名环境变量不覆盖）。

    无需第三方依赖。文件不存在时静默跳过——这样在未配置密钥的环境里
    程序依然能启动（发送验证码会自动回退到控制台打印，便于本地调试）。
    """
    env_path = _PROJECT_ROOT / filename
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
