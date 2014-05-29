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

try:
    from java.io import File
except ImportError:
    print "Note: this file should be run using ..\\nC.bat -python XXX.py' or './nC.sh -python XXX.py'"
    print "See http://www.neuroconstruct.org/docs/python.html for more details"
    quit()

from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.neuron import NeuronFileManager
from ucl.physiol.neuroconstruct.utils import NumberGenerator
from ucl.physiol.neuroconstruct.nmodleditor.processes import ProcessManager
from ucl.physiol.neuroconstruct.project import ProjectManager
from ucl.physiol.neuroconstruct.gui.plotter import PlotManager
from ucl.physiol.neuroconstruct.gui.plotter import PlotCanvas
from ucl.physiol.neuroconstruct.dataset import DataSet
from ucl.physiol.neuroconstruct.simulation import SimulationData
from ucl.physiol.neuroconstruct.simulation import SpikeAnalyser
from ucl.physiol.neuroconstruct.cell import *
from ucl.physiol.neuroconstruct.simulation import SimulationParameters
from math import *
import profiler

neuroConstructSeed = 1234
simulatorSeed = 4321

# Check Inputs:
################################
#defaults:

project_path = "Pyr_RS/Pyr_RS.ncx"
SimConfig = "Default Simulation Configuration"
Stimulation = "Input_0"
cellname = 'L5TuftedPyrRS'
cfg = ConfigParser.ConfigParser()
cfg.read("general.cfg")
operatingSystem = cfg.get("Global", "operatingSystem")


if operatingSystem == "linux":
    filename = "./GenAlg/Programm/Speicher/Config.txt"
else:
    filename = "C:\Python27\GenAlg\Programm\Analyse\Config.txt"
config = open(filename, 'r')
c = 0 #counter
for line in config:
    line = line.strip()
    c = c+1 
            
    if c == 2:
        project_path = line
    elif c == 3:
        SimConfig = line
    elif c == 5:
        cellname = line
    else:
        pass
        
config.close()
##############################


# Load an existing neuroConstruct project

projFile = File(project_path)
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
myProject = pm.loadProject(projFile)

simConfig = myProject.simConfigInfo.getSimConfig(SimConfig)


pm.doGenerate(simConfig.getName(), neuroConstructSeed)
print "Waiting for the project to be generated..."
while pm.isGenerating():
    print "Waiting..."
    profiler.sleep(0.050)

numGenerated = myProject.generatedCellPositions.getNumberInAllCellGroups()

print "Number of cells generated: " + str(numGenerated)

simsRunning = []

def runSim(densities, channels, locations):
    print (len(densities), len(channels), len(locations))
    print densities, channels, locations
    cell = myProject.cellManager.getCell(cellname) 

    # print "Channels present: "+str(cell.getChanMechsVsGroups())

    # hier werden die oben ausgelesenen Daten einzeln dem Konstruktor der Simulation übergeben:
    for i in range(len(densities)):
        chanMech = ChannelMechanism(channels[i], densities[i]) # Konstruktor
        cell.associateGroupWithChanMech(locations[i], chanMech)      

    # print "Channels present: "+str(cell.getChanMechsVsGroups())


    myProject.simulationParameters.setReference(simRef)
    myProject.neuronFileManager.generateTheNeuronFiles(simConfig, None, NeuronFileManager.RUN_HOC, simulatorSeed)

    print "Generated NEURON files for: "+simRef

    compileProcess = ProcessManager(myProject.neuronFileManager.getMainHocFile())

    compileSuccess = compileProcess.compileFileWithNeuron(0,modCompileConfirmation)

    print "Compiled NEURON files for: "+simRef

    if compileSuccess:
        pm.doRunNeuron(simConfig)
        print "Set running simulation: "+simRef
        return simRef


def updateSimsRunning():
    global simsRunning
    simsFinished = []

    for sim in simsRunning:
        timeFile = File(myProject.getProjectMainDirectory(), "simulations/"+sim+"/time.dat")
        #print "Checking file: "+timeFile.getAbsolutePath() +", exists: "+ str(timeFile.exists())
        if (timeFile.exists()):
            simsFinished.append(sim)

    if(len(simsFinished)>0):
        for sim in simsFinished:
            simsRunning.remove(sim)

