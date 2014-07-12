#!/usr/bin/env python2.7
# coding=utf-8

import argparse
import os
import time
import errno
import math
import numpy
import scipy.optimize as optimization
from time import sleep
from pylab import plot, show, title, xlabel, ylabel, subplot, savefig
from scipy import fft, arange
from time import sleep
import matplotlib.pyplot as plt     

from nevo.util import projconf

def plot(pconf, simulations, time = 1.0, show_plot = True, output_file = None):
    dt = pconf.get_float("dt", "Simulation")
    Fs = 1000 / dt
    Ts = 1.0 / Fs; # sampling interval
    duration = pconf.get_float("duration", "Simulation")
    time = min(time, duration / 1000)
    t = numpy.arange(0, time, Ts) # time vector
    D = []
    for simulation in simulations:
        densityFile = projconf.norm_path(pconf.get_sim_project_path(),
                                         "simulations", simulation, "CellGroup_1_0.dat")
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
    if show_plot:
        show()
    if output_file is not None:
        savefig(output_file)


def main():
    parser = argparse.ArgumentParser(description="Plot a neuroConstruct neuron after simulation.")
    parser.add_argument(metavar = "SIM_PATH", dest = "sim_path",
                        help = """Path to the simulation path containing the config files used and the neuroConstruct project.
                        This is also called simulation path and the result of calling "start_sim".""")
    parser.add_argument("-s", "--simulation", required = True, action = "append",
                        help = """Just the name of the simulation as
                        found in the neuroConstruct's neuron simulation.
                        Example: Use "PySim_27" for "Pyr_RS/simulations/PySim_27" """)
    parser.add_argument("-t", "--time", type = float, default = 1.0,
                        help = """The time in seconds that should be displayed.
                        Valid values depend on sampling size and are usually between 0 and 1.0.""")
    parser.add_argument("-f", "--file", action = "store",
                        help = """Don't show image but save the plot in plots/FILE.
                        This name can have a correct file extension to specify the type (*.png or *.eps ..).""")
    options = parser.parse_args()

    configFile = projconf.norm_path(options.sim_path, "full.cfg")
    pconf = projconf.ProjectConfiguration(configFile, options.sim_path)
    if options.file is not None:
        output_file = projconf.norm_path("plots", options.file)
        plot(pconf, options.simulation, options.time, show_plot = False, output_file = output_file)
    else:
        plot(pconf, options.simulation, options.time, show_plot = True)
    

if __name__ == "__main__":
    main()
