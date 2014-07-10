#!/usr/bin/env python2.7
# coding=utf-8

import argparse
import sys
import logging
from multiprocessing import Pool

import nevo.simulation as simulation

def generate_task_parameters(configs, temp, quiet):
    return [{"config" : config, "temp" : temp, "quiet" : quiet}
            for config in configs]
#-----------------------------------------------------------
def task_runner(args):
    config = args["config"]
    temp = args["temp"]
    quiet = args["quiet"]
    
    sim = simulation.Simulation(config, temp)
    result = sim.run(quiet)
    if result != 0:
        print("Simulation did not finish successfully with configuration '" + config
              + "' (Code: " + str(result) + ")")
    else:
        print("Simulation '" + config + "' finished successfully")
    return result
#-----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Optimize conductance of"
                                     + " ion channels for computer modelled neuron cells.")
    parser.add_argument("-c", "--config", required = True, action="append",
                        help="Path to the configuration file defining the parameters for this run."
                        + " When more than one config file is specified, they are executed one after another by default.")
    parser.add_argument("-t", "--temp",
                        action='store_true', dest="temp",
                        help="Create a temporary working directory in which all processing"
                        + " should take place. Results will be copied to result_directory specified in the config)")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Supress logger output to stdout. Meta information about successful and failed"
                        + " is still printed without logger.")
    parser.add_argument("-p", "--pool-size", default = 1, type = int, dest = "pool_size",
                        help="""Runs all specified configurations in a thread pool with the specified number of
                        working processes. Output for each simulation will be suppressed.""")
    options = parser.parse_args()
    work_size = len(options.config)
    pool_size = max(min(options.pool_size, work_size), 1)
    
    success_counter = 0
    returncode = 0
    try:
        # Start threads.
        pool = Pool(processes = pool_size)
        parameters = generate_task_parameters(options.config, options.temp, quiet = True if pool_size > 1 else options.quiet)
        # Run quasi synchronously with one googol timeout. Fix for interrupt.
        results = pool.map_async(task_runner, parameters).get(1e100)
        for result in results:
            if result == 0:
                success_counter += 1
        if work_size > 1:
            print str(success_counter) + " of " + str(work_size) + " tasks finished successfully."
            if success_counter < work_size:
                returncode = 40
        else:
            returncode = results[0]
    except (KeyboardInterrupt, SystemExit):
        print "Interrupted"
    finally:
        logging.shutdown()
    sys.exit(returncode)

#-----------------------------------------------------------
if __name__ == "__main__":
    main()
