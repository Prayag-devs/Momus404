"""
momus404 — app.core.logging
Structured logging configuration for backend components.
"""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger("momus404")
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers if re-initialized
    if not root_logger.handlers:
        root_logger.addHandler(handler)
        try:
            from pathlib import Path
            log_file = Path("storage/backend.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_h = logging.FileHandler(str(log_file), encoding="utf-8")
            file_h.setFormatter(formatter)
            root_logger.addHandler(file_h)
        except Exception:
            pass


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"momus404.{name}")
