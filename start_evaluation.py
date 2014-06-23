#!/usr/bin/env python2.7
import sys
sys.path.append("./nevo/Auswertung")

import Auswertung
import Plotten

BS  = 1
sim = 1
mode = "CH"
num_currents = 3
start = 0.2
step = 0.3
anzahl = 1

dt = 0.025
duration = 500

execfile("./nevo/Auswertung/chromosome_in_density.py")

Auswertung.auswerten(   Anzahl = anzahl,
            modus = mode,
            currents = [num_currents,start,step],
            simulieren = sim, 
            BS = BS,
            timestep = dt)
            
    
#Plotten.plotten(BS,mode,num_currents,duration, dt)
