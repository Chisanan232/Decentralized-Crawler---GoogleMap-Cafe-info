import logging
import getpass


class LogLevel:

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:

    _logger_obj = None

    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __new__(cls, *args, **kwargs):
        if cls._logger_obj is None:
            cls._logger_obj = super(Logger, cls).__new__(cls)
        return cls._logger_obj

    def __init__(self, log_level, debug_log_file=None):
        user = getpass.getuser()
        self.logger = logging.getLogger(user)
        self.logger.setLevel(log_level)

        message_format = '%(asctime)s - %(levelname)s : %(message)s'
        formatter = logging.Formatter(message_format)

        if debug_log_file is not None:
            # global filehandler    # Assign a variable "filehandler" as a global variable
            filehandler = logging.FileHandler(debug_log_file, mode="a+", encoding="utf-8")
            filehandler.setLevel(log_level)
            filehandler.setFormatter(formatter)
            self.logger.addHandler(filehandler)

        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        self.logger.addHandler(streamhandler)

    def debug_level_log(self, msg):
        self.logger.debug(msg)

    def info_level_log(self, msg):
        self.logger.info(msg)

    def warning_level_log(self, msg):
        self.logger.warning(msg)

    def error_level_log(self, msg):
        self.logger.error(msg)

    def critical_level_log(self, msg):
        self.logger.critical(msg)

    def customize_log(self, level, msg):
        self.logger.log(level, msg)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def disable(self):
        logging.disable(50)

