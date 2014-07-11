# coding=utf-8

from time import strftime

import subprocess
import numpy
import time

import nevo.util.projconf as projconf
import nevo.chromgen as chromgen
import analysis
from diptest_inst import DipTest
import hartigans_dip_demo

CONDUCTANCE_PREFIX = "PySim_"
CURRENT_PREFIX = "multiCurrent_"

######################################## EVALUATE_NB ###########################################################

def evaluate_NB(pconf, logger, args):
    show = int(pconf.get("showExtraInfo", "Global"))

    # ### Aufruf von analyze_Nonburst
    analyzer = analysis.Analysis(pconf)
    ausgabe = analyzer.analyze_Nonburst()
    
    if ausgabe['P'] == 0:
        return {'P':0}

    m_apw = ausgabe['mean_apw']; s = ausgabe['slope']; a = ausgabe['ai']

    
    if args["mode"] == "RS":
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
            apw = -1000
            logger.error("Fehler in apw-Berechnung")
        else:
            if m_apw < apw_max and m_apw > apw_min: p = 0
            else:                                   p = -100

            if (m_apw-apw_RS) <=  0:apw = (m_apw-apw_RS)*100/(apw_RS- apw_min)+p
            else:                   apw = (m_apw-apw_RS)*(-100)/(apw_RS - apw_min)+p


        if s < 0:
            slope = -3000
        else:   
            if s< slope_max and s > slope_min:  p = 0
            else:                   p = -100

            if s-slope_RS <= 0: slope = (s-slope_RS)*100/(slope_RS - slope_min)+p
            else:           slope = (s-slope_RS)*(-100)/(slope_RS - slope_min)+p


        if a == -1: #hart bestrafen, da nicht relevant
            ai= float(args['penalty_ai_RS'])
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
            apw = -1000 #TODO: Strafe anpassen (-1000)
            logger.error("Fehler in apw-Berechnung")
        else:
            if m_apw< apw_max and m_apw > apw_min:  p = 0
            else:                   p = -100    

            if (m_apw-apw_FS) <=  0:    apw = (m_apw-apw_FS)*100/(apw_FS - apw_min)+p
            else:                   apw = (m_apw-apw_FS)*(-100)/(apw_FS - apw_min)+p
            

        if ausgabe['slope'] < 0:
            slope = -5000 #TODO: Strafe anpassen (-5000)
        else:
            if s< slope_max and s > slope_min:  p = 0
            else:                   p = -100    

            if s-slope_FS <= 0: slope = (s-slope_FS)*100/(slope_FS - slope_min)+p
            else:                   slope = (s-slope_FS)*(-100)/(slope_FS - slope_min)+p


        if a == -1:
            ai = float(args['penalty_ai_FS'])
        else:       
            if a< ai_max and a > ai_min:    p = 0
            else:               p = -100         

            if (a-ai_FS) <= 0 : ai = (a-ai_FS)*100/(ai_FS - ai_min)+p
            else:               ai = (a-ai_FS)*(-100)/(ai_FS - ai_min)+p
        del apw_FS; del slope_FS; del ai_FS
        
        
    if show == 1:
        logger.info("Bewertung: \napw = " + repr(apw) + "\n"\
                    + "slope = " + repr(slope) + "\n"\
                    + "ai = "+repr(ai))
        
    return {'apw': apw, 'slope': slope, 'ai':ai, 'P':1} 
#endDEF



