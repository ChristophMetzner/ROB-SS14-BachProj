# coding=utf-8

import os
import sys
import errno
import numpy
import subprocess
from random import Random
from time import time, sleep, strftime
import inspyred
import itertools
import copy


# verwendete eigene Module
import HartigansDipDemo
from dipTestInst import dipTest
import analysis
import chromgen
import fitness
import projConf
import logClient

logger = logClient.getClientLogger("main_programm")

"""
 Diese Datei führt eine Evolutionary Computation zur Optimierung von Leitfähigkeiten von Neuronen aus.
 Dabei muss immer angegeben werden, welche Art von Neuronen gewünscht ist.
 Unterteilt werden diese Klassen in Modi ('modus') chattering(4), intrinsic bursting(3), regular (1) und fast spiking (2).
"""

#################### EINGABEN: ##########################
def start(proj_name         = None, 
        proj_path           = None, 
        sim_config          = None, 
        stimulation         = None, 
        cell                = None, 
        duration            = None, 
        dt                  = None, 
        currents            = None, #list [num, start, step]
    # for GA
        pop_size            = None, 
        max_generations     = None, 
        mode                = None,
        crossover_rate      = None,
        mutation_strength   = None,
        mutation_rate       = None,
        num_selected        = None,
        num_co_points       = None,
        num_elites          = None,
        tournament_size     = None,
        thrFourier          = None,
        weights             = None, #List [apw, ibf, ir, ai, slope]
        penalty_ai_RS       = None,
        penalty_ai_FS       = None,
        penalty_ibf_IB      = None,
        penalty_ibf_CH      = None,
        penalty_ir_IB       = None,
        penalty_ir_CH       = None, 
        penFourier          = None,
        custom              = None,
        anhang              = None):

    #Defaults:
    if proj_name is None:            proj_name = "Pyr_RS"
    if proj_path is None:        proj_path = proj_name+"/"+proj_name+".ncx"
    if sim_config is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": sim_config = "Default Simulation Configuration"
        else: logger.info("proj_name not known: Be sure, that you chose the right Simulation Configuration!")
    if stimulation is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": stimulation = "Input_0"
        else: logger.info("proj_name not known: Be sure, that you chose the right Stimulation!")
    if cell is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": cell = "L5TuftedPyrRS"
        else: logger.info("proj_name not known: Be sure, that you chose the right Cell!")

    if duration is None:              duration = 500
    if dt is None:                    dt = 0.05
    if currents is None:              currents = [3,0.2,0.3]
    if custom is None:                custom = 0
    if anhang is None:                anhang = " "

    if pop_size is None:              pop_size = 50
    if max_generations is None:       max_generations = 30
    
    if mode is None:
        if proj_name is "Pyr_RS":     mode = "RS"
        elif proj_name is "Pyr_IB":   mode = "IB"
        else: logger.info("proj_name not known: Be sure, that you chose the right mode!")
        
    if crossover_rate is None:        crossover_rate = 1
    if thrFourier is None:            thrFourier = 5
    if mutation_strength is None:     mutation_strength = 0.4
    if mutation_rate is None:         mutation_rate = 1/12.0
    if num_selected is None:          num_selected = pop_size
    if num_co_points is None:         num_co_points = 1
    if num_elites is None:            num_elites = 1
    if tournament_size is None:       tournament_size = 2
    if weights is None:               weights = [1,1,1,1,1]      #[apw, ibf, ir, ai, slope]
    if penalty_ai_RS is None:         penalty_ai_RS = -3500
    if penalty_ai_FS is None:         penalty_ai_FS = -3500
    if penalty_ibf_IB is None:        penalty_ibf_IB = -2500
    if penalty_ibf_CH is None:        penalty_ibf_CH = -3500
    if penalty_ir_IB is None:         penalty_ir_IB = -3500
    if penalty_ir_CH is None:         penalty_ir_CH = -2500
    if penFourier is None:            penFourier = -10000
    ###############################
    
    
    # Speichern der Konfiguraton für die Simulation in "Config.txt":
    filename = projConf.getPath("projectConfig", "GenAlg")

    # Create folder if not present:
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    with open(filename, "w") as config:
        config.write(str(proj_name) + "\n"
                     + str(proj_path) + "\n"
                     + str(sim_config) + "\n"
                     + str(stimulation) + "\n"
                     + str(cell) + "\n"
                     + str(duration) + "\n"
                     + str(dt) + "\n"
                     + str(currents) + "\n"
                     + str(mode))
    ###############################
    
    
    # Leeren der Dateien, da spaeter die Werte >angehaengt< werden:
    with open(projConf.getPath("channelFile", "GenAlg"), "w"): pass
    with open(projConf.getPath("densityFile", "GenAlg"), "w"): pass
    with open(projConf.getPath("locationFile", "GenAlg"), "w"): pass
    ###############################
    
    
    # Aufruf des Evolutionären Algorithmus:
    main(   proj_name,
            pop_size, 
            max_generations, 
            mode, 
            crossover_rate,
            mutation_strength,
            mutation_rate,
            num_selected,
            num_co_points,
            num_elites,
            tournament_size,
            weights,
            thrFourier,
            penFourier,
            penalty_ai_RS,
            penalty_ai_FS,
            penalty_ibf_IB,
            penalty_ibf_CH,
            penalty_ir_IB,
            penalty_ir_CH, 
            currents,
            custom,
            anhang)
