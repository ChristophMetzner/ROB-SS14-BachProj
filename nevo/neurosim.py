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

import util.projconf as projconf
import chromgen


try:
    from java.io import File
except ImportError:
    logger.error("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
    logger.error("See http://www.neuroconstruct.org/docs/python.html for more details")
    quit()


class Error(Exception):
    """Exception base class for this module."""
    pass

class SimTimeoutError(Error):
    """Timeout error, often occuring with calls to neuroConstruct."""

    def __init__(self, timeout, msg):
        self.timeout = timeout
        self.msg = msg
    
    
class MultiSim(object):
    pconf = None
    logger = None
    proj_path = None
    pm = None
    myProject = None
    simConfig = None
    stimulation = None
    cellName = None
    simulatorSeed = None
    numGenerated = 0
    maxNumSimultaneousSims = 1
    simsRunning = []

    # A value of 0 or lower deactivates timeout.
    sim_timeout = 0
    
    def __init__(self, pconf):
        configDict = pconf.parse_project_data()
        self.pconf = pconf
        self.logger = pconf.get_logger("neurosim")
        self.proj_path = self.pconf.local_path(configDict["proj_path"])
        self.pm = ProjectManager()
        
        projFile = File(self.proj_path)
        self.sim_timeout = self.pconf.get_float("sim_timeout", "Simulation")
        self.myProject = self.pm.loadProject(projFile)
        self.simConfig = self.myProject.simConfigInfo.getSimConfig(self.pconf.get("sim_config", "Simulation"))
    #-----------------------------------------------------------
    def generate(self):

        neuroConstructSeed = int(self.pconf.get("neuroConstructSeed", "NeuroConstruct"))
        self.stimulation = self.pconf.get("stimulation", "Simulation")
        self.cellName = self.pconf.get("cell", "Simulation")
        self.simulatorSeed = int(self.pconf.get("simulatorSeed", "NeuroConstruct"))
        self.pm.doGenerate(self.simConfig.getName(), neuroConstructSeed)
        self.logger.debug("Waiting for the project to be generated...")
        t = 0.0
        startTime = time.time()
        while self.pm.isGenerating():
            self.logger.debug("Waiting...")
            time.sleep(0.050)
            t += 0.050
            if t > 5.0:
                self.logger.debug("Waiting...")
                t = 0.0
            if self.sim_timeout > 0 and (time.time() - startTime) > self.sim_timeout:
                self.logger.error("Project data could not be created due to timeout.")
                raise SimTimeoutError(self.sim_timeout, "Simulation timeout occured during project generation.")
        self.numGenerated = self.myProject.generatedCellPositions.getNumberInAllCellGroups()
        self.logger.debug("Number of cells generated: " + str(self.numGenerated))

        if self.numGenerated > 0:
            self.logger.info("Generating NEURON scripts...")
            self.myProject.neuronSettings.setCopySimFiles(1) # 1 copies hoc/mod files to PySim_0 etc. and will allow multiple sims to run at once
            # hier kann man entscheiden, ob Bilder angezeigt werden sollen oder nicht: 
                # ist ersteres auskommentiert, werden Bilder angezeigt und bei Einkommentierung des Zweiten auch automatisch wieder geschlossen
            self.myProject.neuronSettings.setNoConsole()

            max_sim_threads = self.pconf.get("maxSimThreads")
            if max_sim_threads == "auto":
                self.maxNumSimultaneousSims = available_cpu_count()
            else:
                self.maxNumSimultaneousSims = max(1, int(max_sim_threads))
    #-----------------------------------------------------------
    def run(self, prefix, dataList):
        """Runs all simulations defined by dataList for the loaded project.

        Each sim will be named (prefix + i) and dataList contains a
        dict with at least "densities", "channels" and "locations" keys.
        """
        try:
            for i in range(len(dataList)):
                self.waitForSimsRunning(self.maxNumSimultaneousSims - 1)
                if not self.runSim(i, prefix, dataList[i]):
                    sys.exit(0)
            self.waitForSimsRunning(0)
            self.logger.info("Finished running " + str(len(dataList)) + " simulations for project " + self.proj_path)
            return
        except (KeyboardInterrupt, SystemExit):
            raise
        except SimTimeoutError, e:
            self.logger.warning("Timeout occured: " + e.msg)
            sys.exit(10)
    #-----------------------------------------------------------
    def runSim(self, index, prefix, data):
        simRef = prefix + str(index)
        densities = data["densities"]
        channels = data["channels"]
        locations = data["locations"]

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
                if self.sim_timeout > 0 and (time.time() - startTime) > self.sim_timeout:
                    raise SimTimeoutError(self.sim_timeout, "Simulation timeout occured during sim execution.")
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
def parse_parameters(pconf):
    """Read channel mechanisms."""
    filenameCh = pconf.get_local_path("channelFile")
    filenameDe = pconf.get_local_path("densityFile")
    filenameLo = pconf.get_local_path("locationFile")
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
def populate_candidate_data(pconf, type, candidates = None):
    mode = pconf.get("mode", "Simulation")
    data_list = []
    if candidates != None:
        for i in range(len(candidates)):
            channels = [float(x.strip()) for x in (candidates[i].split(","))];
            data_list.append({"densities" : chromgen.calc_dens(channels, mode),
                            "channels" : chromgen.get_channel_data(mode),
                            "locations" : chromgen.get_location_data(mode)})
    else:
        (densitiesList, channelsList, locationsList) = parse_parameters(pconf)
        index_list = pconf.parse_index_file()
        if(type == "current"):
            index = index_list[-1]
            data_list.append({"densities" : densitiesList[index],
                             "channels" : channelsList[index],
                             "locations" : locationsList[index]})
        elif(type == "conductance"):
            for index in range(index_list[0]):
                data_list.append({"densities" : densitiesList[index],
                                 "channels" : channelsList[index],
                                 "locations" : locationsList[index]})
        else:
            raise RuntimeError("Type parameter not handled: " + type)
    return data_list
#-----------------------------------------------------------
def main():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", action="store", type="string",
                      help="Path to the configuration file defining the parameters for this run")
    parser.add_option("-d", "--sim-directory", action="store", type="string",
                      help="The working directory with the simulation files")
    parser.add_option("-t", "--type", action="store",
                      choices=["current", "conductance"],
                        help = """The type of simulation to launch.
                        "current" will run each supplied candidate with several different currents or the
                        last one specified in the index file.
                        "conductance" will run each supplied candidate or all read from the densities
                        file.""")
    parser.add_option("--candidate", action = "append",
                      help = """The short channel represenation of a chromosome with
                      comma separated values. Supplying any candidates using this option deactivates
                      the lookup using indexFile, channelFile and densityFile.
                      The order of specified candidates will determine the index appended to the
                      given prefix, beginning with 0.""")
    parser.add_option("--prefix",
                      help = """The simulation prefix string. When not specified, the prefix
                      is derived from the --type option.""")
    (options, args) = parser.parse_args()

    pconf = projconf.ProjectConfiguration(options.config, options.sim_directory)
    mode = pconf.get("mode", "Simulation")
    logger = pconf.get_logger("neurosim")


    
    if options.config is None or options.sim_directory is None or options.type is None:
        logger.error("Not enough parameters specified. See -h for more")
        sys.exit(2)
    
    data_list = populate_candidate_data(pconf, type = options.type, candidates = options.candidate)

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
        currents = pconf.get_list("currents", "Simulation")
        currents = [int(currents[0]), float(currents[1]), float(currents[2])]
        expanded_data_list = []
        for data in data_list:
            for i in range(currents[0]):
                dataC = data.copy()
                dataC["current"] = currents[1] + currents[2] * i
                expanded_data_list.append(dataC)
        prefix = "multiCurrent_" if options.prefix == None else options.prefix
        simulator = MultiCurrent(pconf)
        simulator.generate()
        simulator.run(prefix, expanded_data_list)
    elif options.type == "conductance":
        prefix = "PySim_" if options.prefix == None else options.prefix
        simulator = MultiSim(pconf)
        simulator.generate()
        simulator.run(prefix, data_list)
    else:
        raise RuntimeError("Type parameter not handled: " + options.type)

if __name__ == "__main__":
    main()
    sys.exit(0)
