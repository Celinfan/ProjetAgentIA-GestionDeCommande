from logging.config import dictConfig
from app.core.settings import settings
from app.core.logging_filters import RequestIdFilter

# initialisation avec les variables d'environnement
settings.debug

"""
LOGGING_CONFIG paramètre :
Niveau log    |   Console    |   Fichier
DEBUG	      |   ❌ non    |   ✅ oui
INFO	      |   ✅ oui    |   ✅ oui
WARNING+	  |   ✅ oui    |   ✅ oui

à inverser en prod (INFO fichier, WARNING console par ex)

utiliser : logging.config.dictConfig(LOGGING_CONFIG) 
( mais ❌ IL NE FAUT PAS appeler logging.basicConfig() en même temps sinon résultats imprévisibles !)
basicConfig = rapide, jetable, pédagogique -> pas en entreprise !!!
dictConfig = config sérieuse, pro, maîtrisée
"""

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
    """
    Configure le logging global de l'application
    """
    dictConfig(LOGGING_CONFIG)


