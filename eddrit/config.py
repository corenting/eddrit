from environs import Env

env = Env()
env.read_env()

DEBUG: bool = env.bool("DEBUG", False)  # type: ignore
PROXY_COUNT: int = env.int("PROXY_COUNT", 1)  # type: ignore
PROXY_ENABLED: bool = env.bool("PROXY_ENABLED", False)  # type: ignore
