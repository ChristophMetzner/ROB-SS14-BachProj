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
import nevo.eval.fitness as fitness

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
def parse_callable(pconf, sections, known_kwargs):
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
        for item in pconf.cfg.items(section):
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
                     "numCurrents" : int(pconf.get_list("currents", "Simulation")[0]),
                     "pconf" : pconf,
                     "mode" : mode}

    # Parse general evolve parameters.
    for item in pconf.cfg.items("EvolveParameters"):
        parsed_kwargs[item[0]] = eval(item[1])
        
    # Load selector, variators, replacer and terminators from the config file.
    selector_section = pconf.get("selector", "Simulation")
    logger.debug("Parsing selector: " + selector_section)
    EC.selector, parsed_kwargs = parse_callable(pconf, selector_section, parsed_kwargs)

    variator_section_list = pconf.get_list("variators", "Simulation")
    logger.debug("Parsing variators: " + repr(variator_section_list))
    EC.variator, parsed_kwargs = parse_callable(pconf, variator_section_list, parsed_kwargs)
    
    replacer_section = pconf.get("replacer", "Simulation")
    logger.debug("Parsing replacer: " + replacer_section)
    EC.replacer, parsed_kwargs = parse_callable(pconf, replacer_section, parsed_kwargs)

    terminator_section_list = pconf.get_list("terminators", "Simulation")
    logger.debug("Parsing terminators: " + repr(terminator_section_list))
    EC.terminator, parsed_kwargs = parse_callable(pconf, terminator_section_list, parsed_kwargs)

    evaluator_section = pconf.get("evaluator", "Simulation")
    logger.debug("Parsing evaluator: " + evaluator_section)
    evaluator, parsed_kwargs = parse_callable(pconf, evaluator_section, parsed_kwargs)

    generator_section = pconf.get("generator", "Simulation")
    logger.debug("Parsing generator: " + generator_section)
    generator, parsed_kwargs = parse_callable(pconf, generator_section, parsed_kwargs)

    
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
