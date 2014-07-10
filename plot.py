#!/usr/bin/env python2.7
# coding=utf-8

import argparse
import math
import numpy
import scipy.optimize as optimization
from time import sleep
from pylab import plot, show, title, xlabel, ylabel, subplot
from scipy import fft, arange
from time import sleep
import matplotlib.pyplot as plt     

from nevo.util import projconf

def plot(pconf, simulations, time = 1.0):
    time = min(time, 1.0)
    D = []
    for simulation in simulations:
        densityFile = projconf.norm_path(pconf.get_sim_project_path(),
                                         "simulations", simulation, "CellGroup_1_0.dat")
        Fs = 1000 / pconf.get_float("dt", "Simulation");  # sampling rate 1000ms/dt
        Ts = 1.0 / Fs; # sampling interval
        t = numpy.arange(0, time, Ts) # time vector
        with open(densityFile,'r') as fileDE:
            density = numpy.zeros(len(t))
            densities_list= fileDE.read().split('#\n')      
            densities = densities_list[0].split('\n')
            for i in range(len(density)):
                dens = densities[i].strip()             
                density[i] = float(dens)
        fileDE.close()
        y = density
        D.append(y)

        
        plt.plot(t,y)
        xlabel('Zeit [s]')
        ylabel('Membranpotenzial [mV]')
    for z in range(len(simulations)):
        subplot(len(simulations), 1, z + 1)
        plt.plot(t, D[z])
        if(z == len(simulations) // 2):
            ylabel('Membranpotenzial [mV]')
    xlabel('Zeit [s]')
    show()


def main():
    parser = argparse.ArgumentParser(description="Plot a neuroConstruct neuron after simulation.")
    parser.add_argument(metavar = "SIM_PATH", dest = "sim_path",
                        help = """Path to the simulation path containing the config files used and the neuroConstruct project.
                        This is also called simulation path and the result of calling "start_sim".""")
    parser.add_argument("-s", "--simulation", action = "append",
                        help = """Just the name of the simulation as
                        found in the neuroConstruct's neuron simulation.
                        Example: Use "PySim_27" for "Pyr_RS/simulations/PySim_27" """)
    parser.add_argument("-t", "--time", type = float, default = 1.0,
                        help = """The time in seconds that should be displayed.
                        Only valid values are between 0.0 and 1.0.""")
    options = parser.parse_args()

    configFile = projconf.norm_path(options.sim_path, "full.cfg")
    pconf = projconf.ProjectConfiguration(configFile, options.sim_path)
    plot(pconf, options.simulation, options.time)
    

if __name__ == "__main__":
    main()
