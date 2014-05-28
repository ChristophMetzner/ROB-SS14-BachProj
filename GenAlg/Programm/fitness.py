#! usr/local/lib/python2.7 python
# coding=utf-8

from time import strftime
import profiler

import subprocess
import numpy

import chromgen
import analysis
from dipTestInst import dipTest
import HartigansDipDemo

######################################## EVALUATE_NB ###########################################################

def evaluate_NB(args):

    # ### Aufruf von analyze_Nonburst
    ausgabe = analysis.analyze_Nonburst()
    
    if ausgabe['P'] == 0:
        return {'P':0}
    max_gens = float(args.get('max_generations'))
    num_gens = float(args['_ec'].num_generations)
    m_apw = ausgabe['mean_apw']; s = ausgabe['slope']; a = ausgabe['ai']

    
    if args.get('modus') == 1:  #RS
        """
        general mean values:
        from 'Electrophysical Classes of Cat Primary Visual Cortical Neurons In Vivo as Revealed by Quantitative Analyses' 
        by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
        """
        apw_RS = 0.61; apw_min = 0.39; apw_max = 0.83   
        ai_RS = 56.4; ai_min = 43.2;    ai_max = 69.6
        slope_RS = 135; slope_min = 68; slope_max = 202
        
    ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
        if m_apw == -1:
            apw = -1000*(max_gens - num_gens)/max_gens
            print "Fehler in apw-Berechnung"
        else:
            if m_apw < apw_max and m_apw > apw_min: p = 0
            else:                                   p = -100

            if (m_apw-apw_RS) <=  0:apw = (m_apw-apw_RS)*100/(apw_RS- apw_min)+p
            else:                   apw = (m_apw-apw_RS)*(-100)/(apw_RS - apw_min)+p


        if s < 0:
            slope = -3000*(max_gens - num_gens)/max_gens
        else:   
            if s< slope_max and s > slope_min:  p = 0
            else:                   p = -100

            if s-slope_RS <= 0: slope = (s-slope_RS)*100/(slope_RS - slope_min)+p
            else:           slope = (s-slope_RS)*(-100)/(slope_RS - slope_min)+p


        if a == -1: #hart bestrafen, da nicht relevant
            ai= float(args.get('p_ai_RS'))*(max_gens - num_gens)/max_gens
        else:
            if a< ai_max and a > ai_min:    p = 0
            else:               p = -100    

            if (a-ai_RS) <= 0 : ai = (a-ai_RS)*100/(ai_RS - ai_min)+p
            else:           ai = (a-ai_RS)*(-100)/(ai_RS - ai_min)+p
        del apw_RS; del slope_RS; del ai_RS
        
        
    else: # FS
        """
        general mean values:
        from 'Electrophysical Classes of Cat Primary Visual Cortical Neurons In Vivo as Revealed by Quantitative Analyses' 
        by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
        """
        apw_FS = 0.28; slope_FS = 351; ai_FS = 9.1
        apw_min = 0.2;      apw_max = 0.36
        ai_min = -5.2;      ai_max = 23.4
        slope_min = 194;    slope_max = 508

        ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
        if ausgabe['mean_apw'] == -1:
            apw = -1000*(max_gens - num_gens)/max_gens #TODO: Strafe anpassen (-1000)
            print "Fehler in apw-Berechnung"
        else:
            if m_apw< apw_max and m_apw > apw_min:  p = 0
            else:                   p = -100    

            if (m_apw-apw_FS) <=  0:    apw = (m_apw-apw_FS)*100/(apw_FS - apw_min)+p
            else:                   apw = (m_apw-apw_FS)*(-100)/(apw_FS - apw_min)+p
            

        if ausgabe['slope'] < 0:
            slope = -5000*(max_gens - num_gens)/float(max_gens) #TODO: Strafe anpassen (-5000)
        else:
            if s< slope_max and s > slope_min:  p = 0
            else:                   p = -100    

            if s-slope_FS <= 0: slope = (s-slope_FS)*100/(slope_FS - slope_min)+p
            else:                   slope = (s-slope_FS)*(-100)/(slope_FS - slope_min)+p


        if a == -1:
            ai = float(args.get('p_ai_FS'))*(max_gens - num_gens)/max_gens
        else:       
            if a< ai_max and a > ai_min:    p = 0
            else:               p = -100         

            if (a-ai_FS) <= 0 : ai = (a-ai_FS)*100/(ai_FS - ai_min)+p
            else:               ai = (a-ai_FS)*(-100)/(ai_FS - ai_min)+p
        del apw_FS; del slope_FS; del ai_FS
        
        
    if args.get('show') == 1:
        print "Bewertung: \napw = "+str(apw)+"\nslope = "+str(slope)+"\nai = "+str(ai)
        
    return {'apw': apw, 'slope': slope, 'ai':ai, 'P':1} 
