#! usr/local/lib/python2.7 python
# coding=utf-8
import time
import ConfigParser


cfg = ConfigParser.ConfigParser()
cfg.read("general.cfg")

timeSleep = 0.0
startTime = 0.0
debugMode = int(cfg.get("Global", "debugMode"))

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
