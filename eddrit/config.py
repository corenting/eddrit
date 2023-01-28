from environs import Env

env = Env()
env.read_env()

DEBUG: bool = env.bool("DEBUG", False)
LOG_LEVEL: str = env.str("LOG_LEVEL", "WARNING")