##################################### EVALUATE_B #############################################################
def evaluate_B(pconf, logger, args):
    show = int(pconf.get("showExtraInfo", "Global"))
    
    ### Aufruf von analyze_Burst
    analyzer = analysis.Analysis(pconf)
    ausgabe = analyzer.analyze_Burst()
    
    if ausgabe['P'] == 0:
        return {'P':0}      

    m_apw = ausgabe['mean_apw']; m_ibf = ausgabe['mean_ibf']; m_ir = ausgabe['mean_ir']


    if args["mode"] == "IB":
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
            apw = -1000 #TODO: Strafe anpassen (-1000)
            logger.error("Fehler in apw-Berechnung")
        else:
            if m_apw< apw_max and m_apw > apw_min:  p = 0
            else:                   p = -100    

            if (m_apw-apw_IB) <=  0:apw = (m_apw-apw_IB)*100/(apw_IB - apw_min)+p
            else:           apw = (m_apw-apw_IB)*(-100)/(apw_IB - apw_min)+p
            
        
        if m_ibf == -1 and m_ir == -1:
            logger.info("keine Bursts:")
            ibf = float(args['penalty_ibf_IB']+args['penalty_ir_IB'])
            ir = 0
        elif m_ibf == -1:
            ibf = float(args['penalty_ibf_IB'])
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_IB) <= 0 :  ir = (m_ir-ir_IB)*100/(ir_IB - ir_min)+p
            else:           ir = (m_ir-ir_IB)*(-100)/(ir_IB - ir_min)+p
        elif m_ir == -1:
            ir = float(args['penalty_ir_IB'])
            
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
            
            
    else: # mode CH
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
            apw = -1000 #TODO: Strafe anpassen (-1000)
            logger.error("Fehler in apw-Berechnung")
        else:
            if m_apw < apw_max and m_apw > apw_min: p = 0
            else:                   p = -100    

            if (m_apw-apw_CH) <=  0:apw = (m_apw-apw_CH)*100/(apw_CH - apw_min)+p
            else:           apw = (m_apw-apw_CH)*(-100)/(apw_CH - apw_min)+p


        if m_ibf == -1 and m_ir == -1:
            logger.info("keine Bursts:")
            ibf = float(args['penalty_ibf_CH']+args['penalty_ir_CH'])
            ir = 0
        elif m_ibf == -1:
            ibf = float(args['penalty_ibf_CH'])
            
            #ir:
            if m_ir < ir_max and m_ir > ir_min:     p = 0
            else:                   p = -100    
    
            if (m_ir-ir_CH) <= 0 :  ir = (m_ir-ir_CH)*100/(ir_CH - ir_min)+p
            else:           ir = (m_ir-ir_CH)*(-100)/(ir_CH - ir_min)+p
        elif m_ir == -1:
            ir = float(args['penalty_ir_CH'])
            
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
            
            
    if show == 1:   
        logger.info("Bewertungen: \napw = " + repr(apw) + "\nibf = "\
                    + repr(ibf) + "\nir = " + repr(ir))
        
    return {'apw': apw, 'ibf': ibf, 'ir':ir, 'P':1}
#endDEF 









