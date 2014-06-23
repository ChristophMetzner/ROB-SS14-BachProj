#!/usr/bin/env python2.7
# coding=utf-8

import argparse
import sys
import logging
import subprocess

import nevo.simulation as simulation


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
    parser.add_argument("-p", "--parallel", action="store_true", dest="parallel",
                        help="Runs all specified configurations in a new parallel thread. Output for each simulation"
                        + " will be suppressed.")
    options = parser.parse_args()
    num_configs = len(options.config)
    processes = []
    success_counter = 0
    result = 0
    returncode = 0
    try:
        # Start threads.
        if not options.parallel:
            for config in options.config:
                sim = simulation.Simulation(config, options.temp)
                result = sim.run(options.quiet)
                if result != 0:
                    print("Simulation did not finish successfully with configuration '" + config
                          + "' (Code: " + str(result) + ")")
                else:
                    success_counter += 1
        else:
            for config in options.config:
                args = [sys.argv[0], "-c", config, "-q"]
                if options.temp:
                    args.append("-t")
                processes.append(subprocess.Popen(args))
            for p in processes:
                result = p.wait()
                if result != 0:
                    print("Simulation did not finish successfully with configuration '" + config
                          + "' (Code: " + str(result) + ")")
                else:
                    success_counter += 1
        if num_configs > 1:
            print str(success_counter) + " of " + str(num_configs) + " workers finished successfully."
            if success_counter < num_configs:
                returncode = 40
        else:
            returncode = result
    except (KeyboardInterrupt, SystemExit):
        print "Interrupted"
    finally:
        logging.shutdown()
    sys.exit(returncode)

#-----------------------------------------------------------
if __name__ == "__main__":
    main()
