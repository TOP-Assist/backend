"""Logging configuration that provides a template for all submodules."""

from logging.config import dictConfig


def configure_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s %(levelname)s %(name)s: %(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "standard",
                },
            },
            "root": {
                "level": "WARNING",
                "handlers": ["console"],
            },
            "loggers": {
                "backend": {
                    "level": level,
                    "handlers": [],
                    "propagate": True,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": [],
                    "propagate": True,
                },
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": [],
                    "propagate": True,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": [],
                    "propagate": True,
                },
            },
        }
    )
