from logging.config import dictConfig
from pathlib import Path

from app.core.logging_filters import RequestIdFilter
from app.core.settings import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "filters": {
        "request_id": {
            "()": RequestIdFilter,
        },
    },

    "formatters": {
        "default": {
            "format": settings.LOG_FORMAT,
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL_CONSOLE,
            "formatter": "default",
            "filters": ["request_id"],   # <== ici on rattache le filtre au handler
        },

        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL_FILE,
            "formatter": "default",
            "filename": settings.LOG_FILE,
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["request_id"],   # <== ici aussi
        },
    },

    "root": {
        "level": settings.log_level,
        "handlers": ["console", "file"],
    },
}


def setup_logging() -> None:
    """ Configure le système de logging global de l'application"""
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True) 
    #Évite que RotatingFileHandler échoue au démarrage si logs/ n'existe pas.

    dictConfig(LOGGING_CONFIG)