############################################# EVALUATE_PARM ################################################################
def evaluate_param(candidates, args):
    """Expects candidates in their chromosome representations (see chromgen)
    
    Returns a list of fitness values.
    """
    pconf = args["pconf"]
    logger = pconf.get_logger("fitness")
    
    candidate_size = len(candidates)
    chromosomes = candidates
    channels_list = []
    if candidate_size < 1:
        logger.warning("No candidates specified")
        return []

    show = int(pconf.get("showExtraInfo", "Global"))
    for chromosome in chromosomes:
        candidate = chromgen.chromosome_to_channels(chromosome)
        channels_list.append(candidate)
    
    if show == 1:
        logger.info("=========================================")
        #logger.info(strftime("%d.%m.%Y %H:%M:%S")+": "+repr(args['_ec'].num_generations+1)+". Generation!")
        logger.info("=========================================")
        logger.info("start evaluating")
        #k = 0
        #for candidate in channels_list:
        #   logger.info("Neuron ", repr(k))
        #   k = k+1
        #   for allel in candidate:
        #       logger.info(repr(allel))
        logger.info("- simulating " + repr(candidate_size) + " neurons...")
    

    """
     - Aufruf der Simulation; -PySim_(i) -> 'SampleCell'
    """
    pconf.invoke_neurosim(logger, "conductance", candidates = channels_list, prefix = CONDUCTANCE_PREFIX)

    """
     -ISI bestimmen
     -danach Prüfung auf Unimodalitaet oder Bimodalitaet --> Hartigan
     -gibt Objekte mit index, dip, p zurück, dann in Liste HDinst als Objekte DipTest(idx, dip, p) gespeichert #### 
    """
    if show == 1:
        logger.info("- analyzing the InterSpikeIntervals: " + repr(candidate_size))

    HDinst = []
    for i in range(candidate_size):
        analyzer = analysis.Analysis(pconf)
        ISI = analyzer.analyze_ISI(i)
        hist = ISI['hist']

        if ISI['ISI'][0] == -1: # keine Spikes, damit nicht zu gebrauchen! 
            if show == 1:
                logger.info("            Neuron " + repr(i) + " does not fire")
            HDinst.append(DipTest(i, 0, 3))  

        else: #Spikes vorhanden: prüfen, ob sie auch bursten!
            if show == 1:
                logger.info("            Neuron " + repr(i) + " fires")

            #hartigan ist komisch:
            if args["mode"] == "IB" or args["mode"] == "CH":
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
                        HDinst.append(DipTest(i, 0, 0.0))
                        hart = hartigans_dip_demo.main(pconf, hist, i)
                        logger.info("Hat zwei Peaks, Hartigan wäre: " + repr(hart.get_p()))
                    else:
                        HDinst.append(hartigans_dip_demo.main(pconf, ISI['hist'], i))
                else:
                    HDinst.append(DipTest(i, 0, 3))
            else: #RS, FS
                start = 0
                if sum(hist) >= 150:
                    start = 2
                    
                if start == 2:
                    HDinst.append(DipTest(i, 0, 3))
                else:
                    HDinst.append(hartigans_dip_demo.main(pconf, ISI['hist'], i))
            logger.debug("HDinst: " + repr(HDinst[-1]))
    if show == 1:
        logger.info("=================================")
    """
    - Fitness bestimmen: 
    """
    Fit = []
    for inst in HDinst:
        logger.debug("HDinst: " + repr(inst))

        p_value = inst.get_p(); mode= args["mode"]
        burst = 0

        if show == 1:
            logger.info(strftime("%d.%m.%Y %H:%M:%S")+": Neuron "
                        + repr(inst.get_index()))
            logger.info("p-Wert = " + repr(p_value))
    
        #if p_value >= 0.01 and p_value <= 1.0 and (mode == "RS" or mode == "FS"): #Non-Bursting
        if p_value == 3 or p_value == 2:
            fitness = -20000.0
        elif mode == "RS" or mode == "FS":
        
            ### für jede NB-Instanz müssen noch einmal Simulationen für verschiedene Stromstärken durchgeführt werden!
            pconf.invoke_neurosim(logger, type = "current", candidates = [channels_list[inst.get_index()]], prefix = CURRENT_PREFIX)

            ausgabeNB = evaluate_NB(pconf, logger, args)
            if ausgabeNB['P'] == 0: #hat sich aufgehangen
                fitness = -30000.0
            else:
                fitness = float(args['W_apw']) * ausgabeNB['apw']\
                        + float(args['W_slope']) * ausgabeNB['slope']\
                        + float(args['W_ai']) * ausgabeNB['ai']
                # Fourieranalyse für RS und FS:
            
                F = Fourier_analyse(pconf, logger, args, prefix = CURRENT_PREFIX)
                reason = F['R']
                P = F['P']
                schon_besucht = 0
                #for i in range(len(P)):
                #   if P[i] == 1:
                #       fitness = -20000.0
                #       logger.info("Fourier: " + reason[i])
                #       break
                #   elif P[i] == 0.5:
                #       if schon_besucht == 0:
                #           fitness = fitness-10000.0
                #           logger.info("Fourier: " + reason[i])
                #           schon_besucht = 1
                #   else:
                #       pass
                F = Fourier_analyse(pconf, logger, args, prefix = CURRENT_PREFIX)
                logger.info("Fourier: " + repr(F['M']))
                for m in F['M']:
                    if args["mode"] == "RS":
                        if m > args['thrFourier']:
                            fitness = fitness + args['penFourier']
                            logger.info("Fourier-Penalty: " + repr(args['penFourier']))
                            break
                    else:
                        if m < args['thrFourier']:
                            fitness = fitness + args['penFourier']
                            break
                
        elif mode == "IB" or mode == "CH": #Bursting

            ### für jede NB-Instanz müssen noch einmal Simulationen für 10 verschiedene Stromstärken durchgeführt werden!
            pconf.invoke_neurosim(logger, "current", candidates = [channels_list[inst.get_index()]], prefix = CURRENT_PREFIX)

            ausgabeB = evaluate_B(pconf, logger, args)
            if ausgabeB['P'] == 0: #hat sich aufgehangen
                fitness = -30000.0
            else:
                fitness = float(args['W_apw'])*ausgabeB['apw']\
                        + float(args['W_ibf'])*ausgabeB['ibf']\
                        + float(args['W_ir'])*ausgabeB['ir'] 

                F = Fourier_analyse(pconf, logger, args, prefix = CURRENT_PREFIX)
                reason = F['R']
                P = F['P']
                schon_besucht = 0
                for i in range(len(P)):
                    if P[i] == 1:
                        fitness = -20000.0
                        logger.info("Fourier: " + reason[i])
                        break
                    elif P[i] == 0.5:
                        if schon_besucht == 0:
                            fitness = fitness-10000.0
                            logger.info("Fourier: " + reason[i])
                            schon_besucht = 1
                    else:
                        pass
            
        else:   fitness = -15000.0

        if type(fitness) is numpy.ndarray:  Fit.append(fitness[0])
        else:                   Fit.append(fitness)
        
        if show == 1:
            logger.info(" ==> Fitness = " + repr(fitness))
            logger.info("=================================")
    return Fit
