#!/usr/bin/env python2.7
# coding=utf-8

from __future__ import with_statement

from ucl.physiol.neuroconstruct.utils import NumberGenerator
from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.neuron import NeuronFileManager
from ucl.physiol.neuroconstruct.nmodleditor.processes import ProcessManager
from ucl.physiol.neuroconstruct.cell import *

import sys
import os.path
import time
import optparse

# For finding the cpu count: os, re, subprocess
import os
import re
import subprocess

sys.path.append(os.path.abspath(os.path.join(".")))

import logClient
import projConf


try:
    from java.io import File
except ImportError:
    logger.error("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
    logger.error("See http://www.neuroconstruct.org/docs/python.html for more details")
    quit()


class MultiSim(object):
    proj_conf = None
    logger = None
    projPath = None
    pm = None
    myProject = None
    simConfig = None
    stimulation = None
    cellName = None
    simulatorSeed = None
    numGenerated = 0
    maxNumSimultaneousSims = 1
    densitiesList = []
    channelsList = []
    locationsList = []
    simsRunning = []

    
    def __init__(self, proj_conf):
        configDict = proj_conf.parseProjectConfig()
        self.proj_conf = proj_conf
        self.logger = proj_conf.getClientLogger("MultiSim")
        self.projPath = self.proj_conf.localPath(configDict.get("projPath"))
        self.pm = ProjectManager()
        
        projFile = File(self.projPath)
        self.myProject = self.pm.loadProject(projFile)
        self.simConfig = self.myProject.simConfigInfo.getSimConfig(configDict.get("simConfig"))
    #-----------------------------------------------------------
    def generate(self):
        configDict = self.proj_conf.parseProjectConfig()

        neuroConstructSeed = int(self.proj_conf.get("neuroConstructSeed", "NeuroConstruct"))
        self.stimulation = configDict["stimulation"]
        self.cellName = configDict["cellname"]
        self.simulatorSeed = int(self.proj_conf.get("simulatorSeed", "NeuroConstruct"))
        self.pm.doGenerate(self.simConfig.getName(), neuroConstructSeed)
        self.logger.debug("Waiting for the project to be generated...")
        t = 0.0
        startTime = time.time()
        while self.pm.isGenerating():
            self.logger.debug("Waiting...")
            time.sleep(0.050)
            t += 0.050
            if t > 2.0:
                self.logger.debug("Waiting...")
                t = 0.0
            if (time.time() - startTime) > 50.0:
                self.logger.error("Project data could not be created due to timeout.")
                raise RuntimeError("Simulation timeout occured")
        self.numGenerated = self.myProject.generatedCellPositions.getNumberInAllCellGroups()
        self.logger.debug("Number of cells generated: " + str(self.numGenerated))

        if self.numGenerated > 0:
            self.logger.info("Generating NEURON scripts...")
            self.myProject.neuronSettings.setCopySimFiles(1) # 1 copies hoc/mod files to PySim_0 etc. and will allow multiple sims to run at once
            # hier kann man entscheiden, ob Bilder angezeigt werden sollen oder nicht: 
                # ist ersteres auskommentiert, werden Bilder angezeigt und bei Einkommentierung des Zweiten auch automatisch wieder geschlossen
            self.myProject.neuronSettings.setNoConsole() #1
            #myProject.neuronFileManager.setQuitAfterRun(1) #2

            max_sim_threads = self.proj_conf.get("maxSimThreads")
            if max_sim_threads == "auto":
                self.maxNumSimultaneousSims = available_cpu_count()
            else:
                self.maxNumSimultaneousSims = max(1, int(max_sim_threads))
            self.densitiesList, self.channelsList, self.locationsList = self.parseParameters()
    #-----------------------------------------------------------
    def run(self, prefix, dataList):
        """Runs all simulations defined by dataList for the loaded project.

        Each sim will be named (prefix + i) and dataList contains a
        dict with at least the "candidateIndex" key for accessing the self.densitiesList,
        self.channelsList and self.locationsList
        """
        for i in range(len(dataList)):
            self.waitForSimsRunning(self.maxNumSimultaneousSims - 1)
            if not self.runSim(i, prefix, dataList[i]):
                sys.exit(0)
        self.waitForSimsRunning(0)
        self.logger.info("Finished running " + str(len(dataList)) + " simulations for project " + self.projPath)
        self.logger.info("These can be loaded and replayed in the previous simulation browser in the GUI")

    #-----------------------------------------------------------
    def runSim(self, index, prefix, data):
        simRef = prefix + str(index)
        candidateIndex = data["candidateIndex"]
        densities = self.densitiesList[candidateIndex]
        channels = self.channelsList[candidateIndex]
        locations = self.locationsList[candidateIndex]
        self.logger.debug("densities: " + repr(densities))
        self.logger.debug("channels: " + repr(channels))
        self.logger.debug("locations: " + repr(locations))
        self.logger.debug("Going to run simulation: " + simRef)
        
        stim = self.myProject.elecInputInfo.getStim(self.stimulation)
        self.logger.debug("Stimulation data: " + str(stim))
                
        cell = self.myProject.cellManager.getCell(self.cellName) 
        # hier werden die oben ausgelesenen Daten einzeln dem Konstruktor der Simulation übergeben:
        for i in range(len(densities)):
            chanMech = ChannelMechanism(channels[i], densities[i]) # Konstruktor
            cell.associateGroupWithChanMech(locations[i], chanMech)

        self.myProject.simulationParameters.setReference(simRef)
        self.myProject.neuronFileManager.generateTheNeuronFiles(self.simConfig, None, NeuronFileManager.RUN_HOC, self.simulatorSeed)
        self.logger.debug("Generated NEURON files for: " + simRef)
        compileProcess = ProcessManager(self.myProject.neuronFileManager.getMainHocFile())
        compileSuccess = compileProcess.compileFileWithNeuron(0, 0)
        self.logger.debug("Compiled NEURON files for: " + simRef)
        if compileSuccess:
            self.pm.doRunNeuron(self.simConfig)
            self.logger.info("Set running simulation: " + simRef)
            self.simsRunning.append(simRef)
            return True
        self.logger.error("Could not run simulation: " + simRef)
        return False
    #-----------------------------------------------------------
    def updateSimsRunning(self):
        simsFinished = []
        for sim in self.simsRunning:
            timeFile = File(self.myProject.getProjectMainDirectory(), "simulations/" + sim + "/time.dat")
            if (timeFile.exists()):
                simsFinished.append(sim)

        if(len(simsFinished) > 0):
            for sim in simsFinished:
                self.simsRunning.remove(sim)
    #-----------------------------------------------------------
    def parseParameters(self):
        """Read channel mechanisms."""
        filenameCh = self.proj_conf.getLocalPath("channelFile")
        filenameDe = self.proj_conf.getLocalPath("densityFile")
        filenameLo = self.proj_conf.getLocalPath("locationFile")
        self.logger.debug("channel file: " + filenameCh)
        self.logger.debug("density file: " + filenameDe)
        self.logger.debug("location file: " + filenameLo)
        with open(filenameDe, 'r') as fileDe:
            densitiesList = [l.split('\n') for l in fileDe.read().split('#\n')]
            def convertToFloat(l):
                result = []
                for x in l:
                    x = x.strip()
                    if x != "":
                        result.append(float(x))
                return result
            densitiesList = map(convertToFloat, densitiesList)
        with open(filenameCh, 'r') as fileCh:
            channelsList = [l.split('\n')[:-1] for l in fileCh.read().split('#\n')]
            channelsList = [map(lambda x : x.strip(), l) for l in channelsList]
        with open(filenameLo, 'r') as fileLo:
            locationsList = [l.split('\n')[:-1] for l in fileLo.read().split('#\n')]
            locationsList = [map(lambda x : x.strip(), l) for l in locationsList]
        return (densitiesList, channelsList, locationsList)
    #-----------------------------------------------------------
    def waitForSimsRunning(self, maximumRunning):
        maximumRunning = max(0, maximumRunning)
        if len(self.simsRunning) > maximumRunning:
            self.logger.info("Sims currently running: " + str(self.simsRunning))
            self.logger.info("Waiting...")
            startTime = time.time()
            t = 0
            while (len(self.simsRunning) > maximumRunning):
                tDiff = 1.5 / self.maxNumSimultaneousSims
                time.sleep(tDiff)
                self.updateSimsRunning()
                t = t + tDiff
                if t > 5.0:
                    self.logger.debug("Waiting...")
                    t = 0.0
                if (time.time() - startTime) > 50:
                    self.logger.error("Simulation hat sich aufgehangen!")
                    raise RuntimeError("Simulation timeout occured")

#-----------------------------------------------------------
# Utility method for finding the cpu count.
def available_cpu_count():
    """ Number of available virtual or physical CPUs on this system, i.e.
    user/real as output by time(1) when called with an optimally scaling
    userspace-only program"""

    # cpuset
    # cpuset may restrict the number of *available* processors
    try:
        m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                      open('/proc/self/status').read())
        if m:
            res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        pass

    # Python 2.6+
    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass

    # http://code.google.com/p/psutil/
    try:
        import psutil
        return psutil.NUM_CPUS
    except (ImportError, AttributeError):
        pass

    # POSIX
    try:
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

        if res > 0:
            return res
    except (AttributeError, ValueError):
        pass

    # Windows
    try:
        res = int(os.environ['NUMBER_OF_PROCESSORS'])

        if res > 0:
            return res
    except (KeyError, ValueError):
        pass

    # jython
    try:
        from java.lang import Runtime
        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()
        if res > 0:
            return res
    except ImportError:
        pass

    # BSD
    try:
        sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'],
                                  stdout=subprocess.PIPE)
        scStdout = sysctl.communicate()[0]
        res = int(scStdout)

        if res > 0:
            return res
    except (OSError, ValueError):
        pass

    # Linux
    try:
        res = open('/proc/cpuinfo').read().count('processor\t:')

        if res > 0:
            return res
    except IOError:
        pass

    # Solaris
    try:
        pseudoDevices = os.listdir('/devices/pseudo/')
        res = 0
        for pd in pseudoDevices:
            if re.match(r'^cpuid@[0-9]+$', pd):
                res += 1

        if res > 0:
            return res
    except OSError:
        pass

    # Other UNIXes (heuristic)
    try:
        try:
            dmesg = open('/var/run/dmesg.boot').read()
        except IOError:
            dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
            dmesg = dmesgProcess.communicate()[0]

        res = 0
        while '\ncpu' + str(res) + ':' in dmesg:
            res += 1

        if res > 0:
            return res
    except OSError:
        pass

    raise Exception('Can not determine number of CPUs on this system')
