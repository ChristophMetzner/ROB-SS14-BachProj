# coding=utf-8

import logging
import logging.handlers

logger_dict = {}

def getClientLogger(logger_name, log_server_port, log_server_level=1):
    """Creates a logger that logs to the logServer.

    logger_name should be the part of the programme that is doing the
    logging. For example the module name. It will appear in the log
    messages.

    Returns a pre-configured logger instance."""
    if logger_name not in logger_dict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(1)
        logger.propagate = False
        sh = logging.handlers.SocketHandler("localhost",\
                                            log_server_port)
        sh.setLevel(log_server_level)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

        # add the handlers to logger
        logger.addHandler(sh)
        logger_dict[logger_name] = logger
        return logger
    else:
        return logger_dict[logger_name]