#endDEF




"""
Fourieranalyse des Membranpotenzialverlaufs auf Bursts
"""
def Fourier_analyse(pconf, logger, args, prefix, offset = 0):
    M = []
    Fpenalty = []
    reason = []
    num_currents = int(pconf.get_list("currents", "Simulation")[0])
    for z in range(num_currents):
        filename = pconf.local_path(pconf.get_sim_project_path(),
                                    "simulations",
                                    prefix + repr(z + offset),
                                    "CellGroup_1_0.dat")
        try:
            density = numpy.zeros(20000)
            with open(filename, "r") as fileDE:
                densities_list= fileDE.read().split('#\n')      
                densities = densities_list[0].split('\n')
                for i in range(len(densities)):
                    dens = densities[i].strip()
                    if dens != "":
                        try:
                            density[i] = float(dens)
                        except IndexError:
                            pass
        except:
            logger.error("Could not open file '" + filename + "'")
            raise

        Fs = 20000.0  # sampling rate
        Ts = 1.0/Fs # sampling interval
        #t = numpy.arange(0, 0.50005, Ts) # time vector
        t = numpy.arange(0, 0.5, Ts) # time vector
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
                #return{'P':Fpenalty, 'R': reason, 'M':M}
                break
        if p == 0:
            ''' Analysieren, wo die Frequenzen angesiedelt sind:
                Intraburstfrequenzen:
                    IB: 281 +/- 56 = [225, 337], [170, 402]
                    CH: 495 +/- 85 = [410, 580], [296, 701]
                Interburstfrequenzen:
                    IB/CH: [0, 100] nach Schätzungen
            '''

            if args["mode"] == "RS" or args["mode"] == "FS":
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

                logger.info(repr(maxF) + " " + repr(i0))
                logger.info(repr(MAX) + " " + repr(f_MAX))

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
                logger.debug("Max from i onwards: " + repr(m))
                M.append(m)
            if args["mode"] == "IB":
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

                logger.info(repr(maxF/S) + " " + repr(i0))
                logger.info(repr(MAX/S) + " " + repr(f_MAX))

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
                            
            elif args["mode"] == "CH":
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
                logger.debug("S = " + repr(S))
                MAX = max([maxF1, maxF2, maxF3, maxF4, maxF5, maxF6, maxF7, maxF8, maxF9]) #normalsiert über die Summe aller maxFs
                logger.debug("MAX = " + repr(MAX))
                f_MAX = list(absY).index(MAX)*dt
                logger.debug("f_MAX = " + repr(f_MAX))
                logger.debug("MAX/S = " + repr(MAX/S))
                logger.debug("maxF/S = " + repr(maxF/S) + ", i0 = " + repr(i0))
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
