import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    discord_webhook: str | None
    log_level: str
    host: str
    port: int
    crashes_dir: str
    logs_dir: str
    symbols_dir: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            discord_webhook=os.getenv("DISCORD_WEBHOOK"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            crashes_dir=os.getenv("CRASHES_DIR", "crashes"),
            logs_dir=os.getenv("LOGS_DIR", "logs"),
            symbols_dir=os.getenv("SYMBOLS_DIR", "symbols"),
        )


config = Config.from_env()