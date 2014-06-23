# coding=utf-8

import logging
import logging.handlers

def initClientLogger(logger_name, log_server_port, console_level = logging.INFO,
                    log_server_level=1, suppress_console_output = False):
    """Creates a logger that logs to the logServer.

    logger_name should be the part of the programme that is doing the
    logging. For example the module name. It will appear in the log
    messages.

    Returns a pre-configured logger instance."""
    logger = logging.getLogger(logger_name)
    # First clean the probably old logger.
    oldHandlers = list(logger.handlers)
    for h in oldHandlers:
        logger.removeHandler(h)
        h.close()
    logger.setLevel(1)
    logger.propagate = False
    # Add the appropriate handlers
    sh = logging.handlers.SocketHandler("localhost",\
                                        log_server_port)
    sh.setLevel(log_server_level)
    logger.addHandler(sh)

    if not suppress_console_output:
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

