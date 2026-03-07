"""
CyberSentinel - Logger Module
==============================
Configures and provides a centralized logging system with both
console (colored) and file output handlers.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from colorama import init as colorama_init, Fore, Style


# Initialize colorama for Windows terminal color support
colorama_init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """
    Custom log formatter that adds color to console output
    based on log level for better readability.
    """

    # Map log levels to colors
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Apply color formatting to the log level name."""
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "data/cybersentinel.log",
    max_file_size: int = 5_242_880,
    backup_count: int = 3,
) -> None:
    """
    Set up the root logger with console and file handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to the log file (relative to project root).
        max_file_size: Maximum size of a single log file in bytes.
        backup_count: Number of rotated log files to keep.
    """
    # Resolve log file path relative to project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    log_path = os.path.join(project_root, log_file)

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Get the root logger
    root_logger = logging.getLogger("cybersentinel")
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid adding duplicate handlers if setup_logging is called multiple times
    if root_logger.handlers:
        return

    # ---- Console Handler (colored output) ----
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = ColoredFormatter(
        fmt="%(asctime)s │ %(levelname)-18s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # ---- File Handler (rotating log files) ----
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger that is a child of the 'cybersentinel' root logger.

    Args:
        name: Name for the logger (typically the module name).

    Returns:
        A configured logging.Logger instance.

    Usage:
        logger = get_logger("sniffer")
        logger.info("Packet captured")
    """
    return logging.getLogger(f"cybersentinel.{name}")
