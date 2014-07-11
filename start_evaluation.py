#!/usr/bin/env python2.7

import argparse
from nevo import evaluation
from nevo.util import projconf
from multiprocessing import Pool

def parse_result_candidates(filename):
    """Returns a list of (fitness, channels) items."""
    densities_list = []
    densities = []
    fitness = 9999999
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("#"):
                if len(densities) > 0:
                    densities_list.append((fitness, densities))
                    densities = []
                if line.startswith("# fitness:"):
                    fitness = line.split(":")[1]
            elif line != "":
                densities.append(float(line))
    return densities_list

def task_runner(args):
    pconf = projconf.ProjectConfiguration(sim_path = args["sim_path"],
                                          config_file = projconf.norm_path(args["sim_path"],"full.cfg"))

    item_list = parse_result_candidates(pconf.get_local_path("resultDensityFile"))
    (fitness, candidates) = zip(*item_list)
    if args["best_neurons"] is not None:
        last = min(args["best_neurons"], len(candidates))
        candidates = candidates[:last]
    evaluation.evaluate(pconf.get_logger("start_evaluation"), pconf, candidates)
    return args

def generate_task_arguments(sim_paths, best_neurons = None):
    return [{"sim_path" : sim_path,
             "best_neurons" : best_neurons} for sim_path in sim_paths]

def main():
    parser = argparse.ArgumentParser(description="""Reevaluate neurons from existing simulation.
                                     Evaluates all neurons from the given simulations (--sim-path)
                                     and stores the result in the output file. """)
    parser.add_argument("-s", "--sim-path", required = True, action="append",
                        help = """Path to the result folder of a simulation""")
    parser.add_argument("-b", "--best-neurons", type = int, help = """Limit the
                        neurons to evaluate to the number specified.""")
    parser.add_argument("-p", "--pool-size", default = 1, type = int,
                        help = """Specifies how many --sim-path options will be processed in parallel
                        at any given time.""")
    parser.add_argument("output_file", help = """The result of the simulations will be stored in
                        specified file""")
    parser.add_argument("-c", "--cleanup", action = "store_true",
                        help = """When specified, any simulation folder of the form '""" + evaluation.EVAL_PREFIX
                        + """*' will be deleted after evaluation""")
    options = parser.parse_args()

    work_size = len(options.sim_path)
    pool_size = max(min(options.pool_size, work_size), 1)

    if work_size > 1:
        pool = Pool(processes = options.pool_size)
        # Run quasi synchronously with one googol timeout. Fix for interrupt.
        result = pool.map_async(task_runner,
                                generate_task_arguments(options.sim_path, options.best_neurons)).get(1e100)
    elif work_size == 1:
        result = [task_runner(generate_task_arguments(options.sim_path, options.best_neurons)[0])]
    else:
        result = []
    
if __name__ == "__main__":
    main()
