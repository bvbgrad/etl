"""
"""

import argparse
import json
import logging
import os

import app.utils6L.utils6L as utils

author = __author__ = 'Brent V. Bingham'
version = __version__ = '0.1'

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

CONFIG_FILE_NAME = "config.json"
default_config_data = {
    "theme": {
        "lookandfeel": "LightGreen"
    }
}


@utils.log_wrap
def get_config():
    logger.info(__name__ + ".get_config()")

    if os.path.exists(CONFIG_FILE_NAME):
        try:
            with open(CONFIG_FILE_NAME, "r") as json_data_file:
                config_data = json.load(json_data_file)
                logger.info(__name__ + ".load_config() config file loaded successfully")
        except Exception as err:
            logger.warn(f"{err}: Using default configuration")
            config_data = default_config_data
    else:
        logger.info(__name__ + ".load_config() no config file: using default configuration")
        config_data = default_config_data

    return config_data


@utils.log_wrap
def save_config(config_data):
    logger.info(__name__ + ".save_config()")
    try:
        with open(CONFIG_FILE_NAME, "w") as json_data_file:
            json.dump(config_data, json_data_file)
    except Exception as err:
        logger.warn(f"{err}: error saving configuration")


@utils.log_wrap
def get_version():
    logger.info(__name__ + ".get_version()")
    return f"Version: {version}\nCopyright 2021 6L.LLC dba 6LSolutions\nAll rights reserved"


@utils.log_wrap
def getargs():
    logger.info(__name__ + ".getargs()")
    parser = argparse.ArgumentParser(
        description="Track and log job search activities")
    parser.add_argument(
        '-i', '--index', default=False, action="store_true",
        help='Display object indexes in tables')
    parser.add_argument(
        '-v', '--verbose', default=False, action="store_true",
        help='Provide detailed information')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {version}')
    args = parser.parse_args()
    return args
