from environs import Env

from eddrit.constants import SpoofedClient

env = Env()
env.read_env()

DEBUG: bool = env.bool("DEBUG", default=False)
LOG_LEVEL: str = env.str("LOG_LEVEL", default="WARNING")
SPOOFED_CLIENT: SpoofedClient = env.enum(
    "SPOOFED_CLIENT",
    type=SpoofedClient,
    ignore_case=True,
    default=SpoofedClient.OFFICIAL_ANDROID_APP.value,
)
