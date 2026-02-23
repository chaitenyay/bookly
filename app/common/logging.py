import json
import logging
from contextvars import ContextVar
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def clear_request_id() -> None:
    _request_id_ctx.set(None)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "error_code": getattr(record, "error_code", None),
            "error_message": getattr(record, "error_message", None),
            "error_details": getattr(record, "error_details", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    logger = logging.getLogger("bookly")
    if logger.handlers:
        return logger

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    formatter = JsonFormatter()
    context_filter = RequestContextFilter()

    app_handler = TimedRotatingFileHandler(
        filename=str(Path(log_dir) / "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        utc=True,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    app_handler.addFilter(context_filter)

    error_handler = TimedRotatingFileHandler(
        filename=str(Path(log_dir) / "error.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        utc=True,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(context_filter)

    logger.setLevel(logging.INFO)
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.propagate = False
    return logger
