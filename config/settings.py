import os
import logging
from configparser import ConfigParser
from dotenv import load_dotenv  # Voor .env ondersteuning
from config.secrets import get_db_password, get_api_key
from config.logging_config import configure_logging

# .env laden voor omgevingsvariabelen
load_dotenv()

# Initialize the robots_logger
logger = logging.getLogger(__name__)


def get_config():
    """Lees en retourneer configuratie."""
    config = ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "config.ini")

    # Controleer of het configuratiebestand bestaat
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuratiebestand niet gevonden: {config_path}")

    config.read(config_path)
    return config


def get_mysql_connection_string():
    """Genereer de MySQL-verbindingstring."""
    config = get_config()
    db_pass = get_db_password()
    try:
        user = config['mysql']['user']
        host = config['mysql']['host']
        database = config['mysql']['database']
        return f"mysql+pymysql://{user}:{db_pass}@{host}/{database}"
    except KeyError as e:
        raise KeyError(f"Configuratiefout: ontbrekende sleutel {e} in [mysql] sectie")


def get_db_config():
    """Retourneer databaseconfiguratie als dict."""
    config = get_config()
    db_pass = get_db_password()
    try:
        return {
            "host": config['mysql']['host'],
            "user": config['mysql']['user'],
            "password": db_pass,
            "db": config['mysql']['database'],
            "port": 3306,
        }
    except KeyError as e:
        raise KeyError(f"Configuratiefout: ontbrekende sleutel {e} in [mysql] sectie")


def get_bearer_token():
    """Haal het Bearer Token op uit de omgeving."""
    bearer_token = os.getenv("BEARER_TOKEN")
    if not bearer_token:
        raise EnvironmentError("BEARER_TOKEN is niet ingesteld in de omgeving.")
    return bearer_token


# Initialiseer robots_logger
config = get_config()
logger = configure_logging(
    global_level=config.get("settings", "level", fallback="INFO"),
    specific_loggers={
        "PyUrl": config.get("settings", "pyurl_level", fallback="INFO"),
        "CrawlerController": config.get("settings", "crawler_level", fallback="INFO"),
        "ProcessingController": config.get("settings", "processing_level", fallback="INFO"),
    }
)