#endDEF



##################################### EVALUATE_B #############################################################
def evaluate_B(args):

    ### Aufruf von analyze_Burst
    ausgabe = analysis.analyze_Burst()
    
    if ausgabe['P'] == 0:
        return {'P':0}      
    max_gens = float(args.get('max_generations'))
    num_gens = float(args['_ec'].num_generations)
    m_apw = ausgabe['mean_apw']; m_ibf = ausgabe['mean_ibf']; m_ir = ausgabe['mean_ir']


    if args.get('modus') == 3: # IB
        """
        general mean values:
        from 'Electrophysical Classes of Cat Primary Visual Cortical Neurons In Vivo as Revealed by Quantitative Analyses' 
        by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
        """
        apw_IB = 0.6; ibf_IB = 281; ir_IB = 76.3    
        apw_min = 0.45; apw_max = 0.75
        ibf_min = 225;  ibf_max = 337
        ir_min = 63.4;  ir_max = 89.2

    ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
        if m_apw == -1:
            apw = -1000*(max_gens - num_gens)/float(max_gens) #TODO: Strafe anpassen (-1000)
            print "Fehler in apw-Berechnung"
        else:
            if m_apw< apw_max and m_apw > apw_min:  p = 0
            else:                   p = -100    

            if (m_apw-apw_IB) <=  0:apw = (m_apw-apw_IB)*100/(apw_IB - apw_min)+p
            else:           apw = (m_apw-apw_IB)*(-100)/(apw_IB - apw_min)+p
            
        
        if m_ibf == -1 and m_ir == -1:
            print "keine Bursts:"
            ibf = float(args.get('p_ibf_IB')+args.get('p_ir_IB'))*(max_gens - num_gens)/max_gens
            ir = 0
        elif m_ibf == -1:
            ibf = float(args.get('p_ibf_IB'))*(max_gens - num_gens)/max_gens
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_IB) <= 0 :  ir = (m_ir-ir_IB)*100/(ir_IB - ir_min)+p
            else:           ir = (m_ir-ir_IB)*(-100)/(ir_IB - ir_min)+p
        elif m_ir == -1:
            ir = float(args.get('p_ir_IB'))*(max_gens - num_gens)/max_gens
            
            #ibf:
            if m_ibf< ibf_max and m_ibf > ibf_min:  p = 0
            else:                   p = -100    

            if m_ibf-ibf_IB <= 0:   ibf = (m_ibf-ibf_IB)*100/(ibf_IB - ibf_min)+p
            else:           ibf = (m_ibf-ibf_IB)*(-100)/(ibf_IB - ibf_min)+p
        else:   
            #ibf:
            if m_ibf< ibf_max and m_ibf > ibf_min:  p = 0
            else:                   p = -100    

            if m_ibf-ibf_IB <= 0:   ibf = (m_ibf-ibf_IB)*100/(ibf_IB - ibf_min)+p
            else:           ibf = (m_ibf-ibf_IB)*(-100)/(ibf_IB - ibf_min)+p
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_IB) <= 0 :  ir = (m_ir-ir_IB)*100/(ir_IB - ir_min)+p
            else:           ir = (m_ir-ir_IB)*(-100)/(ir_IB - ir_min)+p
            
            
    else: # mode = 4 (CH)
        """
        general mean values:
        from 'Electrophysical Classes of Cat Primary Visual Cortical Neurons In Vivo as Revealed by Quantitative Analyses' 
        by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
        """
        apw_CH = 0.31; ibf_CH = 495; ir_CH = 53.9
        apw_min = 0.21; apw_max = 0.41
        ibf_min = 410;  ibf_max = 580
        ir_min = 49;    ir_max = 58.8
        
    ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
        if m_apw == -1:
            apw = -1000*(max_gens - num_gens)/max_gens #TODO: Strafe anpassen (-1000)
            print "Fehler in apw-Berechnung"
        else:
            if m_apw < apw_max and m_apw > apw_min: p = 0
            else:                   p = -100    

            if (m_apw-apw_CH) <=  0:apw = (m_apw-apw_CH)*100/(apw_CH - apw_min)+p
            else:           apw = (m_apw-apw_CH)*(-100)/(apw_CH - apw_min)+p


        if m_ibf == -1 and m_ir == -1:
            print "keine Bursts:"
            ibf = float(args.get('p_ibf_CH')+args.get('p_ir_CH'))*(max_gens - num_gens)/max_gens
            ir = 0
        elif m_ibf == -1:
            ibf = float(args.get('p_ibf_CH'))*(max_gens - num_gens)/max_gens
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_CH) <= 0 :  ir = (m_ir-ir_CH)*100/(ir_CH - ir_min)+p
            else:           ir = (m_ir-ir_CH)*(-100)/(ir_CH - ir_min)+p
        elif m_ir == -1:
            ir = float(args.get('p_ir_CH'))*(max_gens - num_gens)/max_gens
            
            #ibf:
            if m_ibf < ibf_max and m_ibf > ibf_min: p = 0
            else:                   p = -100    

            if m_ibf-ibf_CH <= 0:   ibf = (m_ibf-ibf_CH)*100/(ibf_CH - ibf_min)+p
            else:           ibf = (m_ibf-ibf_CH)*(-100)/(ibf_CH - ibf_min)+p
        else:   
            #ibf:
            if m_ibf < ibf_max and m_ibf > ibf_min: p = 0
            else:                   p = -100    

            if m_ibf-ibf_CH <= 0:   ibf = (m_ibf-ibf_CH)*100/(ibf_CH - ibf_min)+p
            else:           ibf = (m_ibf-ibf_CH)*(-100)/(ibf_CH - ibf_min)+p
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_CH) <= 0 :  ir = (m_ir-ir_CH)*100/(ir_CH - ir_min)+p
            else:           ir = (m_ir-ir_CH)*(-100)/(ir_CH - ir_min)+p
            
            
    if args.get('show') == 1:   
        print "Bewertungen: \napw = "+str(apw)+"\nibf = "+str(ibf)+"\nir = "+str(ir)        
        
    return {'apw': apw, 'ibf': ibf, 'ir':ir, 'P':1}
