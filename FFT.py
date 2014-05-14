#! usr/local/lib/python2.7 python
# coding=utf-8
import subprocess
from numpy import sin, linspace, pi, zeros, argmax
from pylab import plot, show, title, xlabel, ylabel, subplot
from scipy import fft, arange
from time import sleep
import matplotlib.pyplot as plt

def Fourier( Anzahl = None, modus = None, currents = None, simulieren = None, BS = None):
    
    if Anzahl is None:
        Anzahl = 1
    if modus is None:
        modus = 1
        mode = 1
    elif modus == 1 or modus == 2:
        mode = 1
    elif modus == 3 or modus == 4:
        mode = 2
    if currents is None:
        currents = [3,0.2,0.3]
    if simulieren is None:
        simulieren = 1
    if BS is None:
        BS = 1
        
    print "##############################"
    print "Es startet die Auswertung von "+str(Anzahl)+" Ergebnissen im Modus "+str(mode)
    print "##############################"
    
    if BS == 1:
        config = open("./GenAlg/Auswertung/AuswertungsConfig.txt", "w")
    else:
        config = open("C:\Python27\GenAlg\Auswertung\AuswertungsConfig.txt", "w")
    config.write(str(mode)+"\n"+str(currents)+"\n"+str(Anzahl)+"\n")
    config.close()  
    
    for i in range(Anzahl):
        
        if simulieren != 0:
            print " Fuer Ergebnis "+str(i)+" startet die Simulation mit den drei Stroemen "+str(currents[1])+", "+str(currents[1]+currents[2])+" und "+ str(currents[1]+currents[2]*2)+"."
            #Aufruf der Simulation:
            if BS == 1:
                #subprocess.check_call(['/home/kloskowski/Desktop/Python-skript/neuroConstruct_1.6.0/nC.sh', 
                            #'-python', 
                            #'/home/kloskowski/Desktop/Python-skript/Bachelorarbeit/Auswertung/MultiCurrent.py'])
                subprocess.check_call(['./neuroConstruct_1.6.0/nC.sh', 
                            '-python', 
                            './GenAlg/Auswertung/MultiCurrent.py'])
                sleep(12)
            else:
                uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Auswertung\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" # muss im Pfad liegen, sonst explizit mit angeben 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) )
                # warten auf die Simulation:
                p.wait()
                sleep(20)
        else:
            pass
    for z in range(currents[0]):        
        if BS == 1:
            if mode == 1:
                filename = "./Pyr_RS/simulations/A_"+str(z)+"/CellGroup_1_0.dat"
            else:
                filename = "./Pyr_IB/simulations/A_"+str(z)+"/CellGroup_1_0.dat"
        else:
            if mode == 1:
                filename = "C:\Python27\Pyr_RS\simulations\A_"+str(z)+"\CellGroup_1_0.dat"
            else:
                filename = "C:\Python27\Pyr_IB\simulations\A_"+str(z)+"\CellGroup_1_0.dat"
        t = 0
        while t < 60:
            try:
                fileDE = open(filename,'r')
                t = 100
                check = 1
            except:
                sleep(3)
                t = t+3
                print t 
                        
        density = zeros(20000)
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
        
        Fs = 40000.0;  # sampling rate
        Ts = 1.0/Fs; # sampling interval
        t = arange(0,0.5,Ts) # time vector

        y = density
        print len(t)
        print len(density)
        subplot(2,1,1)
        plot(t,y)
        xlabel('Zeit  [s]')
        ylabel('Membranpotenzial [mV]')
        subplot(2,1,2)
        plotSpectrum(y,Fs, modus)
        show()

