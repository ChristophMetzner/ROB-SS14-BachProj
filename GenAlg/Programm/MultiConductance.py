#! usr/local/lib/python2.7 python
# coding=utf-8

#
#   A file which opens a neuroConstruct project and generates it, then generates a series
#   of slightly different NEURON simulations, using the same network, but different stimulations.
#   An input current vs firing frequency plot is generated afterwards.
#   The simulations can also be viewed and analysed afterwards in the neuroConstruct GUI
#
#   Author: Padraig Gleeson
#
#   This file has been developed as part of the neuroConstruct project
#   This work has been funded by the Medical Research Council and the
#   Wellcome Trust
#
#

from __future__ import with_statement

import sys
import ConfigParser
import profiler
import projConf

import MultiSim

neuroConstructSeed = int(projConf.get("neuroConstructSeed", "NeuroConstruct"))
simulatorSeed = int(projConf.get("simulatorSeed", "NeuroConstruct"))

logger = profiler.getLog()
configDict = projConf.parseProjectConfig("GenAlg")

simulator = MultiSim.MultiSim(configDict["projPath"], configDict["simConfig"])
simulator.generate(neuroConstructSeed, simulatorSeed, configDict["stimulation"], configDict["cellname"])

candidateLength = projConf.parseIndexFile("GenAlg")[0]
dataList = [{"candidateIndex":x} for x in range(candidateLength)]
simulator.run("PySim_", dataList)

sys.exit(0)
