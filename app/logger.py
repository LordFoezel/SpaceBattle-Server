import logging
import inspect
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dataclasses import asdict, is_dataclass


class Logger:
    """
    Advanced logger that supports strings, dicts, lists, tuples, and objects.
    Logs to console and rotating file.
    """

    def __init__(
        self,
        name: str = "SpaceBattle",
        log_file: str = "logs/app.log",
        max_bytes: int = 5_000_000,
        backup_count: int = 5,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s -> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def _get_origin(self) -> str:
        """Return the filename and function where the log was called."""
        frame = inspect.stack()[2]
        filename = frame.filename.split("/")[-1]
        func_name = frame.function
        return f"{filename}:{func_name}"

    def _format_message(self, message):
        """Format dicts, lists, or objects as JSON; strings stay unchanged."""
        try:
            # Dataclasses → dict
            if is_dataclass(message):
                message = asdict(message)

            # Dicts, lists, tuples, objects → JSON
            if isinstance(message, (dict, list, tuple)):
                return json.dumps(message, indent=2, ensure_ascii=False)
            # Fallback: try to serialize object attributes
            elif hasattr(message, "__dict__"):
                return json.dumps(message.__dict__, indent=2, ensure_ascii=False)
            else:
                return str(message)
        except Exception as e:
            return f"[Unserializable object: {e}] {repr(message)}"

    def log_info(self, message):
        origin = self._get_origin()
        formatted = self._format_message(message)
        self.logger.info(f"{origin} -> {formatted}")

    def log_warning(self, message):
        origin = self._get_origin()
        formatted = self._format_message(message)
        self.logger.warning(f"{origin} -> {formatted}")

    def log_error(self, message):
        origin = self._get_origin()
        formatted = self._format_message(message)
        self.logger.error(f"{origin} -> {formatted}")