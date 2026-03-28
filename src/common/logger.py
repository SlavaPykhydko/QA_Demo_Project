import logging
import os
import sys
from contextvars import ContextVar
from datetime import datetime


_LOG_CONTEXT: ContextVar[dict] = ContextVar("log_context", default={})
_CONTEXT_KEYS = ("env", "worker", "test_nodeid", "user_type", "request_id")


def set_log_context(**kwargs):
    current = dict(_LOG_CONTEXT.get())
    for key, value in kwargs.items():
        if value is None:
            current.pop(key, None)
        else:
            current[key] = value
    _LOG_CONTEXT.set(current)


def clear_log_context(*keys):
    if not keys:
        _LOG_CONTEXT.set({})
        return

    current = dict(_LOG_CONTEXT.get())
    for key in keys:
        current.pop(key, None)
    _LOG_CONTEXT.set(current)


def get_log_context():
    """Return a copy of current structured logging context."""
    return dict(_LOG_CONTEXT.get())


class _ContextFilter(logging.Filter):
    def filter(self, record):
        context = _LOG_CONTEXT.get()
        for key in _CONTEXT_KEYS:
            value = context.get(key, "-")
            setattr(record, key, value)

        # Append a blank separator line after each entry so logs are easier
        # to scan in console, log files, and the Allure `log` attachment.
        # Runs at logger level → affects ALL handlers including pytest capture.
        if isinstance(record.msg, str) and not record.msg.endswith("\n"):
            record.msg = record.msg + "\n"

        return True


def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "env=%(env)s worker=%(worker)s test=%(test_nodeid)s "
            "user=%(user_type)s req=%(request_id)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logger.addFilter(_ContextFilter())

        #set up output in stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        #set up output in file
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 4. Handler for logging into file
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_name = f"{log_dir}/automation_{current_date}.log"
        file_handler = logging.FileHandler(log_file_name, encoding='utf-8')

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger