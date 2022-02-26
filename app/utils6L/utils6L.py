"""
Copyright 6L LLC (2021) - See MIT LICENSE

Cross project features or decorators, similar to Spring Aspect-Oriented
Programming(AOP)

https://docs.spring.io/spring-framework/docs/4.3.12.RELEASE/spring-framework-reference/html/aop.html

usage - copy/paste package directory into the project file structure and

Special considerations for the logging setup and decorator
Logger name is defined as an environment variable.

ensure the following statements is added to the rest of the modules.

    import bvb_utils.bvb_utils as utils
    import logging

    logger_name = os.getenv("LOGGER_NAME")
    logger = logging.getLogger(logger_name)

Then, for example, reference the log_wrap decorator as follows
@utils.log_wrap

or, directly invoke a log message
logger.info("log message")

"""

import logging
from logging.handlers import RotatingFileHandler
import os

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)


def log_wrap(func):
    def wrapped(*args, **kwargs):
        logger.debug(f"enter {func.__name__}()")
        result = func(*args, **kwargs)
        logger.debug(f"exit {func.__name__}()")
        return result
    return wrapped


def setup_logging():
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # use environment variables to set each logging channel level
    logger_level_base = os.getenv("LOGGER_LEVEL_BASE")
    logger_level_file = os.getenv("LOGGER_LEVEL_FILE")
    logger_level_stream = os.getenv("LOGGER_LEVEL_STREAM")

    logger.setLevel(logger_level_base)

    # create file handler which logs even debug messages
    fh = RotatingFileHandler(
        f"logs/{logger_name}.log", maxBytes=1000000, backupCount=10)
    fh.setLevel(logger_level_file)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logger_level_stream)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [%(pathname)s:%(lineno)d]')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # logger.debug(f'setup_logging():{logger_name}: example debug message')
    # logger.info(f"setup_logging():{logger_name}: example info message")
    # logger.warning(f'setup_logging():{logger_name}: example warn message')
    # logger.error(f'setup_logging():{logger_name}: example error message')
    # logger.critical(
    #   f'setup_logging():{logger_name}: example critical message')

    logger.info(f"setup_logging():{logger_name}: Logging enabled")
