from environs import Env

env = Env()
env.read_env()

DEBUG: bool = env.bool("DEBUG", False)  # type: ignore