#endDEF

        
###################################### MUTATE_COND #####################################################
""" Mutation der Leitfähigkeiten   
#   damit die Verhältnisse in den einzenlen Kanälen erhalten bleiben:
#       es muss gelten : 
#                       x1/x2 = (x1+k1)/(x2+k2)
#       also:(wenn x1, x2 und k1 geben)
#                          k2 = x2/x1*k1
#       oder allgemein:
#                          ki = xi/x1*k1
#   mit k1 := add,  x1:=inst[start], xi:=inst[j],   
#
#def mutate_cond(random, candidates, args):
#   if int(projConf.get("showExtraInfo", "Global")) == 1:
#       logger.info("=================================")
#       logger.info(strftime("%d.%m.%Y %H:%M:%S")+": there are "+str(len(candidates))+" individuals for mutation")
#       logger.info(strftime("%d.%m.%Y %H:%M:%S")+": there are "+str(len(candidates)/2)+" pairs for crossover")
#       #logger.info("=================================")
#
#   mutants = []
#   for inst in candidates:
#       for chan in inst:
#           chan.mutate()
#       mutants.append(inst)
#   return mutants
#endDEF 
"""



###################################### MUTATE_UNIFORM #####################################################
# 1:1 "abgeschrieben" von der inspyred-Funktion, Sie hat beim regulären Aufruf nicht funktioniert
def nuMutation(random, candidate, args):
    l_bound = args.get('lower_bound')
    u_bound = args.get('upper_bound')
    num_gens = args['_ec'].num_generations
    max_gens = args.get('max_generations')
    strength = args.get('mutation_strength')
    exponent = (1.0-num_gens/float(max_gens))**strength
    mutant = copy.copy(candidate)
    for i, (c,lo,hi) in enumerate(zip(candidate, l_bound, u_bound)):
        #if random.random() < args.get('mutation_rate'):
        if random.random() <= 0.5:
            new_value = c+(hi-c)*(1.0-random.random()**exponent)
        else:
            new_value = c-(c-lo)*(1.0-random.random()**exponent)
        mutant[i] = new_value

    return mutant
#endDEF




#################################### CROSS #########################################################
""" crossover soll verschiedene Kanäle austauschen je nach crossover_rate und num_allel
#def cross(random, mom, dad, args):
#   #if int(projConf.get("showExtraInfo", "Global")) == 1:
#       #logger.info("=================================")
#       #logger.info(strftime("%Y.%m.%d %H:%M:%S")+": crossing over")
#       #logger.info("=================================")
#
#   os1 = mom
#   os2 = dad
#   randL = int(random.uniform(0, len(mom)-args.get('num_allel')+1))
#   for i in range(args.get('num_allel')):
#       os1[randL+i] = dad[randL+i]
#       os2[randL+i] = mom[randL+i]
#   return [os1, os2]
#endDEF 
""" 




