# coding=utf-8

import logging
import logging.handlers

import projConf

loggerDict = {}

def getClientLogger(loggerName):
    """Creates a logger that logs to normal stream and to the logServer.

    loggerName should be the part of the programme that is doing the
    logging. For example the module name. It will appear in the log
    messages.

    Returns a pre-configured logger instance."""
    if loggerName not in loggerDict:
        logger = logging.getLogger(loggerName)
        logger.setLevel(1)
        logger.propagate = False
        ch = logging.StreamHandler()
        sh = logging.handlers.SocketHandler("localhost",\
                                            int(projConf.get("logServerPort", "Logging")))
        if int(projConf.get("debugMode")):
            ch.setLevel(logging.DEBUG)

        else:
            ch.setLevel(logging.INFO)
        sh.setLevel(int(projConf.get("logServerLevel", "Logging")))
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        ch.setFormatter(formatter)

        # add the handlers to logger
        logger.addHandler(ch)
        logger.addHandler(sh)
        loggerDict[loggerName] = logger
        return logger
    else:
        return loggerDict[loggerName]
