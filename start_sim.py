#!/usr/bin/env python2.7
# coding=utf-8

import argparse
import sys
import logging
import threading

sys.path.append("./GenAlg/Programm/")

import simulation


class SimulationThread(threading.Thread):
    def __init__(self, config, temp, quiet):
        threading.Thread.__init__(self)
        self.config = config
        self.sim = simulation.Simulation(config, temp)
        self.quiet = quiet
    def run(self):
        self.result = self.sim.run(self.quiet)
        if self.result != 0:
            print "Simulation did not finish successfully with configuration '" + self.config + "'"
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
    parser.add_argument("-p", "--parallel", action="store_true", dest="parallel",
                        help="Runs all specified configurations in a new parallel thread. Output for each simulation"
                        + " will be suppressed.")
    args = parser.parse_args()
    quiet = args.quiet or args.parallel
    threads = []
    success_counter = 0
    try:
        # Start threads.
        for config in args.config:
            thread = SimulationThread(config, args.temp, quiet)
            threads.append(thread)
            thread.start()
            if not args.parallel:
                thread.join()
                if thread.result == 0:
                    success_counter += 1
        # Wait on all threads.
        if args.parallel:
            for thread in threads:
                thread.join()
                if thread.result == 0:
                    success_counter += 1
        num_threads = len(threads)
        print str(success_counter) + " of " + str(num_threads) + " threads finished successfully."
    finally:
        logging.shutdown()
#-----------------------------------------------------------
if __name__ == "__main__":
    main()
