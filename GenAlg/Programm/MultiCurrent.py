#! usr/local/lib/python2.7 python
# coding=utf-8

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

from math import *
import profiler

neuroConstructSeed = 1234
simulatorSeed = 4321

# Check Inputs:
################################
#defaults:

project_path = "Pyr_RS/Pyr_RS.ncx"
SimConfig = "Default Simulation Configuration"
Stimulation = "Input_0" #["Input_0","Input_1","Input_2"]
cellname = 'L5TuftedPyrRS'
cfg = ConfigParser.ConfigParser()
cfg.read("general.cfg")
operatingSystem = cfg.get("Global", "operatingSystem")
numCurrents = 2
startCurrent = 0.3  #mA
stepCurrent = 0.5   #mA

if operatingSystem == "linux":
    filename = "./GenAlg/Programm/Speicher/Config.txt"
else:
    filename = "C:\Python27\GenAlg\Programm\Analyse\Config.txt"
with open(filename, 'r') as config:
    c = 0 #counter
    for line in config:
        line = line.strip()
        c = c+1 
        if c == 2:
            project_path = line
        elif c == 3:
            SimConfig = line
        #elif c == 4:
            #Stimulation = line
        elif c == 5:
            cellname = line
        elif c == 8:
            currents = line
            currents = line.strip("[").strip("]").split(",")
            numCurrents = int(currents[0])
            startCurrent = float(currents[1])
            stepCurrent = float(currents[2])
        else:
            pass
##############################


# Load an existing neuroConstruct project

projFile = File(project_path)
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
myProject = pm.loadProject(projFile)


def runSim(simRef, densities, channels, locations):
    cell = myProject.cellManager.getCell(cellname) 
    # print "Channels present: "+str(cell.getChanMechsVsGroups())

    # hier werden die oben ausgelesenen Daten einzeln dem Konstruktor der Simulation übergeben:
    for i in range(len(densities)):
        chanMech = ChannelMechanism(channels[i], densities[i]) # Konstruktor
        cell.associateGroupWithChanMech(locations[i], chanMech)

    myProject.simulationParameters.setReference(simRef)
    myProject.neuronFileManager.generateTheNeuronFiles(simConfig, None, NeuronFileManager.RUN_HOC, simulatorSeed)
    print "Generated NEURON files for: "+simRef
    compileProcess = ProcessManager(myProject.neuronFileManager.getMainHocFile())
    compileSuccess = compileProcess.compileFileWithNeuron(0,modCompileConfirmation)
    print "Compiled NEURON files for: "+simRef
    if compileSuccess:
        pm.doRunNeuron(simConfig)
        print "Set running simulation: "+simRef
        return True
    return False


def updateSimsRunning(simsRunning):
    simsFinished = []

    for sim in simsRunning:
        timeFile = File(myProject.getProjectMainDirectory(), "simulations/"+sim+"/time.dat")
        if (timeFile.exists()):
            simsFinished.append(sim)

    if(len(simsFinished)>0):
        for sim in simsFinished:
            simsRunning.remove(sim)


def parseParameters():
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


def waitForSimsRunning(maximumRunning, simsRunning):
    maximumRunning = max(0, maximumRunning)
    if len(simsRunning) > maximumRunning:
        print "Sims currently running: "+str(simsRunning)
        print "Waiting..."
        t = 0
        while (len(simsRunning) > maximumRunning):
            tDiff = 1.5 /maxNumSimultaneousSims
            profiler.sleep(tDiff)
            updateSimsRunning(simsRunning)
            t = t + tDiff
            if t > 40:
                print "Simulation hat sich aufgehangen!"
                sys.exit(0)



simConfig = myProject.simConfigInfo.getSimConfig(SimConfig)


pm.doGenerate(simConfig.getName(), neuroConstructSeed)
print "Waiting for the project to be generated..."
while pm.isGenerating():
    print "Waiting..."
    profiler.sleep(0.050)
    
numGenerated = myProject.generatedCellPositions.getNumberInAllCellGroups()

print "Number of cells generated: " + str(numGenerated)
            

if numGenerated > 0:

    print "Generating NEURON scripts..."
    
    
    myProject.neuronSettings.setCopySimFiles(1) # 1 copies hoc/mod files to PySim_0 etc. and will allow multiple sims to run at once

    # hier kann man entscheiden, ob Bilder angezeigt werden sollen oder nicht: 
        # ist ersteres auskommentiert, werden Bilder angezeigt und bei Einkommentierung des Zweiten auch automatisch wieder geschlossen
    myProject.neuronSettings.setNoConsole() #1
    #myProject.neuronFileManager.setQuitAfterRun(1) #2

    modCompileConfirmation = 0 # 0 means do not pop up console or confirmation dialog when mods have compiled
    

    # Note same network structure will be used for each!
    numSimulationsToRun = numCurrents
    maxNumSimultaneousSims = max(1, min(numCurrents, int(cfg.get("Global", "maxSimThreads"))))

    
    #### Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!#####
    if operatingSystem == "linux":
        filenameIndex = "./GenAlg/Programm/Speicher/index.txt"
    else:
        filenameIndex = "C:\Python27\GenAlg\Programm\Analyse\index.txt"
    with open(filenameIndex, "r") as indexFile:
        idx = []
        val = 0
        for line in indexFile:
            try:    
                val=int(line.strip())
                idx.append(val)
            except:
                pass
    
    densitiesList, channelsList, locationsList = parseParameters()
    simsRunning = []
    for i in range(0, numSimulationsToRun):
        waitForSimsRunning(maxNumSimultaneousSims, simsRunning)
        
        simRef = "multiCurrent_"+str(i)
        print "Going to run simulation: "+simRef
        ########  Adjusting the amplitude of the current clamp #######
        stim = myProject.elecInputInfo.getStim(Stimulation)
        newAmp = startCurrent+stepCurrent*i
        stim.setAmp(NumberGenerator(newAmp))
        

        myProject.elecInputInfo.updateStim(stim)
        print "Next stim: "+ str(stim)

        if runSim(simRef, densitiesList[idx[-1]], channelsList[idx[-1]], locationsList[idx[-1]]):
            simsRunning.append(simRef)
        else:
            print
            print "ERROR, Could not run simulation: "+simRef
            sys.exit(0)
    waitForSimsRunning(0, simsRunning)
    
    
    print
    print "Finished running "+str(numSimulationsToRun)+" simulations for project "+ projFile.getAbsolutePath()
    print "These can be loaded and replayed in the previous simulation browser in the GUI"
    print

sys.exit(0)
