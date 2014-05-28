import time

timeSaved = 0.0
timeSleep = 0.0

def sleep(x, originalX = 0):
    global timeSleep, timeSaved
    """Execute regular time.sleep, but also stores additional data."""
    time.sleep(x)
    timeDelta = max(0.0, originalX - float(x));
    if __debug__ and timeDelta > 0:
        print "+++++++ Saved time delta: ", timeDelta, " seconds"
    timeSaved += timeDelta
    timeSleep += max(0.0, float(x));

def printStats():
    print "+++++++ Sleep time total: ", timeSleep
    print "+++++++ Saved time total: ", timeSaved
