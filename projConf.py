#! usr/local/lib/python2.7 python
# coding=utf-8

from __future__ import with_statement

import subprocess
import os.path
import sys

import ConfigParser



cfg = ConfigParser.ConfigParser()
cfg.read("general.cfg")

def get(key, section = "Global"):
    return cfg.get(section, key)

def getPath(key, section = "Global"):
    return normPath(get(key, section))

def normPath(*paths):
    """Accept one or several paths and returns the joined, normalized, absolute path."""
    if sys.platform == "win32":
        return os.path.normpath(os.path.join("C:/Python27/", *paths))
    else:
        return os.path.abspath(os.path.join(*paths))

def parseProjectConfig(section):
    values = {}
    filename = getPath("projectConfig", section)
    with open(filename, 'r') as config:
        c = 0 #counter
        for line in config:
            line = line.strip()
            c = c+1
            if c == 1:
                values.update(projName = line)
            elif c == 2:
                values.update(projPath = line)
            elif c == 3:
                values.update(simConfig = line)
            elif c == 4:
                values.update(stimulation = line)
            elif c == 5:
                values.update(cellname = line)
            elif c == 6:
                values.update(duration = int(line))
            elif c == 7:
                values.update(dt = float(line))
            elif c == 8:
                currents = line.strip("[").strip("]").split(",")
                values.update(currents = currents)
                values.update(numCurrents = int(currents[0]))
                values.update(startCurrent = float(currents[1]))
                values.update(stepCurrent = float(currents[2]))
            elif c == 9:
                values.update(mode = int(line))
    return values
#-----------------------------------------------------------
def parseIndexFile(section):
    """Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!"""
    filenameIndex = getPath("candidateIndex", section)
    with open(filenameIndex, "r") as indexFile:
        idx = []
        val = 0
        for line in indexFile:
            try:    
                val=int(line.strip())
                idx.append(val)
            except:
                pass
        return idx
#-----------------------------------------------------------
def invokeNeuroConstruct(*args):
    if sys.platform == "win32":
        externesProgramm = os.path.normpath(os.path.join(get("installPath", "NeuroConstruct"), "NC.bat"))
        p = subprocess.Popen( externesProgramm + " " + " ".join(args) )
        p.wait()
    else:
        subprocess.check_call([os.path.join(get("installPath", "NeuroConstruct"), "nC.sh")] + list(args))
