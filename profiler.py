# coding=utf-8

import time

import logClient

timeSleep = 0.0
startTime = 0.0
stopTime = 0.0

logger = logClient.getClientLogger("profiler")

def sleep(x):
    global timeSleep
    """Execute regular time.sleep, but also stores additional data."""
    logger.debug("Sleeping for: " + str(x) + " seconds")
    time.sleep(x)
    timeSleep += max(0.0, float(x));

def printStats():
    """Prints the time spend sleeping and last stopped intervall.

    All calls to this module are accumulated here, except when they
    are made from a different python interpreter process.
    """
    logger.info("Sleep time total: " + str(timeSleep) + " seconds")
    logger.info("Time passed: " + str(stopTime - startTime) + " seconds")

def startTimer():
    """Stores the start time of the intervall to measure."""
    global startTime, stopTime
    startTime = time.time()
    stopTime = startTime

def stopTimer():
    """Stores the stop time of the intervall that has been measured."""
    global stopTime
    stopTime = time.time()
    