def parseParameters():
    ###### Einstellen der ein Channelmechanismen ########
    
    if operatingSystem == "linux":
        filenameCh = "./GenAlg/Programm/Speicher/channel.txt"
        filenameDe = "./GenAlg/Programm/Speicher/density.txt"
        filenameLo = "./GenAlg/Programm/Speicher/location.txt"
    else:
        filenameCh = "C:\Python27\GenAlg\Programm\Analyse\channel.txt"
        filenameDe = "C:\Python27\GenAlg\Programm\Analyse\density.txt"
        filenameLo = "C:\Python27\GenAlg\Programm\Analyse\location.txt"
    with open(filenameDe, 'r') as fileDe:
        densitiesList = [l.split('\n') for l in fileDe.read().split('#\n')]
        def convertToFloat(l):
            result = []
            for x in l:
                try:
                    result.append(float(x))
                except:
                    pass
            return result
        densitiesList = map(convertToFloat, densitiesList)
    with open(filenameCh, 'r') as fileCh:
        channelsList = [l.split('\n')[:-1] for l in fileCh.read().split('#\n')]
    with open(filenameLo, 'r') as fileLo:
        locationsList = [l.split('\n')[:-1] for l in fileLo.read().split('#\n')]
    return (densitiesList, channelsList, locationsList)


def waitForSimsRunning(maximumRunning):
    maximumRunning = max(0, maximumRunning)
    if len(simsRunning) > maximumRunning:
        print "Sims currently running: "+str(simsRunning)
        print "Waiting..."
        t = 0
        while (len(simsRunning) > maximumRunning):
            tDiff = 1.5 /maxNumSimultaneousSims
            profiler.sleep(tDiff)
            updateSimsRunning()
            t = t + tDiff
            if t > 30:
                print "Simulation hat sich aufgehangen!"
                sys.exit(0)

if numGenerated > 0:
    print "Generating NEURON scripts..."
    myProject.neuronSettings.setCopySimFiles(1) # 1 copies hoc/mod files to PySim_0 etc. and will allow multiple sims to run at once

    # hier kann man entscheiden, ob Bilder angezeigt werden sollen oder nicht: 
        # ist ersteres auskommentiert, werden Bilder angezeigt und bei Einkommentierung des Zweiten auch automatisch wieder geschlossen
    myProject.neuronSettings.setNoConsole() #1
    #myProject.neuronFileManager.setQuitAfterRun(1) #2

    modCompileConfirmation = 0 # 0 means do not pop up console or confirmation dialog when mods have compiled
    
    #### Anzahl der Kandidaten aus Datei lesen #####
    if operatingSystem == "linux":
        index = open("./GenAlg/Programm/Speicher/index.txt","r")
    else:
        index = open("C:\Python27\GenAlg\Programm\Analyse\index.txt","r")
    len_cand = 0
    for line in index:
        line = line.strip()             
        try:    
            len_cand=int(line)
        except:
            pass
    index.close()
    ################################################    

    # Note same network structure will be used for each!
    numSimulationsToRun = len_cand
    
    maxNumSimultaneousSims = max(1, min(len_cand, int(cfg.get("Global", "maxSimThreads"))))
    
    simReferences = {}
    
    densitiesList, channelsList, locationsList = parseParameters()
        
    for i in range(0, numSimulationsToRun):
        waitForSimsRunning(maxNumSimultaneousSims)

        simRef = "PySim_"+str(i)
        stim = myProject.elecInputInfo.getStim(Stimulation)
        print stim
        
        print "Going to run simulation: "+simRef

        ###### Einstellen der einzelnen Channelmechanismen ########

        newSim = runSim(densitiesList[i], channelsList[i], locationsList[i])
        simsRunning.append(newSim)
    waitForSimsRunning(0)
        
    print
    print "Finished running "+str(numSimulationsToRun)+" simulations for project "+ projFile.getAbsolutePath()
    print "These can be loaded and replayed in the previous simulation browser in the GUI"
    print


#  Remove this line to remain in interactive mode -- den wollen wir NICHT! Also:
sys.exit(0)
