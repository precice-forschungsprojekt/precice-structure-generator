from pathlib import Path
from termcolor import colored
from datetime import datetime

class Logger:
    def __init__(self) -> None:
        """ Custom logger"""
        self.root_generated = Path(__file__).parent

    def _log(self, msg: str, level: str, color: str, symbol: str) -> None:
        """
        Internal method to log a message with a specified level, color, and symbol.
        :param msg: The log message.
        :param level: The log level (e.g., INFO, SUCCESS, ERROR).
        :param color: The color for terminal output.
        :param symbol: Symbol to display alongside the log.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"{timestamp} {symbol} [{level}] {msg}"
        print(colored(formatted_msg, color))

    def success(self, msg: str) -> None:
        """Logs a success message."""
        self._log(msg, "SUCCESS", "green", "✅")

    def info(self, msg: str) -> None:
        """Logs an informational message."""
        self._log(msg, "INFO", "blue", "ℹ️")

    def warning(self, msg: str) -> None:
        """Logs a warning message."""
        self._log(msg, "WARNING", "yellow", "⚠️")

    def error(self, msg: str) -> None:
        """Logs an error message."""
        self._log(msg, "ERROR", "red", "❌")
