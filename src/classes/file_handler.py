import re
import logging.handlers


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        # self.suffix = "%Y%m%d"
        # self.extMatch = re.compile(r"^\d{4}\d{2}\d{2}$")
        self.interval = 60 * 60 * 24 # one day
        self.suffix = "%Y-%m-%d"
        self.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}(\.\w+)?$")
