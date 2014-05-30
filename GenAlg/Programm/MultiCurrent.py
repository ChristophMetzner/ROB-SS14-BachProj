#! usr/local/lib/python2.7 python
# coding=utf-8

from __future__ import with_statement

from ucl.physiol.neuroconstruct.utils import NumberGenerator

import sys
import ConfigParser
import profiler
import projConf

import MultiSim

neuroConstructSeed = int(projConf.get("neuroConstructSeed", "NeuroConstruct"))
simulatorSeed = int(projConf.get("simulatorSeed", "NeuroConstruct"))

logger = profiler.getLog()
configDict = projConf.parseProjectConfig()

class MultiCurrent(MultiSim.MultiSim):
    def runSim(self, index, prefix, data):
        """Hook into runSim to manipulate the current."""
        stim = self.myProject.elecInputInfo.getStim(self.stimulation)
        newAmp = data["current"]
        stim.setAmp(NumberGenerator(newAmp))
        self.myProject.elecInputInfo.updateStim(stim)
        return MultiSim.MultiSim.runSim(self, index, prefix, data)

        
simulator = MultiCurrent(configDict["projPath"], configDict["simConfig"])
simulator.generate(neuroConstructSeed, simulatorSeed, configDict["stimulation"], configDict["cellname"])

idx = projConf.parseIndexFile()
dataList = [{"candidateIndex":idx[-1], "current":configDict["startCurrent"] + configDict["stepCurrent"] * i}\
            for i in range(configDict["numCurrents"])]
simulator.run("multiCurrent_", dataList)
    
sys.exit(0)
