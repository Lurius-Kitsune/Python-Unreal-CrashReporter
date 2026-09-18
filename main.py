import logging
import os
from app import App
from config import config

os.makedirs(config.logs_dir, exist_ok=True)

logging.basicConfig(
    level=config.log_level.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(config.logs_dir, "crash_reporter.log"), encoding="utf-8"),
    ],
)


def Main():
    _appInstance = App(config.discord_webhook,config.crashes_dir, config.port)
    _appInstance.run()

Main()