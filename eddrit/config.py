from environs import Env

env = Env()
env.read_env()

DEBUG: bool = env.bool("DEBUG", default=False)
LOG_LEVEL: str = env.str("LOG_LEVEL", default="WARNING")

VALKEY_URL: str = env.str("VALKEY_URL")
PROXY: str | None = env.str("PROXY", default=None)
