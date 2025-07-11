import logging
import sys

class Logger:
    def __init__(self, name: str, level: str = "INFO") -> None:
        """
        Initializes the custom logger.

        Args:
            name (str): Name of the logger.
            level (str): Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level(level))

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _get_log_level(self, level: str):
        """
        Converts a string log level to the logging module's constant.

        Args:
            level (str): String log level.

        Returns:
            int: Corresponding logging level constant.
        """
        level = level.upper()
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level, logging.INFO)

    def get_logger(self):
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger