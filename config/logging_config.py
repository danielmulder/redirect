import logging

def configure_logging(global_level=logging.ERROR, specific_loggers=None):
    """
    Configure global logging and optionally specific loggers.

    Parameters:
    - global_level (int): The global logging level.
    - specific_loggers (dict): A dictionary where keys are robots_logger names and values are log levels.

    Returns:
    - Logger: The root robots_logger for the module.
    """
    # Globale configuratie
    logging.basicConfig(
        level=global_level,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    # Specifieke loggers configureren
    if specific_loggers:
        for logger_name, logger_level in specific_loggers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(logger_level)

    # Return de root robots_logger van het huidige script/module
    return logging.getLogger(__name__)

