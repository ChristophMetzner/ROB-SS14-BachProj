#! usr/local/lib/python2.7 python
# coding=utf-8
import time
import logging
import projConf


timeSleep = 0.0
startTime = 0.0
debugMode = False;
loggerName = "global"

def initProfiler():
    global timeSleep, startTime, debugMode
    timeSleep = 0.0
    startTime = 0.0
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

initProfiler()

def getLog():
    return logging.getLogger(loggerName)

def sleep(x):
    global timeSleep
    """Execute regular time.sleep, but also stores additional data."""
    if debugMode:
        print "+++++++ Sleeping for: ", x, " seconds"
    time.sleep(x)
    timeSleep += max(0.0, float(x));

def printStats():
    print "+++++++ Sleep time total: ", timeSleep, " seconds"

def startTimer():
    global startTime
    startTime = time.time()

def stopTimer():
    print "+++++++ Time passed: ", time.time() - startTime, " seconds"
