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
import nevo.chromgen as chromgen
from nevo.util.callable import parse_callable

logger = None

"""
 Diese Datei führt eine Evolutionary Computation zur Optimierung von Leitfähigkeiten von Neuronen aus.
 Dabei muss immer angegeben werden, welche Art von Neuronen gewünscht ist.
 Unterteilt werden diese Klassen in Modi ('mode') chattering(4), intrinsic bursting(3), regular (1) und fast spiking (2).
"""
        
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
#   if int(projconf.get("showExtraInfo", "Global")) == 1:
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

#################################### CROSS #########################################################
""" crossover soll verschiedene Kanäle austauschen je nach crossover_rate und num_allel
#def cross(random, mom, dad, args):
#   #if int(projconf.get("showExtraInfo", "Global")) == 1:
#       #logger.info("=================================")
#       #logger.info(strftime("%Y.%m.%d %H:%M:%S")+": crossing over")
#       #logger.info("=================================")
#
#   os1 = mom
#   os2 = dad
#   randL = int(random.uniform(0, len(mom)-args['num_allel']+1))
#   for i in range(args['num_allel']):
#       os1[randL+i] = dad[randL+i]
#       os2[randL+i] = mom[randL+i]
#   return [os1, os2]
#endDEF 
""" 




####################################### START  #########################################################
"""
Es wird der Genetische Algorithmus aufgerufen und gestartet. Mit den Eingabeparametern, die am Anfang übergeben wurden, werden nun die nötigen Einstellungen vorgenommen.
Die Module für generation, variator(mutation, crossover),selection, observer und replacement werden hier initialisiert und aufgerufen.
Zum Schluss wird die finale Population und deren Eigenschaften bzw. die EIngabeparameter ausgegeben und gespeichert.
"""
def start(pconf):
    global logger
    logger = pconf.get_logger("evolution")
    
    #logger.info(Currents)
    rand = Random()
    rand.seed(int(time()))
    
    t = strftime("%d.%m.%Y-%H:%M:%S")   

    EC = inspyred.ec.EvolutionaryComputation(rand)
    #EC.analysis = inspyred.ec.analysis.generation_plot
    mode = pconf.get("mode", "Simulation")
    
    l_bound, u_bound = chromgen.get_bounds(mode)

    # braucht statistics_file und individuals_file für analysis
    EC.observer = inspyred.ec.observers.file_observer


    
    statistics_file = open(pconf.local_path("inspyred-statistics-{0}.csv"
                                               .format(strftime('%m%d-%H%M'))),"w")
    individuals_file = open(pconf.local_path("inspyred-individuals-{0}.csv"
                                                .format(strftime('%m%d-%H%M'))),"w")
    filename = pconf.local_path("inspyred-inspyred-statistics-{0}.csv"
                                   .format(strftime('%m%d-%H%M')))
    parsed_kwargs = {"statistics_file" : statistics_file,
                     "individuals_file" : individuals_file,
                     "filename" : filename,
                     "proj_name" : pconf.parse_project_data()["proj_name"],
                     "errorbars" : False,
                     "logger" : pconf.get_logger("EC.inspyred"),
                     "lower_bound" : l_bound,
                     "upper_bound" : u_bound,
                     "pconf" : pconf,
                     "mode" : mode}

    # Parse general evolve parameters.
    for item in pconf.cfg.items("EvolveParameters"):
        parsed_kwargs[item[0]] = eval(item[1])
        
    # Load selector, variators, replacer and terminators from the config file.
    selector_section = pconf.get("selector", "Simulation")
    logger.debug("Parsing selector: " + selector_section)
    EC.selector, parsed_kwargs = parse_callable(pconf, logger, selector_section, parsed_kwargs)

    variator_section_list = pconf.get_list("variators", "Simulation")
    logger.debug("Parsing variators: " + repr(variator_section_list))
    EC.variator, parsed_kwargs = parse_callable(pconf, logger, variator_section_list, parsed_kwargs)
    
    replacer_section = pconf.get("replacer", "Simulation")
    logger.debug("Parsing replacer: " + replacer_section)
    EC.replacer, parsed_kwargs = parse_callable(pconf, logger, replacer_section, parsed_kwargs)

    terminator_section_list = pconf.get_list("terminators", "Simulation")
    logger.debug("Parsing terminators: " + repr(terminator_section_list))
    EC.terminator, parsed_kwargs = parse_callable(pconf, logger, terminator_section_list, parsed_kwargs)

    evaluator_section = pconf.get("evaluator", "Simulation")
    logger.debug("Parsing evaluator: " + evaluator_section)
    evaluator, parsed_kwargs = parse_callable(pconf, logger, evaluator_section, parsed_kwargs)

    generator_section = pconf.get("generator", "Simulation")
    logger.debug("Parsing generator: " + generator_section)
    generator, parsed_kwargs = parse_callable(pconf, logger, generator_section, parsed_kwargs)

    
    logger.debug("Arguments accumulated for evolve: " + repr(parsed_kwargs))
    final_pop = EC.evolve(generator = generator,
                          evaluator = evaluator,
                          **parsed_kwargs)
    final_pop.sort(reverse=True)


    logger.info("=================================")
    logger.info("The best candidate has a fitness value of " + repr(final_pop[0].fitness))
    #schreibt Ergebnisse in Datei zur späteren Auswertung!
    with open(pconf.get_local_path("resultDensityFile"), "a") as d:
        for item in final_pop:
            d.write("# fitness: " + repr(item.fitness) + "\n")
            channels = chromgen.chromosome_to_channels(item.candidate)
            for v in channels:
                d.write(str(v)+"\n")
            d.write("\n")
        d.write("####\n\n")
    logger.info("Die Eigenschaften der letzten Generation"
                + " kann in '" + pconf.get("resultDensityFile") + "' gefunden werden.")
#endDEF
