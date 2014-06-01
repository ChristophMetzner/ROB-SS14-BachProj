# coding=utf-8

from __future__ import with_statement

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.neuron import NeuronFileManager
from ucl.physiol.neuroconstruct.nmodleditor.processes import ProcessManager
from ucl.physiol.neuroconstruct.cell import *

import profiler
import logClient
import projConf

logger = logClient.getClientLogger("MultiSim")


try:
    from java.io import File
except ImportError:
    logger.error("Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'")
    logger.error("See http://www.neuroconstruct.org/docs/python.html for more details")
    quit()


class MultiSim(object):
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

    
    def __init__(self, projPath, SimConfig):
        self.projPath = projPath
        self.pm = ProjectManager()
        
        projFile = File(projPath)
        self.myProject = self.pm.loadProject(projFile)
        self.simConfig = self.myProject.simConfigInfo.getSimConfig(SimConfig)
    #-----------------------------------------------------------
    def generate(self, neuroConstructSeed, simulatorSeed, stimulation, cellName):
        self.simulatorSeed = simulatorSeed
        self.stimulation = stimulation
        self.cellName = cellName
        self.pm.doGenerate(self.simConfig.getName(), neuroConstructSeed)
        logger.debug("Waiting for the project to be generated...")
        while self.pm.isGenerating():
            logger.debug("Waiting...")
            profiler.sleep(0.050)
        self.numGenerated = self.myProject.generatedCellPositions.getNumberInAllCellGroups()
        logger.debug("Number of cells generated: " + str(self.numGenerated))

        if self.numGenerated > 0:
            logger.info("Generating NEURON scripts...")
            self.myProject.neuronSettings.setCopySimFiles(1) # 1 copies hoc/mod files to PySim_0 etc. and will allow multiple sims to run at once
            # hier kann man entscheiden, ob Bilder angezeigt werden sollen oder nicht: 
                # ist ersteres auskommentiert, werden Bilder angezeigt und bei Einkommentierung des Zweiten auch automatisch wieder geschlossen
            self.myProject.neuronSettings.setNoConsole() #1
            #myProject.neuronFileManager.setQuitAfterRun(1) #2
            
            self.maxNumSimultaneousSims = max(1, int(projConf.get("maxSimThreads")))
            self.densitiesList, self.channelsList, self.locationsList = self.parseParameters()
    #-----------------------------------------------------------
    def run(self, prefix, dataList):
        """Runs all simulations defined by dataList for the loaded project.

        Each sim will be named (prefix + i) and dataList contains a
        dict with at least the "candidateIndex" key for accessing the self.densitiesList,
        self.channelsList and self.locationsList
        """
        for i in range(len(dataList)):
            self.waitForSimsRunning(self.maxNumSimultaneousSims)
            if not self.runSim(i, prefix, dataList[i]):
                sys.exit(0)
        self.waitForSimsRunning(0)
        logger.info("Finished running " + str(len(dataList)) + " simulations for project " + self.projPath)
        logger.info("These can be loaded and replayed in the previous simulation browser in the GUI")

    #-----------------------------------------------------------
    def runSim(self, index, prefix, data):
        simRef = prefix + str(index)
        candidateIndex = data["candidateIndex"]
        densities = self.densitiesList[candidateIndex]
        channels = self.channelsList[candidateIndex]
        locations = self.locationsList[candidateIndex]
        logger.debug("Going to run simulation: " + simRef)
        
        stim = self.myProject.elecInputInfo.getStim(self.stimulation)
        logger.debug("Stimulation data: " + str(stim))
                
        cell = self.myProject.cellManager.getCell(self.cellName) 
        # hier werden die oben ausgelesenen Daten einzeln dem Konstruktor der Simulation übergeben:
        for i in range(len(densities)):
            chanMech = ChannelMechanism(channels[i], densities[i]) # Konstruktor
            cell.associateGroupWithChanMech(locations[i], chanMech)

        self.myProject.simulationParameters.setReference(simRef)
        self.myProject.neuronFileManager.generateTheNeuronFiles(self.simConfig, None, NeuronFileManager.RUN_HOC, self.simulatorSeed)
        logger.debug("Generated NEURON files for: " + simRef)
        compileProcess = ProcessManager(self.myProject.neuronFileManager.getMainHocFile())
        compileSuccess = compileProcess.compileFileWithNeuron(0, 0)
        logger.debug("Compiled NEURON files for: " + simRef)
        if compileSuccess:
            self.pm.doRunNeuron(self.simConfig)
            logger.info("Set running simulation: " + simRef)
            self.simsRunning.append(simRef)
            return True
        logger.error("Could not run simulation: " + simRef)
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
        filenameCh = projConf.getPath("channelFile", "GenAlg")
        filenameDe = projConf.getPath("densityFile", "GenAlg")
        filenameLo = projConf.getPath("locationFile", "GenAlg")
        with open(filenameDe, 'r') as fileDe:
            densitiesList = [l.split('\n') for l in fileDe.read().split('#\n')]
            def convertToFloat(l):
                result = []
                for x in l:
                    try:
                        result.append(float(x.strip()))
                    except:
                        pass
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
            logger.info("Sims currently running: " + str(self.simsRunning))
            logger.info("Waiting...")
            t = 0
            while (len(self.simsRunning) > maximumRunning):
                tDiff = 1.5 / self.maxNumSimultaneousSims
                profiler.sleep(tDiff)
                self.updateSimsRunning()
                t = t + tDiff
                if t > 30:
                    logger.error("Simulation hat sich aufgehangen!")
                    sys.exit(0)
