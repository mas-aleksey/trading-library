import logging
import sys
import traceback
from logging import config as logger_config
from pathlib import Path

from jsonformatter import JsonFormatter as BaseJsonFormatter
from yaml import safe_load as yaml_load


class EndpointLogFilter(logging.Filter):
    def __init__(self, path: str, name: str = "") -> None:
        super().__init__(name)
        self.path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self.path) == -1


def init_logger(file_path: Path = None) -> logging.Logger:
    if file_path is None:
        file_path = Path(__file__).parent / "logging.yaml"
    with Path(file_path).open() as f:
        logger_config.dictConfig(yaml_load(f.read()))
    return logging.getLogger("app")


class JsonFormatter(BaseJsonFormatter):
    LOG_ADD_RECORDS = {
        # "trace_id": lambda: str(trace_id.get()),
        "traceback": lambda: (
            traceback.format_exc() if sys.exc_info() != (None, None, None) else None
        ),
    }

    def __init__(self, *args, **kwargs):
        if (record_custom_attrs := kwargs.get("record_custom_attrs", None)) is None:
            record_custom_attrs = self.LOG_ADD_RECORDS
        else:
            record_custom_attrs.update(self.LOG_ADD_RECORDS)
        kwargs["record_custom_attrs"] = record_custom_attrs

        super().__init__(*args, **kwargs)
