#! usr/local/lib/python2.7 python
# coding=utf-8
import sys


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


BS = 1 #1:linux, 2:windows


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
import time

neuroConstructSeed = 1234
simulatorSeed = 4321

# Check Inputs:
################################
#defaults:

project_path = "Pyr_RS/Pyr_RS.ncx"
SimConfig = "Default Simulation Configuration"
Stimulation = "Input_0" #["Input_0","Input_1","Input_2"]
cellname = 'L5TuftedPyrRS'
numCurrents = 2
startCurrent = 0.3  #mA
stepCurrent = 0.5   #mA

if BS == 1:
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
        
config.close()
##############################


# Load an existing neuroConstruct project

projFile = File(project_path)
print "Loading project from file: " + projFile.getAbsolutePath()+", exists: "+ str(projFile.exists())

pm = ProjectManager()
myProject = pm.loadProject(projFile)

simConfig = myProject.simConfigInfo.getSimConfig(SimConfig)


pm.doGenerate(simConfig.getName(), neuroConstructSeed)

while pm.isGenerating():
    print "Waiting for the project to be generated..."
    time.sleep(2)
    
numGenerated = myProject.generatedCellPositions.getNumberInAllCellGroups()

print "Number of cells generated: " + str(numGenerated)

simsRunning = []




def updateSimsRunning():

    simsFinished = []

    for sim in simsRunning:
        timeFile = File(myProject.getProjectMainDirectory(), "simulations/"+sim+"/time.dat")
        if (timeFile.exists()):
            simsFinished.append(sim)

    if(len(simsFinished)>0):
        for sim in simsFinished:
            simsRunning.remove(sim)

            

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
    # Change this number to the number of processors you wish to use on your local machine
    if numSimulationsToRun < 4:
        maxNumSimultaneousSims = numSimulationsToRun
    else:
        maxNumSimultaneousSims = 4
    #maxNumSimultaneousSims = 1    

    simReferences = {}
    
    #### Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!#####
    if BS == 1:
        index = open("./GenAlg/Programm/Speicher/index.txt","r")
    else:
        index = open("C:\Python27\GenAlg\Programm\Analyse\index.txt","r")
    idx = []
    val = 0
    for line in index:
        line = line.strip()             
        try:    
            val=int(line)
        except:
            pass
        idx.append(val)
        
    index.close()
    
    if BS == 1:
        fileCH = open("./GenAlg/Programm/Speicher/channel.txt", 'r')
        fileDE = open("./GenAlg/Programm/Speicher/density.txt", 'r')
        fileLO = open("./GenAlg/Programm/Speicher/location.txt", 'r')
    else:
        fileCH = open("C:\Python27\GenAlg\Programm\Analyse\channel.txt", 'r')
        fileDE = open("C:\Python27\GenAlg\Programm\Analyse\density.txt", 'r')
        fileLO = open("C:\Python27\GenAlg\Programm\Analyse\location.txt", 'r')
    
    density = []
    channel = []
    location = []
    
    densities_list= fileDE.read().split('#\n')  
    channels_list= fileCH.read().split('#\n')
    locations_list= fileLO.read().split('#\n')
    
    ### Leitfähigkeiten des Neurons idx in die Simulation bringen ####
    densities = densities_list[idx[-1]].split('\n')
    for dens in densities:
        dens = dens.strip()             
        try:    
            x = float(dens)
            density.append(x)
        except:
            pass    

    
    channels = channels_list[idx[-1]].split('\n') 
    for chan in channels:
        chan = chan.strip()             
        channel.append(chan)

    
    locations = locations_list[idx[-1]].split('\n')
    for loc in locations:
        loc = loc.strip()               
        location.append(loc)


    for i in range(0, numSimulationsToRun):
        t = 0
        while (len(simsRunning)>=maxNumSimultaneousSims):
            print "Sims currently running: "+str(simsRunning)
            print "Waiting..."
            time.sleep(2) # wait a while...
            updateSimsRunning()
            t = t+1
            if t == 20:
                print "Simulation hat sich aufgehangen!"
                sys.exit(0)

    
        simRef = "multiCurrent_"+str(i)

        print "Going to run simulation: "+simRef
        
        ########  Adjusting the amplitude of the current clamp #######
        
        stim = myProject.elecInputInfo.getStim(Stimulation)
        newAmp = startCurrent+stepCurrent*i
        stim.setAmp(NumberGenerator(newAmp))
        
        simReferences[simRef] = newAmp

        myProject.elecInputInfo.updateStim(stim)
        print "Next stim: "+ str(stim)
            time.sleep(2)
        
    
        cell = myProject.cellManager.getCell(cellname)
    
        print "Channels present: "+str(cell.getChanMechsVsGroups())
        
        for i in range(len(density)):
            chanMech = ChannelMechanism(channel[i], density[i])
            cell.associateGroupWithChanMech(location[i], chanMech)  
            
        print "Channels present: "+str(cell.getChanMechsVsGroups())
        
        myProject.simulationParameters.setReference(simRef)
        
        myProject.neuronFileManager.generateTheNeuronFiles(simConfig, None, NeuronFileManager.RUN_HOC, simulatorSeed)

        print "Generated NEURON files for: "+simRef
    
        compileProcess = ProcessManager(myProject.neuronFileManager.getMainHocFile())
    
        compileSuccess = compileProcess.compileFileWithNeuron(0,modCompileConfirmation)

        print "Compiled NEURON files for: "+simRef
    
        if compileSuccess:
            pm.doRunNeuron(simConfig)
            print "Set running simulation: "+simRef
            simsRunning.append(simRef)
            
        time.sleep(1) # Wait for sim to be kicked off
    
    
    fileCH.close()
    fileDE.close()
    fileLO.close()
        
    print
    print "Finished running "+str(numSimulationsToRun)+" simulations for project "+ projFile.getAbsolutePath()
    print "These can be loaded and replayed in the previous simulation browser in the GUI"
    print

sys.exit(0)
