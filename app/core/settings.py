"""
  Configuration globale de l'application
"""
class Settings:
    """
    Sans variable d'environnement :
    env = "dev"
    debug = True
    log_level = "DEBUG"

    Avec variables d'environnement :
    APP_ENV=prod
    APP_DEBUG=false
    APP_LOG_LEVEL=INFO
    """

    # environnement
    env: str = "dev" # dev | prod
    debug: bool = True
    
    # logging
    LOG_FILE="logs/app.log"
    # log_level: str = "DEBUG" # DEBUG | INFO | WARNING | ERROR
    log_level = "DEBUG" if debug else "INFO"
    LOG_LEVEL_CONSOLE = "DEBUG" if debug else "INFO"
    LOG_LEVEL_FILE = "INFO" if debug else "WARNING"
    """
    model_config = {
        "env_prefix": "APP_",
        "case_sensitive": False,
    }
    """
    LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s : %(message)s"

# instance unique
settings = Settings()
