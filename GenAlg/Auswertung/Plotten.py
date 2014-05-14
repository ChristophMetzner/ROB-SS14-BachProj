#! usr/local/lib/python2.7 python
# coding=utf-8

import math
import numpy
import scipy.optimize as optimization
from time import sleep
from pylab import plot, show, title, xlabel, ylabel, subplot
from scipy import fft, arange
from time import sleep
import matplotlib.pyplot as plt     

BS = 1 #1:linux, 2:windows
mode = 1
num_currents = 3
duration = 500  #default
dt = 0.025  #default

def plotten(BS,mode,num_currents,duration, dt):

    D = []      
    for z in range(num_currents):   
        if BS == 1:
            if mode == 1 or mode == 2:
                filename = "./Pyr_RS/simulations/A_"+str(z)+"/CellGroup_1_0.dat"
            else: 
                filename = "./Pyr_IB/simulations/A_"+str(z)+"/CellGroup_1_0.dat"
        else:
            if mode == 1 or mode == 2:
                filename = "C:\Python27\Pyr_RS\simulations\A_"+str(z)+"\CellGroup_1_0.dat"
            else:
                filename = "C:\Python27\Pyr_IB\simulations\A_"+str(z)+"\CellGroup_1_0.dat"
        t = 0
        while t < 30:
            try:
                fileDE = open(filename,'r')
                t = 100
                check = 1
            except:
                sleep(3)
                t = t+3
                print t 
                
        density = numpy.zeros(20000)
        densities_list= fileDE.read().split('#\n')      
        densities = densities_list[0].split('\n')
        for i in range(len(densities)):
            dens = densities[i].strip()             
            try:    
                x = float(dens)
                density[i] = x
            except:
                pass    
        fileDE.close()
        Fs = 1000/dt;  # sampling rate 1000ms/dt
        Ts = 1.0/Fs; # sampling interval
        t = numpy.arange(0,0.5,Ts) # time vector
        y = density
        D.append(y)

        plt.plot(t,y)
        xlabel('Zeit [s]')
        ylabel('Membranpotenzial [mV]')
        show()

    for z in range(num_currents):   
        subplot(num_currents,1,z+1)
        plt.plot(t,D[z])
        if z == 1:
            xlabel('Zeit [s]')
            ylabel('Membranpotenzial [mV]')
    show()
