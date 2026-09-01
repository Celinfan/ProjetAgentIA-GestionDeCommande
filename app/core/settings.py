"""Configuration globale de l'application"""

import os

class Settings:
    """Configuration de l'application."""
    DEFAULT_ENV = "dev"  # dev | prod
    DEFAULT_DEBUG = True
   
    LOG_FILE="logs/app.log"
    LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s : %(message)s"


    def __init__(self) -> None:
        self.env = os.getenv("APP_ENV", self.DEFAULT_ENV)
        self.debug = self._get_bool("APP_DEBUG", self.DEFAULT_DEBUG)

        self.log_level = (
            "DEBUG"
            if self.debug
            else os.getenv("APP_LOG_LEVEL", "INFO")
        )

        self.LOG_LEVEL_CONSOLE = (
            "DEBUG" if self.debug else "INFO"
        )
        self.LOG_LEVEL_FILE = (
            "INFO" if self.debug else "WARNING"
        )

    @staticmethod
    def _get_bool(name: str, default: bool) -> bool:
        """Lit une variable d'environnement booléenne."""
        value = os.getenv(name)

        if value is None:
            return default

        return value.lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

# instance unique
settings = Settings()
