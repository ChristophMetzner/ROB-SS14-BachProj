#!/usr/bin/env python2.7
# -*- coding: cp1252 -*-
import Tkinter as tk
from tkFileDialog   import *
import subprocess
from tkMessageBox import *

from nevo.util import projconf

configIsLoaded=0
gconfig = None

TITLE_FONT = ("Helvetica", 18, "bold")

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        #Variables from ChooseAlgoPage
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        #all variables for the config are stored here in the SampleApp

        #choosen algorithm
        self.algorithm= tk.StringVar(value="genetic")

        #Global settings from Page "ChooseAlgoPage"
        self.debugValue= tk.StringVar(value=0)
        self.threadValue= tk.StringVar(value="auto")
        self.filelogValue = tk.StringVar(value=20)
        self.consolelogValue= tk.StringVar(value=20)
        self.modeVar = tk.StringVar(value="RS")
        
        #Variables from EvoluParaPage
        self.thrFourierValue = tk.StringVar(value=5)
        self.MaxGenerationValue=  tk.StringVar(value=30)
        self.popSizeValue=  tk.StringVar(value=0)
        self.selectorChoice= tk.StringVar(value="tournament_selection")
        self.tournament_sizeValue= tk.StringVar(value=15)
        self.num_selectedValue= tk.StringVar(value=50)
        self.variatorChoice= tk.StringVar(value="n_point_crossover")
        self.num_co_pointValue= tk.StringVar(value=1)
        self.crossover_rateValue= tk.StringVar(value=1)
        self.mutation_strengthValue= tk.StringVar(value=0.15)
        self.replacerChoice= tk.StringVar(value="truncation_replacement")
        self.numElitesValue= tk.StringVar(value=0)
        self.penFourierValue= tk.StringVar(value=-10000)
        self.penalty_ai_RSValue= tk.StringVar(value=-3500)
        self.penalty_ai_FSValue= tk.StringVar(value=-3500)
        self.penalty_ibf_IBValue= tk.StringVar(value=-2500)
        self.penalty_ibf_CHValue= tk.StringVar(value=-3500)
        self.penalty_ir_IBValue= tk.StringVar(value=-3500)
        self.penalty_ir_CHValue= tk.StringVar(value=-2500)
        self.apwValue= tk.StringVar(value=1)
        self.ibfValue= tk.StringVar(value=1)
        self.irValue= tk.StringVar(value=1)
        self.aiValue= tk.StringVar(value=1)
        self.slopeValue= tk.StringVar(value=1)

        #Variables from SimulatedAnealingPag
        self.stepmaxValue= tk.StringVar(value=100)
        self.start_temperatureValue= tk.StringVar(value=10000)
        self.cooling_scheduleValue =tk.StringVar(value="exponential")
        self.cooling_schedule_alphaValue= tk.StringVar(value=0.9)
        self.neighbour_countValue= tk.StringVar(value=2)

        #Variables from Gridsearch
        self.gridmodeValue =tk.StringVar(value="exponential")
        self.howToChannelar= tk.StringVar(value="constant")
        self.howToChannelcal= tk.StringVar(value="constant")
        self.howToChannelcat= tk.StringVar(value="constant")
        self.howToChannelk2= tk.StringVar(value="constant")
        self.howToChannelka= tk.StringVar(value="constant")
        self.howToChannelkahp= tk.StringVar(value="constant")
        self.howToChannelhc= tk.StringVar(value="constant")
        self.howToChannelalpha= tk.StringVar(value="constant")
        self.howToChannelkm= tk.StringVar(value="constant")
        self.howToChannelnaf= tk.StringVar(value="constant")
        self.howToChannelnap= tk.StringVar(value="constant")
        self.howToChannelpas= tk.StringVar(value="constant")
                               
        self.ar=tk.StringVar(value="0")
        self.cal=tk.StringVar(value="9")
        self.cat=tk.StringVar(value="2.8*10**-9")
        self.k2=tk.StringVar(value="0")
        self.ka=tk.StringVar(value="8.3*10**-6")
        self.kahp=tk.StringVar(value="0")
        self.hc=tk.StringVar(value="3.47*10**-6")
        self.alpha=tk.StringVar(value="1.56")
        self.km=tk.StringVar(value="0")
        self.naf=tk.StringVar(value="0.00086")
        self.nap=tk.StringVar(value="0")
        self.pas=tk.StringVar(value="0.00002")

        self.arUpper=tk.StringVar(value="9*10**-8")
        self.calUpper=tk.StringVar(value="10*10**-8")
        self.catUpper=tk.StringVar(value="0")
        self.k2Upper=tk.StringVar(value="0")
        self.kaUpper=tk.StringVar(value="0")
        self.kahpUpper=tk.StringVar(value="0")
        self.hcUpper=tk.StringVar(value="0")
        self.alphaUpper=tk.StringVar(value="0")
        self.kmUpper=tk.StringVar(value="0")
        self.nafUpper=tk.StringVar(value="0")
        self.napUpper=tk.StringVar(value="0")
        self.pasUpper=tk.StringVar(value="0")

        self.arLower=tk.StringVar(value="8*10**-8")
        self.calLower=tk.StringVar(value="9*10**-8")
        self.catLower=tk.StringVar(value="0")
        self.k2Lower=tk.StringVar(value="0")
        self.kaLower=tk.StringVar(value="0")
        self.kahpLower=tk.StringVar(value="0")
        self.hcLower=tk.StringVar(value="0")
        self.alphaLower=tk.StringVar(value="0")
        self.kmLower=tk.StringVar(value="0")
        self.nafLower=tk.StringVar(value="0")
        self.napLower=tk.StringVar(value="0")
        self.pasLower=tk.StringVar(value="0")

        self.arStep=tk.StringVar(value="0.2*10**-8")
        self.calStep=tk.StringVar(value="0.2*10**-8")
        self.catStep=tk.StringVar(value="0")
        self.k2Step=tk.StringVar(value="0")
        self.kaStep=tk.StringVar(value="0")
        self.kahpStep=tk.StringVar(value="0")
        self.hcStep=tk.StringVar(value="0")
        self.alphaStep=tk.StringVar(value="0")
        self.kmStep=tk.StringVar(value="0")
        self.nafStep=tk.StringVar(value="0")
        self.napStep=tk.StringVar(value="0")
        self.pasStep=tk.StringVar(value="0")
                              
        
        for F in (ChooseAlgoPage, EvoluParameterPage, SimulatedAnnealingPage, GridsearchPage):
            frame = F(container, self)
            self.frames[F] = frame
            # put all of the pages in the same location; 
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ChooseAlgoPage)



    def show_frame(self, c):
        '''Show a frame for the given class'''
        frame = self.frames[c]
        frame.tkraise()

    #load the chosen parameter in the config file and start the specified algorithm
    def start(self):
        global gconfig

        print "starte algorithmus"
        
        self.configFile = asksaveasfile(title="Save Configuration",mode='w', defaultextension=".cfg")
        Config = gconfig

        Config.set("Global", "debugMode", self.debugValue.get())
        Config.set("Global", "maxSimThreads",self.threadValue.get())
        Config.set("Logging", "file_log_level",self.filelogValue.get())
        Config.set("Logging", "console_log_level",self.consolelogValue.get())
        Config.set("Simulation", "mode", self.modeVar.get())
        Config.set("Simulation", "algorithm",self.algorithm.get())
        Config.set("Simulation","selector", self.selectorChoice.get())
        Config.set("Simulation","variators", self.variatorChoice.get())
        Config.set("Simulation","replacer", self.replacerChoice.get())
        Config.set("EvolveParameters","pop_size",self.popSizeValue.get())
        Config.set("EvolveParameters","max_generations",self.MaxGenerationValue.get())
        Config.set("tournament_selection","num_selected",self.num_selectedValue.get())
        Config.set("tournament_selection","tournament_size",self.tournament_sizeValue.get())
        Config.set("fitness_proportionate_selection","num_selected",self.num_selectedValue.get())
        Config.set("truncation_selection","num_selected",self.num_selectedValue.get())
        Config.set("n_point_crossover","crossover_rate",self.crossover_rateValue.get())
        Config.set("n_point_crossover","num_crossover_points",self.num_co_pointValue.get())
        Config.set("nuMutation","mutation_strength",self.mutation_strengthValue.get())
        Config.set("random_replacement","num_elites",self.numElitesValue.get())
        Config.set("fitness.calc_fitness_candidates","thrFourier",self.thrFourierValue.get())
        Config.set("fitness.calc_fitness_candidates","penFourier",self.penFourierValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ai_RS",self.penalty_ai_RSValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ai_FS",self.penalty_ai_FSValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ibf_IB",self.penalty_ibf_IBValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ibf_CH",self.penalty_ibf_CHValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ir_IB",self.penalty_ir_IBValue.get())
        Config.set("fitness.calc_fitness_candidates","penalty_ir_CH",self.penalty_ir_CHValue.get())
        Config.set("fitness.calc_fitness_candidates","W_apw",self.apwValue.get())
        Config.set("fitness.calc_fitness_candidates","W_ibf",self.ibfValue.get())
        Config.set("fitness.calc_fitness_candidates","W_ir",self.irValue.get())
        Config.set("fitness.calc_fitness_candidates","W_ai",self.aiValue.get())
        Config.set("fitness.calc_fitness_candidates","W_slope",self.slopeValue.get())
        Config.set("annealing","stepmax",self.stepmaxValue.get())
        Config.set("annealing","start_temperature",self.start_temperatureValue.get())
        Config.set("annealing","cooling_schedule",self.cooling_scheduleValue.get())
        Config.set("annealing","cooling_schedule_alpha",self.cooling_schedule_alphaValue.get())
        Config.set("annealing","neighbour_count",self.neighbour_countValue.get())
        Config.set("gridsearch","gridmode",self.gridmodeValue.get())
        
        if (self.howToChannelar.get()=="constant"):
            Config.set("gridsearch","ar",self.ar.get())
            print"constant"
        else:
            Config.set("gridsearch","ar", self.arLower.get()+","+self.arUpper.get()+","+self.arStep.get())
            print"bounds"

        if(self.howToChannelcal.get()=="constant"):
            Config.set("gridsearch","cal",self.cal.get())
        else:
            Config.set("gridsearch","cal", self.calLower.get()+","+self.calUpper.get()+","+self.calStep.get())
            
        if(self.howToChannelcat.get()=="constant"):
            Config.set("gridsearch","cat",self.cat.get())
        else:
            Config.set("gridsearch","cat", self.catLower.get()+","+self.catUpper.get()+","+self.catStep.get())

        if(self.howToChannelk2.get()=="constant"):
            Config.set("gridsearch","k2",self.k2.get())
        else:
            Config.set("gridsearch","k2", self.k2Lower.get()+","+self.k2Upper.get()+","+self.k2Step.get())
            
        if(self.howToChannelka.get()=="constant"):
            Config.set("gridsearch","ka",self.ka.get())
        else:
            Config.set("gridsearch","ka", self.kaLower.get()+","+self.kaUpper.get()+","+self.kaStep.get())
            
        if(self.howToChannelkahp.get()=="constant"):
            Config.set("gridsearch","kahp",self.kahp.get())
        else:
            Config.set("gridsearch","kahp", self.kahpLower.get()+","+self.kahpUpper.get()+","+self.kahpStep.get())
            
        if(self.howToChannelhc.get()=="constant"):
            Config.set("gridsearch","hc",self.hc.get())
        else:
            Config.set("gridsearch","hc", self.hcLower.get()+","+self.hcUpper.get()+","+self.hcStep.get())
            
        if(self.howToChannelhc.get()=="constant"):
            Config.set("gridsearch","alpha",self.alpha.get())
        else:
            Config.set("gridsearch","alpha", self.alphaLower.get()+","+self.alphaUpper.get()+","+self.alphaStep.get())    
        
        if(self.howToChannelkm.get()=="constant"):
            Config.set("gridsearch","km",self.km.get())
        else:
            Config.set("gridsearch","km", self.kmLower.get()+","+self.kmUpper.get()+","+self.kmStep.get())

        if(self.howToChannelnaf.get()=="constant"):
            Config.set("gridsearch","naf",self.naf.get())
        else:
            Config.set("gridsearch","naf", self.nafLower.get()+","+self.nafUpper.get()+","+self.nafStep.get())

        if(self.howToChannelnap.get()=="constant"):
            Config.set("gridsearch","nap",self.nap.get())
        else:
            Config.set("gridsearch","nap", self.nap.get()+","+self.napUpper.get()+","+self.napStep.get())

        if(self.howToChannelpas.get()=="constant"):
            Config.set("gridsearch","pas",self.pas.get())
        else:
            Config.set("gridsearch","pas", self.pasLower.get()+","+self.pasUpper.get()+","+self.pasStep.get())

    
        Config.write(self.configFile)
        self.configFile.close()
        p = subprocess.Popen(["python2.7", "start_sim.py", "-c", self.configFile.name], shell = False)
        showinfo("", "Optimation is running in process " + str(p.pid) + "\nThe GUI can be closed")
        
        #noch anpassen



# First Page. Appears after starting the GUI. Set global settings and choose
# an algorithm to optimize the conductance.

    # choosen values of the parameters are saved in
    # DebugValue
    # ThreadsValue
    # fileLogValue
    # consolelogValue
    # logServerPortValue
    
    
class ChooseAlgoPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        def loadConfigFileDialog():
            name= askopenfilename() 
            loadConfigFile(name)
            
        def loadConfigFile(config_file):
            global gconfig
            pconf = projconf.ProjectConfiguration(config_file = config_file)
            parser = pconf.cfg
            # Store globally to save the settings later
            gconfig = parser

            #Global Configs laden
            debugMode= parser.get('Global','debugMode')
            controller.debugValue.set(debugMode)
            maxSimThreads = parser.get('Global','maxSimThreads')
            controller.threadValue.set(maxSimThreads)
            file_log_level = parser.get('Logging','file_log_level')
            controller.filelogValue.set(file_log_level)
            console_log_level =  parser.get('Logging','console_log_level')
            controller.consolelogValue.set(console_log_level)
            mode= parser.get('Simulation', 'mode')
            controller.modeVar.set(mode)
            
            # load values for gentic algorithm
            thrFourier= parser.get('fitness.calc_fitness_candidates', 'thrFourier')
            controller.thrFourierValue.set(thrFourier)
            max_generations= parser.get('EvolveParameters', 'max_generations')
            controller.MaxGenerationValue.set(max_generations)
            pop_size= parser.get('EvolveParameters','pop_size')
            controller.popSizeValue.set(pop_size)
            tournament_size= parser.get('tournament_selection', 'tournament_size')
            controller.tournament_sizeValue.set(tournament_size)
            num_selected= parser.get('tournament_selection', 'num_selected')
            controller.num_selectedValue.set(num_selected)
            num_crossover_points= parser.get('n_point_crossover','num_crossover_points')
            controller.num_co_pointValue.set(num_crossover_points)
            crossover_rate= parser.get('n_point_crossover','crossover_rate')
            controller.crossover_rateValue.set(crossover_rate)
            mutation_strength= parser.get('nuMutation','mutation_strength')
            controller.mutation_strengthValue.set(mutation_strength)
            penFourier=parser.get('fitness.calc_fitness_candidates','penFourier')
            controller.penFourierValue.set(penFourier)
            penalty_ai_RS=parser.get('fitness.calc_fitness_candidates','penalty_ai_RS')
            controller.penalty_ai_RSValue.set(penalty_ai_RS)
            penalty_ai_FS=parser.get('fitness.calc_fitness_candidates','penalty_ai_FS')
            controller.penalty_ai_FSValue.set(penalty_ai_FS)
            penalty_ibf_IB=parser.get('fitness.calc_fitness_candidates','penalty_ibf_IB')
            controller.penalty_ibf_IBValue.set(penalty_ibf_IB)
            penalty_ibf_CH=parser.get('fitness.calc_fitness_candidates','penalty_ibf_CH')
            controller.penalty_ibf_CHValue.set(penalty_ibf_CH)
            penalty_ir_IB=parser.get('fitness.calc_fitness_candidates','penalty_ir_IB')
            controller.penalty_ir_IBValue.set(penalty_ir_IB)
            penalty_ir_CH=parser.get('fitness.calc_fitness_candidates','penalty_ir_CH')
            controller.penalty_ir_CHValue.set(penalty_ir_CH)
            W_apw=parser.get('fitness.calc_fitness_candidates','W_apw')
            controller.apwValue.set(W_apw)
            W_ibf=parser.get('fitness.calc_fitness_candidates','W_ibf')
            controller.ibfValue.set(W_ibf)
            W_ir=parser.get('fitness.calc_fitness_candidates','W_ir')
            controller.irValue.set(W_ir)
            W_ai=parser.get('fitness.calc_fitness_candidates','W_ai')
            controller.aiValue.set(W_ai)
            W_slope=parser.get('fitness.calc_fitness_candidates','W_slope')
            controller.slopeValue.set(W_slope)

            #load values for simulated annealing algorithm
            stepmax=parser.get('annealing','stepmax')
            start_temperature=parser.get('annealing','start_temperature')
            cooling_schedule=parser.get('annealing','cooling_schedule')
            cooling_schedule_alpha=parser.get('annealing','cooling_schedule_alpha')
            neighbour_count=parser.get('annealing','neighbour_count')
            controller.stepmaxValue.set(stepmax)
            controller.start_temperatureValue.set(start_temperature)
            controller.cooling_scheduleValue.set(cooling_schedule)
            controller.cooling_schedule_alphaValue.set(cooling_schedule_alpha)
            controller.neighbour_countValue.set(neighbour_count)

            #load values for gridsearch algorithm
            gridmode= parser.get('gridsearch','gridmode')
            controller.gridmodeValue.set(gridmode)


            # input: value
            arValue= parser.get('gridsearch', 'ar')
            arValueCheck= arValue.split(",")
            if(len(arValueCheck) == 1):
                controller.ar.set(arValue)
            elif(len(arValueCheck) == 3):
                controller.arUpper.set(arValueCheck[0])
                controller.arLower.set(arValueCheck[1])
                controller.arStep.set(arValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel ar!")

            calValue= parser.get('gridsearch', 'cal')
            calValueCheck= calValue.split(",")
            if(len(calValueCheck) == 1):
                controller.cal.set(calValue)
            elif(len(calValueCheck) == 3):
                controller.calUpper.set(calValueCheck[0])
                controller.calLower.set(calValueCheck[1])
                controller.calStep.set(calValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel cal!")

            catValue= parser.get('gridsearch', 'cat')
            catValueCheck= catValue.split(",")
            if(len(catValueCheck) == 1):
                controller.cat.set(catValue)
            elif(len(catValueCheck) == 3):
                controller.catUpper.set(catValueCheck[0])
                controller.catLower.set(catValueCheck[1])
                controller.catStep.set(catValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel cat!")

            k2Value= parser.get('gridsearch', 'k2')
            k2ValueCheck= k2Value.split(",")
            if(len(k2ValueCheck) == 1):
                controller.k2.set(k2Value)
            elif(len(k2ValueCheck) == 3):
                controller.k2Upper.set(k2ValueCheck[0])
                controller.k2Lower.set(k2ValueCheck[1])
                controller.k2Step.set(k2ValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel k2!")

            kaValue= parser.get('gridsearch', 'ka')
            kaValueCheck= kaValue.split(",")
            if(len(kaValueCheck) == 1):
                controller.ka.set(kaValue)
            elif(len(kaValueCheck) == 3):
                controller.kaUpper.set(kaValueCheck[0])
                controller.kaLower.set(kaValueCheck[1])
                controller.kaStep.set(kaValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel ka!")

            kahpValue= parser.get('gridsearch', 'kahp')
            kahpValueCheck= kahpValue.split(",")
            if(len(kahpValueCheck) == 1):
                controller.kahp.set(kahpValue)
            elif(len(kahpValueCheck) == 3):
                controller.kahpUpper.set(kahpValueCheck[0])
                controller.kahpLower.set(kahpValueCheck[1])
                controller.kahpStep.set(kahpValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel kahp!")

            hcValue= parser.get('gridsearch', 'hc')
            hcValueCheck= hcValue.split(",")
            if(len(hcValueCheck) == 1):
                controller.hc.set(hcValue)
            elif(len(hcValueCheck) == 3):
                controller.hcUpper.set(hcValueCheck[0])
                controller.hcLower.set(hcValueCheck[1])
                controller.hcStep.set(hcValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel hc!")

            alphaValue= parser.get('gridsearch', 'alpha')
            alphaValueCheck= alphaValue.split(",")
            if(len(alphaValueCheck) == 1):
                controller.alpha.set(alphaValue)
            elif(len(alphaValueCheck) == 3):
                controller.alphaUpper.set(alphaValueCheck[0])
                controller.alphaLower.set(alphaValueCheck[1])
                controller.alphaStep.set(alphaValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel alpha!")

            kmValue= parser.get('gridsearch', 'km')
            kmValueCheck= kmValue.split(",")
            if(len(kmValueCheck) == 1):
                controller.km.set(kmValue)
            elif(len(kmValueCheck) == 3):
                controller.kmUpper.set(kmValueCheck[0])
                controller.kmLower.set(kmValueCheck[1])
                controller.kmStep.set(kmValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel km!")

            nafValue= parser.get('gridsearch', 'naf')
            nafValueCheck= nafValue.split(",")
            if(len(nafValueCheck) == 1):
                controller.naf.set(nafValue)
            elif(len(nafValueCheck) == 3):
                controller.nafUpper.set(nafValueCheck[0])
                controller.nafLower.set(nafValueCheck[1])
                controller.nafStep.set(nafValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel naf!")

            napValue= parser.get('gridsearch', 'nap')
            napValueCheck= napValue.split(",")
            if(len(napValueCheck) == 1):
                controller.nap.set(napValue)
            elif(len(napValueCheck) == 3):
                controller.napUpper.set(napValueCheck[0])
                controller.napLower.set(napValueCheck[1])
                controller.napStep.set(napValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel nap!")

            pasValue= parser.get('gridsearch', 'pas')
            pasValueCheck= pasValue.split(",")
            if(len(pasValueCheck) == 1):
                controller.pas.set(pasValue)
            elif(len(pasValueCheck) == 3):
                controller.pasUpper.set(pasValueCheck[0])
                controller.pasLower.set(pasValueCheck[1])
                controller.pasStep.set(pasValueCheck[2])
            else:
                raise RuntimeError("Invalid parameters for channel pas!")


        loadConfigFile("default.cfg")
        
        label = tk.Label(self, text=" How do you want to optimize the conductance of the ion channels?", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)


        openButton= tk.Button(self, text='Load Config', command=loadConfigFileDialog, bd=4, padx=6, pady=8)
        openButton.pack()

        globalParaFrame = tk.LabelFrame(self, text="Set System Settings")
        globalParaFrame.pack(fill="both", expand="yes")

        debugLabel = tk.Label(globalParaFrame, text="Debug Mode?")
        debugCheckButton = tk.Checkbutton(globalParaFrame, variable = controller.debugValue, onvalue = 1, offvalue = 0)
        debugLabel.pack()
        debugCheckButton.pack()

        
        ThreadLabel= tk.Label(globalParaFrame, text="Simultaneous Threads")
        ThreadsEntry = tk.Entry(globalParaFrame, textvariable= controller.threadValue)
        ThreadLabel.pack()
        ThreadsEntry.pack()
        
        
        filelogLabel= tk.Label(globalParaFrame, text="Filtering level for the logging file")
        filelogLabel.pack()

        filelogFrame = tk.Frame(globalParaFrame)
        filelogFrame.pack()
        
        AnythingFile = tk.Radiobutton(filelogFrame, text="Anything", variable=controller.filelogValue, value=1)
        AnythingFile.grid(row =0, column=0)
        INFOFile = tk.Radiobutton(filelogFrame, text="Infos", variable=controller.filelogValue, value=20)
        INFOFile.grid(row =0, column=1)
        WARNINGFile = tk.Radiobutton(filelogFrame, text="Warnings", variable=controller.filelogValue, value=30)
        WARNINGFile.grid(row =0, column=2)
        CRITICALFile = tk.Radiobutton(filelogFrame, text="Criticals", variable=controller.filelogValue, value=50)
        CRITICALFile.grid(row =0, column=3)

        
        
        consolelogLabel= tk.Label(globalParaFrame, text="Filtering level for the console")
        consolelogLabel.pack()
        
        consolelogFrame= tk.Frame(globalParaFrame)
        consolelogFrame.pack()

        AnythingConsole = tk.Radiobutton(consolelogFrame, text="Anything", variable=controller.consolelogValue, value=1)
        AnythingConsole.grid(row =0, column=0)
        INFOConsole = tk.Radiobutton(consolelogFrame, text="Infos", variable=controller.consolelogValue, value=20)
        INFOConsole.grid(row =0, column=1)
        WARNINGConsole = tk.Radiobutton(consolelogFrame, text="Warnings", variable=controller.consolelogValue, value=30)
        WARNINGConsole.grid(row =0, column=2)
        CRITICALConsole = tk.Radiobutton(consolelogFrame, text="Criticals", variable=controller.consolelogValue, value=50)
        CRITICALConsole.grid(row =0, column=3)

        

        SimulationFrame = tk.LabelFrame(self, text= "Simulation")
        SimulationFrame.pack(fill="both", expand="yes")

        modeLabel= tk.Label(SimulationFrame, text="Which kind of neurons do you want to optimize?")
        modeLabel.pack()

        kindOfNeuronsFrame = tk.Frame(SimulationFrame)
        kindOfNeuronsFrame.pack()
        
        RS = tk.Radiobutton(kindOfNeuronsFrame, text="Regular Spiking", variable=controller.modeVar, value="RS")
        RS.grid(row =0, column=0)
        FS = tk.Radiobutton(kindOfNeuronsFrame, text="Fast Spiking", variable=controller.modeVar, value="FS")
        FS.grid(row =0, column=1)
        IB = tk.Radiobutton(kindOfNeuronsFrame, text="Intrinsic Bursting", variable=controller.modeVar, value="IB")
        IB.grid(row =0, column=2)
        CH = tk.Radiobutton(kindOfNeuronsFrame, text="Chattering Bursting", variable=controller.modeVar, value="CH")
        CH.grid(row =0, column=3)

        
        thrFourierLabel = tk.Label(SimulationFrame, text="Fourier")
        thrFourierLabel.pack()
        thrFourierEntry = tk.Entry(SimulationFrame, textvariable= controller.thrFourierValue)
        thrFourierEntry.pack()
        
        #chooseAlgoFrame contains the Genetic Algorithm Button, Simulated Annealing Button and the Gridsearch Button
        chooseAlgoFrame = tk.LabelFrame(self, text="Choose Algorithm")
        chooseAlgoFrame.pack(fill="both", expand="yes")

        button1 = tk.Button(chooseAlgoFrame, text="Genetic Algorithm", 
                            command=lambda: controller.show_frame(EvoluParameterPage))
        button2 = tk.Button(chooseAlgoFrame, text="Simulated Annealing",
                            command=lambda: controller.show_frame(SimulatedAnnealingPage))

        button3 = tk.Button(chooseAlgoFrame, text="Gridsearch",
                            command=lambda: controller.show_frame(GridsearchPage))
        
        button1.pack(pady=10)
        button2.pack(pady=10)
        button3.pack(pady=10)

        



# Page to set the parameter for the genetic algorithm and start the program

    # choosen values of the parameters are saved in
    # modeVar
    # popSizeValue
    # MaxGenerationValue
    # thrFourierValue
    # penFourierValue
    # penalty_ai_RSValue
    # penalty_ai_FSValue
    # penalty_ibf_IBValue
    # penalty_ibf_CHValue
    # penalty_ir_IBValue
    # penalty_ir_CHValue
    # num_selectedValue
    # num_co_pointValue
    # mutation_strengthValue
    # num_elitesValue
    # tournament_sizeValue
    # crossover_rateValue
    # apwValue
    # ibfValue
    # irValue
    # aiValue
    # slopeValue


class EvoluParameterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        
        label = tk.Label(self, text="Set Parameter for the Genetic Algorithm", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        
        button = tk.Button(self, text="Go to the start page", 
                           command=lambda: controller.show_frame(ChooseAlgoPage))
        button.pack()

    
        #different Frames nested for layout purposes
        evolveFrame= tk.LabelFrame(self, text="Evolve Parameters")
        evolveFrame.pack(fill="both", expand="yes")
        evolveLayoutFrame= tk.Frame(evolveFrame)
        evolveLayoutFrame.pack()
        
        MaxGenerationLabel = tk.Label(evolveLayoutFrame, text="Maximum Generations")
        MaxGenerationLabel.grid(row=0, column=0)
        MaxGenerationEntry= tk.Entry(evolveLayoutFrame, textvariable = controller.MaxGenerationValue)
        MaxGenerationEntry.grid(row=1, column=0)
        Pop_Size_Label = tk.Label(evolveLayoutFrame, text="Population Size")
        Pop_Size_Label.grid(row=0, column=1)
        Pop_Size_Entry = tk.Entry(evolveLayoutFrame, textvariable = controller.popSizeValue)
        Pop_Size_Entry.grid(row=1, column=1)

        #different Frames nested for layout purposes
        selectorFrame= tk.LabelFrame(self, text="Selectors")
        selectorFrame.pack(fill="both", expand="yes")
        selectorFrame.pack()
        selectorLayoutFrame= tk.Frame(selectorFrame)
        selectorLayoutFrame.pack()

        tournament_selection= tk.Radiobutton(selectorLayoutFrame, text="Tournament Selection", variable= controller.selectorChoice, value="tournament_selection")
        fitness_proportionate_selection= tk.Radiobutton(selectorLayoutFrame,text="Fitness Proportionate", variable= controller.selectorChoice, value="fitness_proportionate_selection")
        tournamentSelectionLabel= tk.Label(selectorLayoutFrame, text="Tournament Selection")
        tournament_sizeLabel= tk.Label(selectorLayoutFrame, text="Tournament Size")
        tournament_sizeEntry=tk.Entry(selectorLayoutFrame, textvariable= controller.tournament_sizeValue)
        num_selectedLabel= tk.Label(selectorLayoutFrame, text="Numbers  of Selected")
        num_selectedEntry= tk.Entry(selectorLayoutFrame, textvariable= controller.num_selectedValue)
        num_selectedFitnessProportionateLabel= tk.Label(selectorLayoutFrame, text="Numbers  of Selected")
        num_selectedFitnessProportionateEntry= tk.Entry(selectorLayoutFrame, textvariable= controller.num_selectedValue)

        tournament_selection.grid(row=0, column=0)
        fitness_proportionate_selection.grid(row=2, column=0)
        num_selectedLabel.grid(row=0, column=1)
        num_selectedEntry.grid(row=1, column=1)
        num_selectedFitnessProportionateLabel.grid(row=2, column=1)
        num_selectedFitnessProportionateEntry.grid(row=3, column=1)
        tournament_sizeLabel.grid(row=0, column=2)
        tournament_sizeEntry.grid(row=1, column=2)
        

        #different Frames nested for layout purposes
        variatorFrame= tk.LabelFrame(self, text="Variators")
        variatorFrame.pack(fill="both", expand="yes")
        variatorLayoutFrame= tk.Frame(variatorFrame)
        variatorLayoutFrame.pack()
        
        n_point_crossoverRadiobutton = tk.Radiobutton(variatorLayoutFrame, text="n Point Crossover", variable= controller.variatorChoice, value="n_point_crossover")
        nuMutationRadiobutton= tk.Radiobutton(variatorLayoutFrame, text="Nu Mutation", variable= controller.variatorChoice, value="nuMutation")

        num_co_pointLabel= tk.Label(variatorLayoutFrame, text="Numbers  of Crossover Points")
        num_co_pointEntry= tk.Entry(variatorLayoutFrame, textvariable= controller.num_co_pointValue)
        crossover_rateLabel = tk.Label(variatorLayoutFrame, text="Crossover Rate")
        crossover_rateEntry = tk.Entry(variatorLayoutFrame, textvariable= controller.crossover_rateValue)
        mutation_strengthLabel= tk.Label(variatorLayoutFrame, text="Mutation Strength")
        mutation_strengthEntry= tk.Entry(variatorLayoutFrame, textvariable= controller.mutation_strengthValue)

        n_point_crossoverRadiobutton.grid(row=0, column=0)
        nuMutationRadiobutton.grid(row=2, column=0)
        crossover_rateLabel.grid(row=0, column=1)
        crossover_rateEntry.grid(row=1, column=1)
        mutation_strengthLabel.grid(row=2, column=1)
        mutation_strengthEntry.grid(row=3, column=1)
        num_co_pointLabel.grid(row=2, column=2)
        num_co_pointEntry.grid(row=3, column=2)
        
        
        replacerFrame= tk.LabelFrame(self, text="Replacer")
        replacerFrame.pack(fill="both", expand="yes")
        replacerLayoutFrame= tk.Frame(replacerFrame)
        replacerLayoutFrame.pack()

        truncationRadiobutton= tk.Radiobutton(replacerLayoutFrame, text="Truncation Replacement", variable= controller.replacerChoice, value="truncation_replacement")
        randomRadiobutton= tk.Radiobutton(replacerLayoutFrame, text="Random Replacement", variable=controller.replacerChoice, value="random_replacement")
        eliteLabel= tk.Label(replacerLayoutFrame, text="Number of Elites")
        eliteEntry= tk.Entry(replacerLayoutFrame, text="Number of Elites", textvariable= controller.numElitesValue)
        truncationRadiobutton.grid(row=0, column=0)
        randomRadiobutton.grid(row=1, column=0)
        eliteLabel.grid(row=1,column=1)
        eliteEntry.grid(row=2,column=1)

        
        evaluatorFrame= tk.LabelFrame(self, text= "Fitnes Evaluator Parameters")
        evaluatorFrame.pack(fill="both", expand="yes")
        penaltyFrame=tk.Frame(evaluatorFrame)
        penaltyFrame.pack()
        penFourierLabel= tk.Label(penaltyFrame, text="Penalty Fourier")
        penalty_ai_RSLabel = tk.Label(penaltyFrame, text="Penalty Adaptionsindex for Regular Spiking neurons")
        penalty_ai_FSLabel = tk.Label(penaltyFrame, text="Penalty Adaptionsindex for Fast Spiking neurons")
        penalty_ibf_IBLabel =tk.Label(penaltyFrame, text="Panelty Intraburst Frequence for Intrinsic Bursting neurons")
        penalty_ibf_CHLabel = tk.Label(penaltyFrame, text="Penalty Intraburst Frequence rythmic Bursting neurons")
        penalty_ir_IBLabel = tk.Label(penaltyFrame, text=" Penalty inactivation rate for Intrinsic Bursting neurons")
        penalty_ir_CHLabel = tk.Label(penaltyFrame, text=" Penalty inactivation rate rhythmic Bursting neurons")
        penFourierEntry= tk.Entry(penaltyFrame, textvariable=  controller.penFourierValue)
        penalty_ai_RSEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ai_RSValue)
        penalty_ai_FSEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ai_FSValue)
        penalty_ibf_IBEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ibf_IBValue)
        penalty_ibf_CHEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ibf_CHValue)
        penalty_ir_IBEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ir_IBValue)
        penalty_ir_CHEntry= tk.Entry(penaltyFrame, textvariable= controller.penalty_ir_CHValue)
        penFourierLabel.grid(row = 0, column = 0)
        penFourierEntry.grid(row = 1, column = 0)
        penalty_ai_RSLabel.grid(row = 0, column = 1)
        penalty_ai_RSEntry.grid(row = 1, column = 1)
        penalty_ai_FSLabel.grid(row = 2, column = 0)
        penalty_ai_FSEntry.grid(row = 3, column = 0 )
        penalty_ibf_IBLabel.grid(row = 2, column = 1)
        penalty_ibf_IBEntry.grid(row = 3, column = 1)
        penalty_ibf_CHLabel.grid(row = 4, column = 0)
        penalty_ibf_CHEntry.grid(row = 5, column = 0)
        penalty_ir_IBLabel.grid(row = 4, column = 1)
        penalty_ir_IBEntry.grid(row = 5, column = 1)
        penalty_ir_CHLabel.grid(row = 6, column = 0)
        penalty_ir_CHEntry.grid(row = 7, column = 0)

        weightFrame= tk.Frame(evaluatorFrame)
        weightFrame.pack()
        apwLabel =tk.Label(weightFrame, text="weight of apw")
        ibfLabel= tk.Label(weightFrame, text="weight of ibf")
        irLabel= tk.Label(weightFrame, text="weight of ir")
        aiLabel= tk.Label(weightFrame,  text="weight of ai")
        slopeLabel= tk.Label(weightFrame, text="weight of slope")

        apwEntry = tk.Entry(weightFrame, textvariable= controller.apwValue)
        ibfEntry = tk.Entry(weightFrame, textvariable= controller.ibfValue)
        irEntry = tk.Entry(weightFrame, textvariable= controller.irValue)
        aiEntry = tk.Entry(weightFrame, textvariable= controller.aiValue)
        slopeEntry = tk.Entry(weightFrame, textvariable= controller.slopeValue)
        apwLabel.grid(row=0, column=0)
        apwEntry.grid(row=1, column=0)
        ibfLabel.grid(row=0, column=1)
        ibfEntry.grid(row=1, column=1)
        irLabel.grid(row=0, column=2)
        irEntry.grid(row=1, column=2)
        aiLabel.grid(row=2, column=0)
        aiEntry.grid(row=3, column=0)
        slopeLabel.grid(row=2, column=1)
        slopeEntry.grid(row=3, column=1)
    
    

        def startGeneticAlgorithm():
            controller.algorithm.set("genetic")
            controller.start()
    
    
            
        startSimulationButton = tk.Button(self, text="Start the Simulation",command=startGeneticAlgorithm)
        startSimulationButton.pack(side= tk.BOTTOM)



 

# Page to set the parameter for the simulated annealing algorithm and start the program

    # choosen values of the parameters are saved in
    #
    # stepmaxValue
    # start_temperatureValue
    # cooling_scheduleValue
    # If cooling_scheduleValue = 2 which means exponential
    # then cooling_schedule_alphaValue has to read too
    

class SimulatedAnnealingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        
        def disableCooling_schedule_alpha():
            cooling_schedule_alphaLabel.configure(state='disabled')
            cooling_schedule_alphaEntry.configure(state='disabled')

        def activateCooling_schedule_alpha():
            cooling_schedule_alphaLabel.configure(state='normal')
            cooling_schedule_alphaEntry.configure(state='normal')



        label = tk.Label(self, text="Set Parameter for Simulated Annealing", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page", 
                           command=lambda: controller.show_frame(ChooseAlgoPage))
        button.pack()


        variableFrame=tk.LabelFrame(self, text="Temperature and  Duration")
        variableFrame.pack(fill="both", expand="yes")
        
        stepmaxLabel= tk.Label(variableFrame, text= "Step Maximum")
        stepmaxEntry= tk.Entry(variableFrame, textvariable= controller.stepmaxValue)
        stepmaxLabel.pack()
        stepmaxEntry.pack()


        start_temperatureLabel= tk.Label(variableFrame, text="Start Temperature")
        start_temperatureEntry= tk.Entry(variableFrame, textvariable= controller.start_temperatureValue)
        start_temperatureLabel.pack()
        start_temperatureEntry.pack()

        #different Frames nested for layout purposes
        coolingScheduleFrame= tk.LabelFrame(self, text="Cooling Schedule")
        coolingScheduleFrame.pack(fill="both", expand="yes")
        coolingScheduleLayoutFrame= tk.Frame(coolingScheduleFrame)
        coolingScheduleLayoutFrame.pack()
        
        
        linear= tk.Radiobutton(coolingScheduleLayoutFrame, text="Linear", variable= controller.cooling_scheduleValue, value= "linear", command= disableCooling_schedule_alpha)
        linear.grid(row=0, column=0)
        exponential= tk.Radiobutton(coolingScheduleLayoutFrame, text="Exponential", variable = controller.cooling_scheduleValue, value= "exponential", command= activateCooling_schedule_alpha)
        exponential.grid(row=0, column=1)
        
        
        cooling_schedule_alphaLabel= tk.Label(coolingScheduleFrame, text="Parameter [0,1] for exponential cooling schedule")
        cooling_schedule_alphaLabel.pack()
        cooling_schedule_alphaEntry= tk.Entry(coolingScheduleFrame, textvariable= controller.cooling_schedule_alphaValue)
        cooling_schedule_alphaEntry.pack()

        neighbour_countLabel= tk.Label(coolingScheduleFrame, text="Neighbour Count")
        neighbour_countEntry= tk.Entry(coolingScheduleFrame, textvariable=controller.neighbour_countValue)
        neighbour_countLabel.pack()
        neighbour_countEntry.pack()



        def callback(*args):

            if (controller.cooling_scheduleValue.get() =="linear"):
                disableCooling_schedule_alpha()
                print "changed"
                
            else:
                activateCooling_schedule_alpha()
                

        controller.cooling_scheduleValue.trace("w", callback)
                    
             
            
        def startSimulatedAnnealing():
            controller.algorithm.set("annealing")
            controller.start()
            
                
        #save value with this button and exec start_sim.py
        startSimulationButton = tk.Button(self, text="Start the Simulation", command= startSimulatedAnnealing)
        startSimulationButton.pack(side= tk.BOTTOM)


        
        
#Page to set the parameter for the gridsearch algorithm and start the program
        
    # choosen values of the parameters are saved in
    # gridmodeValue
    # different channels
    
class GridsearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Set Parameter for the Gridsearch", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        
        #Button to get back to the startpage
        button = tk.Button(self, text="Go to the start page", 
                           command=lambda: controller.show_frame(ChooseAlgoPage))
        button.pack()


        gridModeFrame= tk.LabelFrame(self, text="Cooling Schedule")
        gridModeFrame.pack(fill="both", expand="yes")
        gridModeFrameLayout= tk.Frame(gridModeFrame)
        gridModeFrameLayout.pack()

        linear= tk.Radiobutton(gridModeFrameLayout, text="Linear", variable= controller.gridmodeValue, value= "linear")
        linear.grid(row=0, column=0)
        exponential= tk.Radiobutton(gridModeFrameLayout, text="Exponential", variable = controller.gridmodeValue, value= "exponential")
        exponential.grid(row=0, column=1)
        
        #different Frames nested for layout purposes
        channelFrame= tk.LabelFrame(self, text="Channel Values")
        channelFrame.pack(fill="both", expand="yes")
        channelFrameRow1= tk.Frame(channelFrame)
        channelFrameRow1.pack()
        channelFrameRow2= tk.Frame(channelFrame)
        channelFrameRow2.pack()
        channelFrameRow3= tk.Frame(channelFrame)
        channelFrameRow3.pack()
        channelFrameRow4= tk.Frame(channelFrame)
        channelFrameRow4.pack()

        #define the widgets for the channels
        arLabel= tk.Label(channelFrameRow1, text="ar")
        calLabel= tk.Label(channelFrameRow1, text="cal")
        catLabel= tk.Label(channelFrameRow1, text="cat")
        k2Label= tk.Label(channelFrameRow2, text="k2")
        kaLabel= tk.Label(channelFrameRow2, text="ka")
        kahpLabel= tk.Label(channelFrameRow2, text="kahp")
        hcLabel= tk.Label(channelFrameRow3, text="hc")
        alphaLabel= tk.Label(channelFrameRow3, text="alpha")
        kmLabel= tk.Label(channelFrameRow3, text="km")
        nafLabel= tk.Label(channelFrameRow4, text="naf")
        napLabel= tk.Label(channelFrameRow4, text="nap")
        pasLabel= tk.Label(channelFrameRow4, text="pas")
        
        arEntry= tk.Entry(channelFrameRow1,textvariable=controller.ar ,text="ar")
        calEntry= tk.Entry(channelFrameRow1,textvariable=controller.cal ,text="cal")
        catEntry= tk.Entry(channelFrameRow1,textvariable=controller.cat ,text="cat")
        k2Entry= tk.Entry(channelFrameRow2,textvariable=controller.k2 ,text="k2")
        kaEntry= tk.Entry(channelFrameRow2,textvariable=controller.ka ,text="ka")
        kahpEntry= tk.Entry(channelFrameRow2,textvariable=controller.kahp ,text="kahp")
        hcEntry= tk.Entry(channelFrameRow3,textvariable=controller.hc ,text="hc")
        alphaEntry= tk.Entry(channelFrameRow3,textvariable=controller.alpha ,text="alpha")
        kmEntry= tk.Entry(channelFrameRow3,textvariable=controller.km ,text="km")
        nafEntry= tk.Entry(channelFrameRow4,textvariable=controller.naf ,text="naf")
        napEntry= tk.Entry(channelFrameRow4,textvariable=controller.nap ,text="nap")
        pasEntry= tk.Entry(channelFrameRow4,textvariable=controller.pas ,text="pas")
        
        arUpperEntry= tk.Entry(channelFrameRow1,textvariable=controller.arUpper)
        calUpperEntry= tk.Entry(channelFrameRow1,textvariable=controller.calUpper)
        catUpperEntry= tk.Entry(channelFrameRow1,textvariable=controller.catUpper)
        k2UpperEntry= tk.Entry(channelFrameRow2,textvariable=controller.k2Upper)
        kaUpperEntry= tk.Entry(channelFrameRow2,textvariable=controller.kaUpper)
        kahpUpperEntry= tk.Entry(channelFrameRow2,textvariable=controller.kahpUpper)
        hcUpperEntry= tk.Entry(channelFrameRow3,textvariable=controller.hcUpper)
        alphaUpperEntry= tk.Entry(channelFrameRow3,textvariable=controller.alphaUpper)
        kmUpperEntry= tk.Entry(channelFrameRow3,textvariable=controller.kmUpper)
        nafUpperEntry= tk.Entry(channelFrameRow4,textvariable=controller.nafUpper)
        napUpperEntry= tk.Entry(channelFrameRow4,textvariable=controller.napUpper)
        pasUpperEntry= tk.Entry(channelFrameRow4,textvariable=controller.pasUpper)
        
        arLowerEntry= tk.Entry(channelFrameRow1,textvariable=controller.arLower ,text="ar")
        calLowerEntry= tk.Entry(channelFrameRow1,textvariable=controller.calLower ,text="cal")
        catLowerEntry= tk.Entry(channelFrameRow1,textvariable=controller.catLower ,text="cat")
        k2LowerEntry= tk.Entry(channelFrameRow2,textvariable=controller.k2Lower ,text="k2")
        kaLowerEntry= tk.Entry(channelFrameRow2,textvariable=controller.kaLower ,text="ka")
        kahpLowerEntry= tk.Entry(channelFrameRow2,textvariable=controller.kahpLower ,text="kahp")
        hcLowerEntry= tk.Entry(channelFrameRow3,textvariable=controller.hcLower ,text="hc")
        alphaLowerEntry= tk.Entry(channelFrameRow3,textvariable=controller.alphaLower ,text="alpha")
        kmLowerEntry= tk.Entry(channelFrameRow3,textvariable=controller.kmLower ,text="km")
        nafLowerEntry= tk.Entry(channelFrameRow4,textvariable=controller.nafLower ,text="naf")
        napLowerEntry= tk.Entry(channelFrameRow4,textvariable=controller.napLower ,text="nap")
        pasLowerEntry= tk.Entry(channelFrameRow4,textvariable=controller.pasLower ,text="pas")
        
        arStepEntry= tk.Entry(channelFrameRow1,textvariable=controller.arStep ,text="ar")
        calStepEntry= tk.Entry(channelFrameRow1,textvariable=controller.calStep ,text="cal")
        catStepEntry= tk.Entry(channelFrameRow1,textvariable=controller.catStep ,text="cat")
        k2StepEntry= tk.Entry(channelFrameRow2,textvariable=controller.k2Step ,text="k2")
        kaStepEntry= tk.Entry(channelFrameRow2,textvariable=controller.kaStep ,text="ka")
        kahpStepEntry= tk.Entry(channelFrameRow2,textvariable=controller.kahpStep ,text="kahp")
        hcStepEntry= tk.Entry(channelFrameRow3,textvariable=controller.hcStep ,text="hc")
        alphaStepEntry= tk.Entry(channelFrameRow3,textvariable=controller.alphaStep ,text="alpha")
        kmStepEntry= tk.Entry(channelFrameRow3,textvariable=controller.kmStep,text="km")
        nafStepEntry= tk.Entry(channelFrameRow4,textvariable=controller.nafStep ,text="naf")
        napStepEntry= tk.Entry(channelFrameRow4,textvariable=controller.napStep ,text="nap")
        pasStepEntry= tk.Entry(channelFrameRow4,textvariable=controller.pasStep ,text="pas")

        arLabelLow= tk.Label(channelFrameRow1,text="      Lower Bound")
        arLabelStepSize = tk.Label(channelFrameRow1,text="Step Size")
        calLabelLow= tk.Label(channelFrameRow1,text="      Lower Bound")
        calLabelStepSize = tk.Label(channelFrameRow1,text="Step Size")
        catLabelLow= tk.Label(channelFrameRow1,text="      Lower Bound")
        catLabelStepSize = tk.Label(channelFrameRow1,text="Step Size")
        k2LabelLow= tk.Label(channelFrameRow2,text="      Lower Bound")
        k2LabelStepSize = tk.Label(channelFrameRow2,text="Step Size")
        kaLabelLow= tk.Label(channelFrameRow2,text="      Lower Bound")
        kaLabelStepSize = tk.Label(channelFrameRow2,text="Step Size")
        kahpLabelLow= tk.Label(channelFrameRow2,text="      Lower Bound")
        kahpLabelStepSize = tk.Label(channelFrameRow2,text="Step Size")
        hcLabelLow= tk.Label(channelFrameRow3,text="      Lower Bound")
        hcLabelStepSize = tk.Label(channelFrameRow3,text="Step Size")
        alphaLabelLow= tk.Label(channelFrameRow3,text="      Lower Bound")
        alphaLabelStepSize = tk.Label(channelFrameRow3,text="Step Size")
        kmLabelLow= tk.Label(channelFrameRow3,text="      Lower Bound")
        kmLabelStepSize = tk.Label(channelFrameRow3,text="Step Size")
        nafLabelLow= tk.Label(channelFrameRow4,text="      Lower Bound")
        nafLabelStepSize = tk.Label(channelFrameRow4,text="Step Size")
        napLabelLow= tk.Label(channelFrameRow4,text="      Lower Bound")
        napLabelStepSize = tk.Label(channelFrameRow4,text="Step Size")
        pasLabelLow= tk.Label(channelFrameRow4,text="      Lower Bound")
        pasLabelStepSize = tk.Label(channelFrameRow4,text="Step Size")
        

        #Put the widgets on the grid
        arconstantRadiobutton= tk.Radiobutton(channelFrameRow1, text="Constant Values", variable =controller.howToChannelar, value="constant")
        arboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow1, text="  Upper Bound   ", variable =controller.howToChannelar, value="bounds")
        arLabel.grid(row=0, column=1)
        arconstantRadiobutton.grid(row=1, column=0)
        arEntry.grid(row=1, column=1)
        arboundAndStepsizeRadiobutton.grid(row=2, column=0)
        arUpperEntry.grid(row=2, column=1)
        arLabelLow.grid(row=3, column=0)
        arLowerEntry.grid(row=3, column=1)
        arLabelStepSize.grid(row=4, column=0)
        arStepEntry.grid(row=4, column=1)
        
        calconstantRadiobutton= tk.Radiobutton(channelFrameRow1, text="Constant Values", variable =controller.howToChannelcal, value="constant")
        calboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow1, text="  Upper Bound   ", variable =controller.howToChannelcal, value="bounds")
        calLabel.grid(row=0, column=3)
        calconstantRadiobutton.grid(row=1, column=2)
        calEntry.grid(row=1, column=3)
        calboundAndStepsizeRadiobutton.grid(row=2, column=2)
        calUpperEntry.grid(row=2, column=3)
        calLabelLow.grid(row=3, column=2)
        calLowerEntry.grid(row=3, column=3)
        calLabelStepSize.grid(row=4, column=2)
        calStepEntry.grid(row=4, column=3)
        
        catconstantRadiobutton= tk.Radiobutton(channelFrameRow1, text="Constant Values", variable =controller.howToChannelcat, value="constant")
        catboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow1, text="  Upper Bound   ", variable =controller.howToChannelcat, value="bounds")
        catLabel.grid(row=0, column=5)
        catconstantRadiobutton.grid(row=1, column=4)
        catEntry.grid(row=1, column=5)
        catboundAndStepsizeRadiobutton.grid(row=2, column=4)
        catUpperEntry.grid(row=2, column=5)
        catLabelLow.grid(row=3, column=4)
        catLowerEntry.grid(row=3, column=5)
        catLabelStepSize.grid(row=4, column=4)
        catStepEntry.grid(row=4, column=5)

        k2constantRadiobutton= tk.Radiobutton(channelFrameRow2, text="Constant Values", variable =controller.howToChannelk2, value="constant")
        k2boundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow2, text="  Upper Bound   ", variable =controller.howToChannelk2, value="bounds")
        k2Label.grid(row=0, column=1)
        k2constantRadiobutton.grid(row=1, column=0)
        k2Entry.grid(row=1, column=1)
        k2boundAndStepsizeRadiobutton.grid(row=2, column=0)
        k2UpperEntry.grid(row=2, column=1)
        k2LabelLow.grid(row=3, column=0)
        k2LowerEntry.grid(row=3, column=1)
        k2LabelStepSize.grid(row=4, column=0)
        k2StepEntry.grid(row=4, column=1)
        
        kaconstantRadiobutton= tk.Radiobutton(channelFrameRow2, text="Constant Values", variable =controller.howToChannelka, value="constant")
        kaboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow2, text="  Upper Bound   ", variable =controller.howToChannelka, value="bounds")
        kaLabel.grid(row=0, column=3)
        kaconstantRadiobutton.grid(row=1, column=2)
        kaEntry.grid(row=1, column=3)
        kaboundAndStepsizeRadiobutton.grid(row=2, column=2)
        kaUpperEntry.grid(row=2, column=3)
        kaLabelLow.grid(row=3, column=2)
        kaLowerEntry.grid(row=3, column=3)
        kaLabelStepSize.grid(row=4, column=2)
        kaStepEntry.grid(row=4, column=3)

        kahpconstantRadiobutton= tk.Radiobutton(channelFrameRow2, text="Constant Values", variable =controller.howToChannelkahp, value="constant")
        kahpboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow2, text="  Upper Bound   ", variable =controller.howToChannelkahp, value="bounds")
        kahpLabel.grid(row=0, column=5)
        kahpconstantRadiobutton.grid(row=1, column=4)
        kahpEntry.grid(row=1, column=5)
        kahpboundAndStepsizeRadiobutton.grid(row=2, column=4)
        kahpUpperEntry.grid(row=2, column=5)
        kahpLabelLow.grid(row=3, column=4)
        kahpLowerEntry.grid(row=3, column=5)
        kahpLabelStepSize.grid(row=4, column=4)
        kahpStepEntry.grid(row=4, column=5)
        
        hcconstantRadiobutton= tk.Radiobutton(channelFrameRow3, text="Constant Values", variable =controller.howToChannelhc, value="constant")
        hcboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow3, text="  Upper Bound   ", variable =controller.howToChannelhc, value="bounds")
        hcLabel.grid(row=0, column=1)
        hcconstantRadiobutton.grid(row=1, column=0)
        hcEntry.grid(row=1, column=1)
        hcboundAndStepsizeRadiobutton.grid(row=2, column=0)
        hcUpperEntry.grid(row=2, column=1)
        hcLabelLow.grid(row=3, column=0)
        hcLowerEntry.grid(row=3, column=1)
        hcLabelStepSize.grid(row=4, column=0)
        hcStepEntry.grid(row=4, column=1)
        
        alphaconstantRadiobutton= tk.Radiobutton(channelFrameRow3, text="Constant Values", variable =controller.howToChannelalpha, value="constant")
        alphaboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow3, text="  Upper Bound   ", variable =controller.howToChannelalpha, value="bounds")
        alphaLabel.grid(row=0, column=3)
        alphaconstantRadiobutton.grid(row=1, column=2)
        alphaEntry.grid(row=1, column=3)
        alphaboundAndStepsizeRadiobutton.grid(row=2, column=2)
        alphaUpperEntry.grid(row=2, column=3)
        alphaLabelLow.grid(row=3, column=2)
        alphaLowerEntry.grid(row=3, column=3)
        alphaLabelStepSize.grid(row=4, column=2)
        alphaStepEntry.grid(row=4, column=3)

        kmconstantRadiobutton= tk.Radiobutton(channelFrameRow3, text="Constant Values", variable =controller.howToChannelkm, value="constant")
        kmboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow3, text="  Upper Bound   ", variable =controller.howToChannelkm, value="bounds")
        kmLabel.grid(row=0, column=5)
        kmconstantRadiobutton.grid(row=1, column=4)
        kmEntry.grid(row=1, column=5)
        kmboundAndStepsizeRadiobutton.grid(row=2, column=4)
        kmUpperEntry.grid(row=2, column=5)
        kmLabelLow.grid(row=3, column=4)
        kmLowerEntry.grid(row=3, column=5)
        kmLabelStepSize.grid(row=4, column=4)
        kmStepEntry.grid(row=4, column=5)
        
        nafconstantRadiobutton= tk.Radiobutton(channelFrameRow4, text="Constant Values", variable =controller.howToChannelnaf, value="constant")
        nafboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow4, text="  Upper Bound   ", variable =controller.howToChannelnaf, value="bounds")
        nafLabel.grid(row=0, column=1)
        nafconstantRadiobutton.grid(row=1, column=0)
        nafEntry.grid(row=1, column=1)
        nafboundAndStepsizeRadiobutton.grid(row=2, column=0)
        nafUpperEntry.grid(row=2, column=1)
        nafLabelLow.grid(row=3, column=0)
        nafLowerEntry.grid(row=3, column=1)
        nafLabelStepSize.grid(row=4, column=0)
        nafStepEntry.grid(row=4, column=1)

        napconstantRadiobutton= tk.Radiobutton(channelFrameRow4, text="Constant Values", variable =controller.howToChannelnap, value="constant")
        napboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow4, text="  Upper Bound   ", variable =controller.howToChannelnap, value="bounds")
        napLabel.grid(row=0, column=3)
        napconstantRadiobutton.grid(row=1, column=2)
        napEntry.grid(row=1, column=3)
        napboundAndStepsizeRadiobutton.grid(row=2, column=2)
        napUpperEntry.grid(row=2, column=3)
        napLabelLow.grid(row=3, column=2)
        napLowerEntry.grid(row=3, column=3)
        napLabelStepSize.grid(row=4, column=2)
        napStepEntry.grid(row=4, column=3)
        
        pasconstantRadiobutton= tk.Radiobutton(channelFrameRow4, text="Constant Values", variable =controller.howToChannelpas, value="constant")
        pasboundAndStepsizeRadiobutton= tk.Radiobutton(channelFrameRow4, text="  Upper Bound   ", variable =controller.howToChannelpas, value="bounds")
        pasLabel.grid(row=0, column=5)
        pasconstantRadiobutton.grid(row=1, column=4)
        pasEntry.grid(row=1, column=5)
        pasboundAndStepsizeRadiobutton.grid(row=2, column=4)
        pasUpperEntry.grid(row=2, column=5)
        pasLabelLow.grid(row=3, column=4)
        pasLowerEntry.grid(row=3, column=5)
        pasLabelStepSize.grid(row=4, column=4)
        pasStepEntry.grid(row=4, column=5)
        
        

        def startGridsearch():
            controller.algorithm.set("gridsearch")
            controller.start()
        
        startSimulationButton = tk.Button(self, text="Start the Simulation", command=startGridsearch)
        startSimulationButton.pack(side= tk.BOTTOM)
        
        

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