####################################### MAIN #########################################################
"""
In der Main wird der Genetische Algorithmus aufgerufen und gestartet. Mit den Eingabeparametern, die am Anfang übergeben wurden, werden nun die nötigen Einstellungen vorgenommen.
Die Module für generation, variator(mutation, crossover),selection, observer und replacement werden hier initialisiert und aufgerufen.
Zum Schluss wird die finale Population und deren Eigenschaften bzw. die EIngabeparameter ausgegeben und gespeichert.
"""
# Beginn der Main:
def main(projName,
         population, 
         generations, 
         mode, 
         crossover, 
         mutation,
         mut_rate,
         selected,
         points,
         elite,
         tsize,
         weights,
         thrF,
         penF,
         penalty_ai_RS,
         penalty_ai_FS,
         penalty_ibf_IB,
         penalty_ibf_CH,
         penalty_ir_IB,
         penalty_ir_CH, 
         Currents,
         custom,
         anhang):
    #logger.info(Currents)
    rand = Random()
    rand.seed(int(time()))
    
    t = strftime("%d.%m.%Y-%H:%M:%S")   

    EC = inspyred.ec.EvolutionaryComputation(rand)
    #EC.analysis = inspyred.ec.analysis.generation_plot

    
    # Variator: braucht 'crossover_rate', 'num_crossover_points'; 'mutation_strength'
    EC.variator = [inspyred.ec.variators.n_point_crossover, inspyred.ec.variators.mutator(nuMutation)]

    if mode == "RS":
        # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
        u_bound = [10**x for x in [ -7, -7, -6, -5, -5, -5, -5, -3, -4, -3, -5, -5]]
        l_bound = [10**x for x in [-14,-14,-14,-14,-14,-14,-14, -5,-11, -5,-14,-15]]
    elif mode == "FS":
        # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
        u_bound = [10**x for x in [ -7, -7, -6, -5, -5, -9, -5, -3, -6, -3, -5, -5]]
        l_bound = [10**x for x in [-14,-14,-14,-14,-14,-11,-14, -5, -8, -5,-14,-15]]
    elif mode == "CH":
        # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
        u_bound = [10**x for x in [ -7, -9, -7, -5, -5, -5, -5, -3, -7, -3, -5, -5]]
        l_bound = [10**x for x in [-14,-12,-12,-12,-12,-12,-12, -4,-11, -5,-12,-13]]
    else:
        # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
        u_bound = [10**x for x in [ -7, -9, -7, -5, -5, -5, -5, -3, -7, -3, -5, -5]]
        l_bound = [10**x for x in [-14,-12,-12,-12,-12,-12,-12, -4,-11, -5,-12,-13]]

    # braucht statistics_file und individuals_file für analysis
    EC.observer = inspyred.ec.observers.file_observer
    if custom == 1:
        if mode == "RS" or mode == "FS":
            EC.selector = inspyred.ec.selectors.tournament_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement # erstellt neue Generation
            anhang = anhang+"tournament_selection und truncation_replacement"
        else:
            EC.selector = inspyred.ec.selectors.truncation_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement
            anhang = anhang+"truncation_selection und truncation_replacement"

    else:
        if mode == "RS" or mode == "FS":
            EC.selector = inspyred.ec.selectors.tournament_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.random_replacement #truncation_replacement#random_replacement# # erstellt neue Generation
            anhang = anhang+"tournament_selection und random_replacement"
        else:
            EC.selector = inspyred.ec.selectors.truncation_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement
            anhang = anhang+"truncation_selection und truncation_replacement"
        


    # terminator: braucht 'max_generations', 'tolerance'
    if sys.platform == "win32":
        statistics_file = open(projConf.normPath("GenAlg/plots/inspyred-statistics.csv"),"w")
        individuals_file = open(proj_conf.normPath("GenAlg/plots/inspyred-individuals.csv"),"w")
        filename = open(proj_conf.normPath("GenAlg/plots/inspyred-inspyred-statistics.csv"))
    else:
        EC.terminator = inspyred.ec.terminators.generation_termination
        statistics_file = open(projConf.normPath("GenAlg/Programm/Speicher/inspyred-statistics-{0}.csv"\
                                                 .format(strftime('%m%d-%H%M'))),"w")
        individuals_file = open(projConf.normPath("GenAlg/Programm/Speicher/inspyred-individuals-{0}.csv"\
                                                  .format(strftime('%m%d-%H%M'))),"w")
        filename = projConf.normPath("GenAlg/Programm/Speicher/inspyred-inspyred-statistics-{0}.csv"\
                                     .format(strftime('%m%d-%H%M')))
    final_pop = EC.evolve(generator = inspyred.ec.generators.diversify(chromgen.generate_conductance),
                          evaluator = fitness.evaluate_param,
                          statistics_file = statistics_file,
                          individuals_file = individuals_file,
                          filename = filename,
                          projName = projName,
                          errorbars = False,
                          lower_bound = l_bound,
                          upper_bound = u_bound,
                          pop_size = population,
                          max_generations = generations,
                          crossover_rate = crossover,
                          num_crossover_points = points,
                          num_selected = selected,
                          num_elites = elite,
                          tournament_size = tsize,
                          mutation_strength = mutation, # higher values correspond to greater variation
                          mutation_rate = mut_rate,
                          modus = mode, 
                          thrFourier = thrF,
                          penFourier = penF,
                          p_ai_RS = penalty_ai_RS,
                          p_ai_FS = penalty_ai_FS,
                          p_ibf_IB = penalty_ibf_IB,
                          p_ibf_CH = penalty_ibf_CH,
                          p_ir_IB = penalty_ir_IB,
                          p_ir_CH = penalty_ir_CH,
                          W_apw = weights[0],
                          W_ibf = weights[1],
                          W_ir = weights[2],
                          W_ai = weights[3],
                          W_slope = weights[4],
                          numCurrents = Currents[0])
    final_pop.sort(reverse=True)

    logger.info(strftime("%Y.%m.%d %H:%M:%S")+":\nDie Eigenschaften des besten Individuums mit Fitness "\
            +str(final_pop[0].fitness)+" koennen in ErgebnisDens.txt gefunden werden.")
    if int(projConf.get("showExtraInfo", "Global")):
        logger.info("=========================================")

    
    #schreibt Ergebnisse in Datei zur späteren Auswertung!
    with open(projConf.getPath("resultDensityFile", "GenAlg"), "a") as d:
        string = "Anfang: "+t+" Ende: "+strftime("%d.%m.%Y %H:%M:%S")+": Ergebnis der EC mit: Fitness"+str(final_pop[0].fitness)+"[2. "+ str(final_pop[1].fitness)+", 3. "+str(final_pop[2].fitness)+"]"
        string += " modus = "+str(mode)
        string += "; pop_size = "+str(population)
        string += "; max_generations = "+str(generations)
        string += "; currents = "+str(Currents[0])+str(Currents[1])+str(Currents[2])
        string += "; crossover_rate = "+str(crossover)
        string += "; mutation_strength = "+str(mutation)
        string += "; mutation_rate = "+str(mut_rate)
        string += "; tournament_size = "+str(tsize)
        string += "; num_selected = "+str(selected)
        string += "; num_co_points = "+str(points)
        string += "; weights = "+str(weights)
        string += "; thrFourier = "+str(thrF)
        string += "; penFourier = "+str(penF) 
        string += "; PaiRS = "+str(penalty_ai_RS)
        string += "; PaiFS = "+str(penalty_ai_FS)
        string += "; PibfIB = "+str(penalty_ibf_IB)
        string += "; PibfCH = "+str(penalty_ibf_CH)
        string += "; PirIB = "+str(penalty_ir_IB)
        string += "; PirCH = "+str(penalty_ir_CH)
        string += "; Anhang = "+anhang
        string += "\n#\n"
        d.write(string)
        returnCount = min(population,10)
        for i in xrange(0,returnCount):
            item = final_pop[i]
            for v in item.candidate:
                d.write(str(v)+"\n")
            d.write("#\n\n")
        d.write("#####\n\n")
#endDEF
