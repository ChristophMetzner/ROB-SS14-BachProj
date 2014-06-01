#!/usr/bin/env python2.7
# coding=utf-8
import logging
import sys

sys.path.append("./GenAlg/Programm/")

import profiler
import main_program
import logServer
import logClient
import projConf
import ConfigParser

server = logServer.initFileLogServer(projConf.get("logServerFile", "Logging"),
                                         int(projConf.get("logServerPort", "Logging")),
                                         int(projConf.get("logServerLevel", "Logging")))
logger = logClient.getClientLogger("multiEA")

def logConfig():
    logger.info("Configuration used:")
    sections = projConf.cfg.sections()
    sections.append("DEFAULT")
    for section in sections:
        items = projConf.cfg.items(section)
        if len(items) > 0:
            logger.info("  [" + section + "]")
            for item in items:
                logger.info("   " + repr(item[0]) + " = " + repr(item[1]))



server.start()
profiler.startTimer()

try:
    logger.info("          =============================================")
    logger.info("          =============================================")
    logger.info("          =======    Starting new Simulation    =======")
    logger.info("          =============================================")
    logger.info("          =============================================")
    logConfig()

    kwargs = {}
    for item in projConf.cfg.items("GenAlgParameters"):
            kwargs[item[0]] = eval(item[1])
    main_program.start(**kwargs)

    profiler.stopTimer()
    profiler.printStats()
finally:
    # Necessary to avoid hanging on open sockets
    logging.shutdown()