#endDEF 









############################################# EVALUATE_PARM ################################################################
def evaluate_param(candidates, args):
    
    """
     Informationen für die Simulation:
    """
    for chromosome in candidates:
        chromgen.calc_dens(chromosome,0, args) 

    if args.get('BS') == 1:
        index = open("./GenAlg/Programm/Speicher/index.txt","w")
    else:
        index = open("C:\Python27\GenAlg\Programm\Analyse\index.txt","w")
    index.write(str(len(candidates)) + "\n")
    index.close()
    ####################
    
    if args.get('show') == 1:
        print "========================================="   
        print strftime("%d.%m.%Y %H:%M:%S")+": "+str(args['_ec'].num_generations+1)+". Generation!!"
        print "========================================="
        print "start evaluating"
        #k = 0
        #for chrom in candidates:
        #   print "Neuron ",k
        #   k = k+1
        #   for allel in chrom:
        #       print allel
        print "- simulating "+str(len(candidates))+" neurons..."
    

    """
     - Aufruf der Simulation; -PySim_(i) -> 'SampleCell'
    """
    if args.get('BS') == 1:
        subprocess.check_call(['./neuroConstruct_1.6.0/nC.sh', 
                    '-python', 
                    './GenAlg/Programm/MultiConductance.py'])
        profiler.sleep(0, 10)
    else:
        uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Programm\MultiConductance.py"'] # muessen alles Strings sein 
        externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
        p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) )
        p.wait()
        profiler.sleep(0, 50)




    """
     -ISI bestimmen
     -danach Prüfung auf Unimodalitaet oder Bimodalitaet --> Hartigan
     -gibt Objekte mit index, dip, p zurück, dann in Liste HDinst als Objekte dipTest(idx, dip, p) gespeichert #### 
    """
    if args.get('show') == 1: print "- analyzing the InterSpikeIntervals: "+str(len(candidates))

    HDinst = []
    for i in range(len(candidates)):

        ISI = analysis.analyze_ISI(i)
        hist = ISI['hist']

        if ISI['ISI'][0] == -1: # keine Spikes, damit nicht zu gebrauchen! 
            if args.get('show') == 1: print "            Neuron "+str(i)+" does not fire"
            HDinst.append(dipTest(i, 0, 3))  

        else: #Spikes vorhanden: prüfen, ob sie auch bursten!
            if args.get('show') == 1: print "            Neuron "+ str(i)+ " fires"

            #hartigan ist komisch:
            if args.get('modus') == 3 or args.get('modus') == 4:
                # schaue nochmal, ob es nicht doch zwei peaks gibt:
                k = []
                r = []
                start = 0
                for j in range(len(hist)):
                    if sum(hist) >= 150:
                        start = 2
                        break
                    if hist[j] > 1:
                        k.append(r)
                        r = []
                        if j < len(hist)-1:
                            if hist[j+1] == 0:
                                start = 1
                            else: start = 0
                    elif hist[j]== 0 and start == 1:
                        r.append(j)
                    else: continue

                
                r = 0
                if start != 2:
                    for h in k:
                        if len(h)>= 4:
                            r = r+1
                    if r >= 1:
                        HDinst.append(dipTest(i, 0, 0.0))
                        hart = HartigansDipDemo.main(hist,i)
                        print "Hat zwei Peaks, Hartigan wäre:", hart.get_p()
                    else:
                        HDinst.append(HartigansDipDemo.main(ISI['hist'], i))
                else:
                    HDinst.append(dipTest(i, 0, 3))
            else: #RS, FS
                print "a"
                start = 0
                if sum(hist) >= 150:
                    start = 2
                    
                if start == 2:
                    HDinst.append(dipTest(i, 0, 3))
                else:
                    HDinst.append(HartigansDipDemo.main(ISI['hist'], i))
            print HDinst[-1]        
    if args.get('show') == 1: print "================================="
    """
    - Fitness bestimmen: 
    """
    Fit = []
    for inst in HDinst:
        print inst,inst.get_index(), inst.get_p()
        ### speichern der Indizes in extra Datei hinter len(cand) für Ex5_MultiSimGenerate
        if args.get('BS') == 1:
            index = open("./GenAlg/Programm/Speicher/index.txt","a")
        else:
            index = open("C:\Python27\GenAlg\Programm\Analyse\index.txt","a")
        index.write(str(inst.get_index())+'\n'); index.close()
        ################

        p_value = inst.get_p(); mode= args.get('modus')
        burst = 0

        if args.get('show') == 1: print strftime("%d.%m.%Y %H:%M:%S")+": Neuron "+str(inst.get_index())+"\np-Wert = "+str(p_value)
    
        #if p_value >= 0.01 and p_value <= 1.0 and (mode == 1 or mode == 2): #Non-Bursting
        if p_value == 3 or p_value == 2:    fitness = -20000.0
        elif mode == 1 or mode == 2:
        
            ### für jede NB-Instanz müssen noch einmal Simulationen für verschiedene Stromstärken durchgeführt werden! 
            if args.get('BS') == 1:
                subprocess.check_call(['./neuroConstruct_1.6.0/nC.sh', 
                            '-python', 
                            './GenAlg/Programm/MultiCurrent.py'])
                profiler.sleep(0, 14)
            else:
                uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Programm\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) ); p.wait()
                profiler.sleep(0, 20)

            ausgabeNB = evaluate_NB(args)
            if ausgabeNB['P'] == 0: #hat sich aufgehangen
                fitness = -30000.0
            else:
                fitness = float(args.get('W_apw'))*ausgabeNB['apw']\
                        + float(args.get('W_slope'))*ausgabeNB['slope']\
                        + float(args.get('W_ai'))*ausgabeNB['ai']           
                                # Fourieranalyse für RS und FS:
            
                F = Fourier_analyse(args.get('BS'), args)
                reason = F['R']
                P = F['P']
                schon_besucht = 0
                #for i in range(len(P)):
                #   if P[i] == 1:
                #       fitness = -20000.0
                #       print "Fourier: ",reason[i]
                #       break
                #   elif P[i] == 0.5:
                #       if schon_besucht == 0:
                #           fitness = fitness-10000.0
                #           print "Fourier: ",reason[i]
                #           schon_besucht = 1
                #   else:
                #       pass
                F = Fourier_analyse(args.get('BS'), args)
                print "Fourier: ",F['M']
                for m in F['M']:
                    if args.get('modus') == 1:
                        if m > args.get('thrFourier'):
                            fitness = fitness + args.get('penFourier')
                            print "Fourier-Penalty: ", args.get('penFourier')
                            break
                    else:
                        if m < args.get('thrFourier'):
                            fitness = fitness + args.get('penFourier')
                            break
                
        elif mode == 3 or mode == 4: #Bursting

            ### für jede NB-Instanz müssen noch einmal Simulationen für 10 verschiedene Stromstärken durchgeführt werden! 
            if args.get('BS') == 1:
                subprocess.check_call(['./neuroConstruct_1.6.0/nC.sh', 
                        '-python', 
                        './GenAlg/Programm/MultiCurrent.py'])
                profiler.sleep(0, 20)
            else:
                uebergabeWerte = [  "-python", 
                            '"C:\Python27\GenAlg\Programm\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) ); p.wait() 
                profiler.sleep(0, 20)

            ausgabeB = evaluate_B(args)
            if ausgabeB['P'] == 0: #hat sich aufgehangen
                fitness = -30000.0
            else:
                fitness = float(args.get('W_apw'))*ausgabeB['apw']\
                        + float(args.get('W_ibf'))*ausgabeB['ibf']\
                        + float(args.get('W_ir'))*ausgabeB['ir'] 

                F = Fourier_analyse(args.get('BS'), args)
                reason = F['R']
                P = F['P']
                schon_besucht = 0
                for i in range(len(P)):
                    if P[i] == 1:
                        fitness = -20000.0
                        print "Fourier: ",reason[i]
                        break
                    elif P[i] == 0.5:
                        if schon_besucht == 0:
                            fitness = fitness-10000.0
                            print "Fourier: ",reason[i]
                            schon_besucht = 1
                    else:
                        pass
            
        else:   fitness = -15000.0

        if type(fitness) is numpy.ndarray:  Fit.append(fitness[0])
        else:                   Fit.append(fitness)
        
        if args.get('show') == 1:
            print " ==> Fitness = "+str(fitness)
            print "================================="

    #Dateien leeren, da später die Werte angehängt werden.
    if args.get('BS') == 1:
        density = open("./GenAlg/Programm/Speicher/density.txt","w"); density.close()
    else:   
        density = open("C:\Python27\GenAlg\Programm\Analyse\density.txt","w"); density.close()
    return Fit
#endDEF




"""
Fourieranalyse des Membranpotenzialverlaufs auf Bursts
"""
def Fourier_analyse(BS, args):
    M = []
    Fpenalty = []
    reason = []
    for z in range(args.get('numCurrents')):    
        if BS == 1:
            if args.get('modus') == 1 or args.get('modus') == 2:
                filename = "./Pyr_RS/simulations/multiCurrent_"+str(z)+"/CellGroup_1_0.dat"
            else: 
                filename = "./Pyr_IB/simulations/multiCurrent_"+str(z)+"/CellGroup_1_0.dat"
        else:
            if args.get('modus') == 1 or args.get('modus') == 2:
                filename = "C:\Python27\Pyr_RS\simulations\multiCurrent_"+str(z)+"\CellGroup_1_0.dat"
            else:
                filename = "C:\Python27\Pyr_IB\simulations\multiCurrent_"+str(z)+"\CellGroup_1_0.dat"
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
                    
        #density = numpy.zeros(10001)
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

        Fs = 20000.0;  # sampling rate
        Ts = 1.0/Fs; # sampling interval
        #t = numpy.arange(0,0.50005,Ts) # time vector
        t = numpy.arange(0,0.5,Ts) # time vector
        y = density

        """
        calculates Single-Sided Amplitude Spectrum of y(t)
        From:   http://glowingpython.blogspot.de/2011/08/how-to-plot-frequency-spectrum-with.html
        (04.10.13, 17:00 Uhr)
        """
        n = len(y) # length of the signal (10001)
        k = numpy.arange(n)
        T = n/Fs # timestep 
        dt = 2
        Y = numpy.fft.fft(y)/n # fft computing and normalization
        Y = Y[range(n/2)]
        absY = abs(Y)
        
        # Abfangen der ersten i Werte, in denen sich die Kurve noch senkt
        slope = (absY[1]-absY[0])/dt
        i = 0
        while(slope<0):
            if i < len(absY):
                i = i+1
                slope = (absY[i]-absY[i-1])/dt
                p = 0
            else:
                #Fpenalty.append(1)
                #reason.append("steigng immer kleiner 0")
                #M.append(0)
                p = 1
                #return{'P':Fpenalty, 'R': reason,'M':M}
                break
        if p == 0:
            ''' Analysieren, wo die Frequenzen angesiedelt sind:
                Intraburstfrequenzen:
                    IB: 281 +/- 56 = [225, 337], [170, 402]
                    CH: 495 +/- 85 = [410, 580], [296,701]
                Interburstfrequenzen:
                    IB/CH: [0, 100] nach Schätzungen
            '''

            if args.get('modus') == 1 or args.get('modus') == 2:
                # Abtasten der Intervalle in 100Hz-Schritten, extrahier jeweils das Maximum
                if i < 100/dt:
                    maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF) # 0  -100
                else:
                    maxF = 0; i0 = 0
                maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)    # 100-200
                maxF2 = max(absY[200/dt+1:]);   i2 = list(absY).index(maxF2)        # 200-infty
                #maxF3 = max(absY[300/dt+1:400/dt]);    i3 = list(absY).index(maxF3)    # 300-400
                #maxF4 = max(absY[400/dt+1:500/dt]);    i4 = list(absY).index(maxF4)    # 400-500
                #maxF5 = max(absY[300/dt+1:]);  i5 = list(absY).index(maxF5)    # 300-infty
    
                S = maxF+maxF1+maxF2
                
                MAX = max([maxF1, maxF2]) # 100-infinity,  normalsiert über die Summe aller maxFs
                f_MAX = list(absY).index(MAX)*dt

                print maxF, i0
                print MAX, f_MAX

                if f_MAX > 200:       
                    Fpenalty.append(0.5)
                    reason.append("Frequenz zu hoch")
                #elif MAX < 0.09:     
                #   Fpenalty.append(0.5)
                #   reason.append("Intraburstfrequenz zwar zwischen 100 und 500Hz, aber nicht deutlich erhöht")
                else:              
                    Fpenalty.append(0)
                    reason.append(" ")
                #if maxF/S < 0.09:    
                    #Fpenalty.append(1)
                    #reason.append("keine erhöhte Frequenz zwischen 0 und 100Hz (Interburstfrequenz)")
                m = max(abs(Y[i:]))
                print m
                M.append(m)
            if args.get('modus') == 3: #IB
                # Abtasten der Intervalle in 100Hz-Schritten, extrahier jeweils das Maximum
                if i < 100/dt:
                    maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF) # 0  -100
                else:
                    maxF = 0; i0 = 0
                maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)    # 100-200
                maxF2 = max(absY[200/dt+1:300/dt]); i2 = list(absY).index(maxF2)    # 200-300
                maxF3 = max(absY[300/dt+1:400/dt]); i3 = list(absY).index(maxF3)    # 300-400
                maxF4 = max(absY[400/dt+1:500/dt]); i4 = list(absY).index(maxF4)    # 400-500
                maxF5 = max(absY[500/dt+1:]);   i5 = list(absY).index(maxF5)    # 500-600
    
                S = maxF+maxF1+maxF2+maxF3+maxF4+maxF5
                
                MAX = max([maxF1, maxF2, maxF3, maxF4, maxF5]) # 100-infinity,  normalsiert über die Summe aller maxFs
                f_MAX = list(absY).index(MAX)*dt

                print maxF/S, i0
                print MAX/S, f_MAX

                if f_MAX > 500:       
                    Fpenalty.append(1)
                    reason.append("Intraburstfrequenz zu hoch (muss sich nicht mit dem berechneten ibf decken)")
                elif MAX < 0.09:      
                    Fpenalty.append(0.5)
                    reason.append("Intraburstfrequenz zwar zwischen 100 und 500Hz, aber nicht deutlich erhöht")
                else:              
                    Fpenalty.append(0)
                    reason.append(" ")
                if maxF/S < 0.09:     
                    Fpenalty.append(1)
                    reason.append("keine erhöhte Frequenz zwischen 0 und 100Hz (Interburstfrequenz)")
                M.append(max(abs(Y[i:])))
                            
            elif args.get('modus') == 4:
                # Abtasten der Intervalle in 100Hz-Schritten, extrahier jeweils das Maximum
                if i <100/dt:
                    maxF = max(absY[i:100/dt]); i0 = list(absY).index(maxF) # 0  -100
                else:
                    maxF = 0; i0 = 0
                maxF1 = max(absY[100/dt+1:200/dt]); i1 = list(absY).index(maxF1)    # 100-200
                maxF2 = max(absY[200/dt+1:300/dt]); i2 = list(absY).index(maxF2)    # 200-300
                maxF3 = max(absY[300/dt+1:400/dt]); i3 = list(absY).index(maxF3)    # 300-400
                maxF4 = max(absY[400/dt+1:500/dt]); i4 = list(absY).index(maxF4)    # 400-500
                maxF5 = max(absY[500/dt+1:600/dt]); i5 = list(absY).index(maxF5)    # 500-600
                maxF6 = max(absY[600/dt+1:800/dt]); i6 = list(absY).index(maxF6)    # 600-700
                maxF7 = max(absY[700/dt+1:800/dt]); i7 = list(absY).index(maxF7)    # 700-800
                maxF8 = max(absY[800/dt+1:900/dt]); i8 = list(absY).index(maxF8)        # 700-infinity
                maxF9 = max(absY[900/dt+1:]); i9 = list(absY).index(maxF9)
    
                S = maxF+maxF1+maxF2+maxF6+maxF7+maxF3+maxF4+maxF5+maxF8+maxF9
                print S
                MAX = max([maxF1,maxF2,maxF3, maxF4, maxF5, maxF6, maxF7,maxF8,maxF9]) #normalsiert über die Summe aller maxFs
                print MAX
                f_MAX = list(absY).index(MAX)*dt
                print f_MAX
                print MAX/S
                print maxF/S, i0
                if f_MAX > 900:        
                    Fpenalty.append(1)
                    reason.append("Intraburstfrequenz zu hoch (muss sich nicht mit dem berechneten ibf decken)")
                elif MAX/S < 0.09:     
                    Fpenalty.append(0.5)
                    reason.append("Intraburstfrequenz zwar zwischen 300 und 800Hz, aber nicht deutlich erhöht")
                else:              
                    Fpenalty.append(0)
                    reason.append(" ")         
                if maxF/S < 0.09:      
                    Fpenalty.append(1)
                    reason.append("keine erhöhte Frequenz zwischen 0 und 100Hz (Interburstfrequenz)")
                M.append(0)
            else:
                Fpenalty.append(0)
                reason.append(" ")
                M.append(max(abs(Y[i:])))
        else:
            Fpenalty.append(1)
            reason.append("Fiel die ganze Zeit ???")
            M.append(0)
    return{'P':Fpenalty, 'R':reason, 'M':M}