def plotSpectrum(y,Fs, modus):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    From:   http://glowingpython.blogspot.de/2011/08/how-to-plot-frequency-spectrum-with.html
    (04.10.13, 17:00 Uhr)
    """
    n = len(y) # length of the signal (10001)
    k = arange(n)
    T = n/Fs # timestep (0.05)
    frq = k/T # two sides frequency range 
    frq = frq[range(n/2)] # one side frequency range
    dt = 2.0 #Hz
    Y = fft(y)/n # fft computing and normalization
    Y = Y[range(n/2)]
    absY = abs(Y)
    
    slope = (absY[1]-absY[0])/dt
    #print slope
    i = 0
    while(slope<0):
        i = i+1
        slope = (absY[i]-absY[i-1])/dt
        #print slope
    
    if modus == 1:
        # Abtasten der Intervalle in 100Hz-Schritten, extrahier jeweils das Maximum
        maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF)                 # 0  -100
        maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)        # 100-200
        maxF2 = max(absY[200/dt+1:300/dt]); i2 = list(absY).index(maxF2)        # 200-300
        #maxF3 = max(absY[300/dt+1:400/dt]);    i3 = list(absY).index(maxF3)# 300-400
        #maxF4 = max(absY[400/dt+1:500/dt]);    i4 = list(absY).index(maxF4)# 400-500
        maxF5 = max(absY[300/dt+1:]);   i5 = list(absY).index(maxF5)            # 300-infty

        S = maxF+maxF1+maxF2+maxF5
        
        MAX = max([maxF1, maxF2, maxF5]) # 100-infinity,  normalsiert über die Summe aller maxFs
        f_MAX = list(absY).index(MAX)*dt

        print maxF, i0*dt
        print MAX, f_MAX
        print "0-100:",maxF/S, i0*dt
        print "101-200:",maxF1/S, i1*dt
        print "201-300:",maxF2/S, i2*dt
        #print "301-400:",maxF3/S, i3*dt
        #print "401-500:",maxF4/S, i4*dt 
        print "301-infty:",maxF5/S, i5*dt

        
        # if f_MAX > 200:     
            # Fpenalty.append(0.5)
            # reason.append("Frequenz zu hoch")
        # #elif MAX < 0.09:       
        # # Fpenalty.append(0.5)
        # # reason.append("Intraburstfrequenz zwar zwischen 100 und 500Hz, aber nicht deutlich erhöht")
        # else:            
            # Fpenalty.append(0)
            # reason.append(" ")
        #if maxF/S < 0.09:    
            #Fpenalty.append(1)
            #reason.append("keine erhöhte Frequenz zwischen 0 und 100Hz (Interburstfrequenz)")
        #M.append(max(abs(Y[i:])))
    elif modus == 3: #IB
        # Abtasten der Intervalle in 100Hz-Schritten, extrahier jeweils das Maximum
        maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF)             # 0  -100
        maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)    # 100-200
        maxF2 = max(absY[200/dt+1:300/dt]); i2 = list(absY).index(maxF2)    # 200-300
        maxF3 = max(absY[300/dt+1:400/dt]); i3 = list(absY).index(maxF3)    # 300-400
        maxF4 = max(absY[400/dt+1:500/dt]); i4 = list(absY).index(maxF4)    # 400-500
        maxF5 = max(absY[500/dt+1:]);   i5 = list(absY).index(maxF5)    # 500-infty

        S = maxF+maxF1+maxF2+maxF3+maxF4+maxF5
        
        MAX = max([maxF1, maxF2, maxF3, maxF4, maxF5]) # 100-infinity,  normalsiert über die Summe aller maxFs
        f_MAX = list(absY).index(MAX)*dt

        print maxF/S, i0
        print MAX/S, f_MAX
        print "0-100:",maxF/S, i0*dt
        print "101-200:",maxF1/S, i1*dt
        print "201-300:",maxF2/S, i2*dt
        print "301-400:",maxF3/S, i3*dt
        print "401-500:",maxF4/S, i4*dt 
        print "501-infty:",maxF5/S, i5*dt


        # if f_MAX > 500:     
            # Fpenalty.append(1)
            # reason.append("Intraburstfrequenz zu hoch (muss sich nicht mit dem berechneten ibf decken)")
        # elif MAX < 0.09:    
            # Fpenalty.append(0.5)
            # reason.append("Intraburstfrequenz zwar zwischen 100 und 500Hz, aber nicht deutlich erhöht")
        # else:            
            # Fpenalty.append(0)
            # reason.append(" ")
        # if maxF/S < 0.09:   
            # Fpenalty.append(1)
            # reason.append("keine erhöhte Frequenz zwischen 0 und 100Hz (Interburstfrequenz)")
        #M.append(max(abs(Y[i:])))
    elif modus == 4:
        maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF) # 0  -100
        maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)    # 100-200
        maxF2 = max(absY[200/dt+1:300/dt]); i2 = list(absY).index(maxF2)    # 200-300
        maxF3 = max(absY[300/dt+1:400/dt]); i3 = list(absY).index(maxF3)    # 300-400
        maxF4 = max(absY[400/dt+1:500/dt]); i4 = list(absY).index(maxF4)    # 400-500
        maxF5 = max(absY[500/dt+1:600/dt]); i5 = list(absY).index(maxF5)    # 500-600
        maxF6 = max(absY[600/dt+1:800/dt]); i6 = list(absY).index(maxF6)    # 600-700
        maxF7 = max(absY[700/dt+1:800/dt]); i7 = list(absY).index(maxF7)    # 700-800
        maxF8 = max(absY[800/dt+1:]); i8 = list(absY).index(maxF8)      # 800-infinity

        S = maxF+maxF6+maxF7+maxF3+maxF4+maxF5+maxF8
        MAX = max([maxF3, maxF4, maxF5, maxF6, maxF7,maxF8]) #normalsiert über die Summes aller maxFs
        #print MAX
        f_MAX = list(absY).index(MAX)*dt
        print maxF/S, i0
        print MAX/S, f_MAX
        #maxis = [maxF,maxF2,maxF3,maxF4,maxF5,maxF6,maxF7,maxF8,maxF9,maxF10,maxF11,maxF12,maxF12,maxF13,maxF14,maxF15,maxF16]
        #MAX = max(maxis)
        #sMAX = sum(maxis)
        #iMAX = maxis.index(MAX)
        print "0-100:",maxF/S, i0*dt
        print "101-200:",maxF2/S, i2*dt
        print "201-300:",maxF3/S, i3*dt
        print "301-400:",maxF3/S, i3*dt
        print "401-500:",maxF4/S, i4*dt 
        print "501-600:",maxF5/S, i5*dt
        print "601-700:",maxF6/S, i6*dt
        print "701-infty:",maxF7/S, i7*dt
        print "801-infty:",maxF8/S, i8*dt
    #print MAX, iMAX+1
    
    #print MAX/sMAX, iMAX+1
    #Y[0:9] = 0
    plot(frq[i:700],abs(Y[i:700]),'r') # plotting the spectrum
    #plot(i1*dt,maxF, 'ko')
    #plot(i2*dt, maxF2, 'ko')
    xlabel('Freq [Hz]')
    ylabel('|Y(freq)|')
    

