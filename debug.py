# import data.scoreboard_config
import time
import sys

DEBUG_ENABLED = False


def set_debug_status(config_debug):
    global DEBUG_ENABLED  # pylint: disable=global-statement
    DEBUG_ENABLED = config_debug


def __debugprint(text):
    print(text)
    sys.stdout.flush()


def log(text):
    if DEBUG_ENABLED:
        __debugprint("DEBUG ({}): {}".format(__timestamp(), text))


def warning(text):
    __debugprint("WARNING ({}): {}".format(__timestamp(), text))


def error(text):
    __debugprint("ERROR ({}): {}".format(__timestamp(), text))


def info(text):
    __debugprint("INFO ({}): {}".format(__timestamp(), text))


def __timestamp():
    return time.strftime("%H:%M:%S", time.localtime())