#-----------------------------------------------------------
def main():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", action="store", type="string",
                      help="Path to the configuration file defining the parameters for this run")
    parser.add_option("-d", "--sim-directory", action="store", type="string",
                      help="The working directory with the simulation files")
    parser.add_option("-t", "--type", action="store",
                      choices=["current", "conductance"],
                        help="The type of simulation to launch")
    (options, args) = parser.parse_args()

    proj_conf = projConf.ProjConf(options.config, options.sim_directory)
    logger = proj_conf.getClientLogger("MultiSim")
    
    if options.config is None or options.sim_directory is None or options.type is None:
        logger.error("Not enough parameters specified. See -h for more")
        sys.exit(1)

    
    
    idx = proj_conf.parseIndexFile()

    configDict = proj_conf.parseProjectConfig()
    logger.info("Running " + options.type + " simulation now")
    if options.type == "current":
        class MultiCurrent(MultiSim):
            def runSim(self, index, prefix, data):
                """Hook into runSim to manipulate the current."""
                stim = self.myProject.elecInputInfo.getStim(self.stimulation)
                newAmp = data["current"]
                stim.setAmp(NumberGenerator(newAmp))
                self.myProject.elecInputInfo.updateStim(stim)
                return MultiSim.runSim(self, index, prefix, data)
        dataList = [{"candidateIndex":idx[-1], "current":configDict["startCurrent"] + configDict["stepCurrent"] * i}\
                    for i in range(configDict["numCurrents"])]
        simulator = MultiCurrent(proj_conf)
        simulator.generate()
        simulator.run("multiCurrent_", dataList)
    elif options.type == "conductance":
        candidateLength = idx[0]
        dataList = [{"candidateIndex":x} for x in range(candidateLength)]
        simulator = MultiSim(proj_conf)
        simulator.generate()
        simulator.run("PySim_", dataList)
    else:
        raise RuntimeError("Type parameter not handled: " + options.type)

if __name__ == "__main__":
    main()
    sys.exit(0)
