#! usr/local/lib/python2.7 python
# coding=utf-8
import time

timeSleep = 0.0
startTime = 0.0

def sleep(x):
    global timeSleep
    """Execute regular time.sleep, but also stores additional data."""
    if __debug__:
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
