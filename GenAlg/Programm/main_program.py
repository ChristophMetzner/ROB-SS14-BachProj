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
import logClient

logger = None

"""
 Diese Datei führt eine Evolutionary Computation zur Optimierung von Leitfähigkeiten von Neuronen aus.
 Dabei muss immer angegeben werden, welche Art von Neuronen gewünscht ist.
 Unterteilt werden diese Klassen in Modi ('mode') chattering(4), intrinsic bursting(3), regular (1) und fast spiking (2).
"""

#-----------------------------------------------------------
def mkiter(x):
    """ list -> list, el -> [el], None -> []

    Always returns an iterable.
    """
    return (x if hasattr( x, "__iter__" ) # list tuple ...
            else [] if x is None
            else [x])
#-----------------------------------------------------------
def mkitem(l):
    """ [el] -> el, [] -> None, list -> list

    Collapses single element items
    """
    if hasattr(l, "__iter__"):
        if len(l) == 0:
            return None
        elif len(l) == 1:
            x, = l
            return x
    return l
#-----------------------------------------------------------
def parse_callable(proj_conf, sections, known_kwargs):
    """Returns the callable object or function defined in the specified section
    with the accumulated parsed_kwargs.

    evaluates the value of the "class" key and returns the callable together with
    any other parameters in a (callable, dictionary) tuple.
    The parsed_kwargs are not modified and will be returned together with any new
    key / eval(value) pairs in the specified section.
    Throws a RuntimeError if any arguments are in conflict.
    """
    callables = []
    parsed_kwargs = dict(known_kwargs)
    for section in mkiter(sections):
        for item in proj_conf.cfg.items(section):
            try:
                value = eval(item[1])
            except:
                logger.exception()
                raise RuntimeError("Could not evaluate the expression '" + item[1]
                                   + "' for the callable '" + section + "'")
            if item[0] == "class":
                callables.append(value)
            elif item[0] in parsed_kwargs:
                if parsed_kwargs[item[0]] == eval(item[1]):
                    logger.warning("Redefined the option '" + item[0] + "' in the section '" + section
                                   + "' with the same value using the expression '"
                                   + item[1] + "'")
                else:
                    raise RuntimeError("Redefined the option '" + item[0] + "' in the section '" + section
                                       + "' with a different value using the expression '"
                                       + item[1] + "'"
                                       + ". Please remove the duplicate entry from your configuration.")
            else:
                parsed_kwargs[item[0]] = value
    return (mkitem(callables), parsed_kwargs)
        
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
    l_bound = args['lower_bound']
    u_bound = args['upper_bound']
    num_gens = args['_ec'].num_generations
    max_gens = args['max_generations']
    strength = args['mutation_strength']
    exponent = (1.0-num_gens/float(max_gens))**strength
    mutant = copy.copy(candidate)
    for i, (c,lo,hi) in enumerate(zip(candidate, l_bound, u_bound)):
        #if random.random() < args['mutation_rate']:
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
#   randL = int(random.uniform(0, len(mom)-args['num_allel']+1))
#   for i in range(args['num_allel']):
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
def main(proj_conf):
    global logger
    logger = proj_conf.getClientLogger("main_programm")
    
    #logger.info(Currents)
    rand = Random()
    rand.seed(int(time()))
    
    t = strftime("%d.%m.%Y-%H:%M:%S")   

    EC = inspyred.ec.EvolutionaryComputation(rand)
    #EC.analysis = inspyred.ec.analysis.generation_plot
    mode = proj_conf.get("mode", "Simulation")
    if mode  == "RS":
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


    
    # Load selector, variators, replacer and terminators from the config file.
    parsed_kwargs = {}
    for item in proj_conf.cfg.items("EvolveParameters"):
        parsed_kwargs[item[0]] = eval(item[1])

    selector_section = proj_conf.get("selector", "Simulation")
    logger.debug("Parsing selector: " + selector_section)
    EC.selector, parsed_kwargs = parse_callable(proj_conf, selector_section, parsed_kwargs)

    variator_section_list = proj_conf.get_list("variators", "Simulation")
    logger.debug("Parsing variators: " + repr(variator_section_list))
    EC.variator, parsed_kwargs = parse_callable(proj_conf, variator_section_list, parsed_kwargs)
    
    replacer_section = proj_conf.get("replacer", "Simulation")
    logger.debug("Parsing replacer: " + replacer_section)
    EC.replacer, parsed_kwargs = parse_callable(proj_conf, replacer_section, parsed_kwargs)

    terminator_section_list = proj_conf.get_list("terminators", "Simulation")
    logger.debug("Parsing terminators: " + repr(terminator_section_list))
    EC.terminator, parsed_kwargs = parse_callable(proj_conf, terminator_section_list, parsed_kwargs)

    evaluator_section = proj_conf.get("evaluator", "Simulation")
    logger.debug("Parsing evaluator: " + evaluator_section)
    evaluator, parsed_kwargs = parse_callable(proj_conf, evaluator_section, parsed_kwargs)

    
    logger.debug("Arguments accumulated for evolve: " + repr(parsed_kwargs))
    if sys.platform == "win32":
        statistics_file = open(proj_conf.localPath("inspyred-statistics.csv"),"w")
        individuals_file = open(proj_conf.localPath("inspyred-individuals.csv"),"w")
        filename = open(proj_conf.localPath("inspyred-inspyred-statistics.csv"))
    else:
        statistics_file = open(proj_conf.localPath("inspyred-statistics-{0}.csv"
                                                 .format(strftime('%m%d-%H%M'))),"w")
        individuals_file = open(proj_conf.localPath("inspyred-individuals-{0}.csv"
                                                  .format(strftime('%m%d-%H%M'))),"w")
        filename = proj_conf.localPath("inspyred-inspyred-statistics-{0}.csv"
                                     .format(strftime('%m%d-%H%M')))
    final_pop = EC.evolve(generator = inspyred.ec.generators.diversify(chromgen.generate_conductance),
                          evaluator = evaluator,
                          statistics_file = statistics_file,
                          individuals_file = individuals_file,
                          filename = filename,
                          proj_name = proj_conf.parseProjectConfig()["proj_name"],
                          errorbars = False,
                          logger = proj_conf.getClientLogger("EC.inspyred"),
                          lower_bound = l_bound,
                          upper_bound = u_bound,
                          numCurrents = int(proj_conf.get_list("currents", "Simulation")[0]),
                          proj_conf = proj_conf,
                          mode = mode,
                          **parsed_kwargs)
    final_pop.sort(reverse=True)

    logger.info(strftime("%Y.%m.%d %H:%M:%S")+":\nDie Eigenschaften des besten Individuums mit Fitness "\
            +str(final_pop[0].fitness)+" koennen in ErgebnisDens.txt gefunden werden.")
    if int(proj_conf.get("showExtraInfo", "Global")):
        logger.info("=========================================")

    
    #schreibt Ergebnisse in Datei zur späteren Auswertung!
    with open(proj_conf.get_local_path("resultDensityFile"), "a") as d:
        d.write("#\n")
        returnCount = min(proj_conf.get_int("pop_size", "EvolveParameters"), 10)
        for i in xrange(0,returnCount):
            item = final_pop[i]
            for v in item.candidate:
                d.write(str(v)+"\n")
            d.write("#\n\n")
        d.write("#####\n\n")
#endDEF
