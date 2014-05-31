#! usr/local/lib/python2.7 python
# coding=utf-8
import time
import logging
import projConf


timeSleep = 0.0
startTime = 0.0
stopTime = 0.0
debugMode = False;
loggerName = "global"

def initProfiler():
    """Initializes this module and is automatically invoked during import."""
    global timeSleep, startTime, debugMode
    timeSleep = 0.0
    startTime = 0.0
    stopTime = 0.0
    debugMode = int(projConf.get("debugMode"))
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    ##create file handler which logs even debug messages
    #fh = logging.FileHandler('output.log')
    #fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if debugMode:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    #logger.addHandler(fh)

def getLog():
    return logging.getLogger(loggerName)

def sleep(x):
    global timeSleep
    """Execute regular time.sleep, but also stores additional data."""
    getLog().debug("++ Sleeping for: " + str(x) + " seconds")
    time.sleep(x)
    timeSleep += max(0.0, float(x));

def printStats():
    """Prints the time spend sleeping and last stopped intervall.

    All calls to this module are accumulated here, except when they
    are made from a different python interpreter process.
    """
    getLog().info("++ Sleep time total: " + str(timeSleep) + " seconds")
    getLog().info("++ Time passed: " + str(stopTime - startTime) + " seconds")

def startTimer():
    """Stores the start time of the intervall to measure."""
    global startTime, stopTime
    startTime = time.time()
    stopTime = startTime

def stopTimer():
    """Stores the stop time of the intervall that has been measured."""
    global stopTime
    stopTime = time.time()
    

initProfiler()

