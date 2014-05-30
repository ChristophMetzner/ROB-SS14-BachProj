# coding=utf-8
# Datei zum Auswerten der Ergebnisse:

# 1. Simulieren
# 2. Analysieren
# 3. Berwerten
# 4. grafisch darstellen

import numpy
import subprocess
from time import time, sleep, strftime



# verwendete eigene Module
import calc_density
import analysis


def auswerten( Anzahl = None, modus = None, currents = None, simulieren = None, BS = None, timestep = None):
    
    if Anzahl is None:
        Anzahl = 1
    if modus is None:
        modus = 1
        mode = 1
    elif modus == 1 or modus == 2:
        mode = 1; proj_name = "Pyr_RS"
    elif modus == 3 or modus == 4:
        mode = 2; proj_name = "Pyr_IB"
    if currents is None:
        currents = [3,0.2,0.3]
    if simulieren is None:
        simulieren = 0
    if BS is None:
        BS = 1
    if timestep is None:
        dt = 0.05
    else:
        dt = timestep

    if BS == 1:
        if mode == 1: proj_path = "./Pyr_RS/Pyr_RS.ncx"
        else: proj_path = "./Pyr_IB/Pyr_IB.ncx"
    else:
        if mode == 1: proj_path = "C:\Python27\Pyr_RS\Pyr_RS.ncx"
        else:   proj_path = "C:\Python27\Pyr_IB\Pyr_IB.ncx" 

    sim_config = "Default Simulation Configuration"
    stimulation = "Input_0"
    cell = "L5TuftedPyrRS"
    #dt = 0.05
    duration = 500


    print "##############################"
    print "Es startet die Auswertung von "+str(Anzahl)+" Ergebnissen im Modus "+str(mode)
    print "##############################"
    
    if BS == 1:
        filename = "./GenAlg/Auswertung/Config.txt"
    else:
        filename = "C:\Python27\GenAlg\Auswertung\Config.txt"
    config = open(filename, "w")
    config.write(str(proj_name)+"\n"
                    +str(proj_path)+"\n"
                    +str(sim_config)+"\n"
                    +str(stimulation)+"\n"
                    +str(cell)+"\n"
                    +str(duration)+"\n"
                    +str(dt)+"\n"
                    +str(currents)+"\n"
                    +str(modus))

    config.close()      
    
    PaiRS = -3500; PaiFS = -3500; PibfIB = -2500; PibfCH = -3500; PirIB = -3500; PirCH = -2500
    for i in range(Anzahl):
        
        if simulieren != 0:
            print " Fuer Ergebnis "+str(i)+" startet die Simulation mit den drei Stroemen "+str(currents[1])+", "+str(currents[1]+currents[2])+" und "+ str(currents[1]+currents[2]*2)+"."
            #Aufruf der Simulation:
            if BS == 1:
                subprocess.check_call(['./neuroConstruct_1.6.0/nC.sh', 
                            '-python', 
                            './GenAlg/Auswertung/MultiCurrent.py'])
            else:
                uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Auswertung\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" # muss im Pfad liegen, sonst explizit mit angeben 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) )
                # warten auf die Simulation:
                p.wait()
                sleep(20)
        else:
            pass
        pen = 0
        if mode == 1:
            apw_list = []
            ai_list = []
            slope_list = []
            
            print "Das Ergebnis wird analysiert."
            ausgabe = analysis.analyze_Nonburst()
            
            max_gens = 40
            num_gens = 39
            m_apw = ausgabe['mean_apw']; s = ausgabe['slope']; a = ausgabe['ai']
            #fourier = ausgabe['Fourier']
            if modus == 1:  
            #############
            # general mean values:
            # from 'Electrophysical Classes of Cat Primary Visual Cortical Neurosns In Vivo as Revealed by Quantitative Analyses' 
            # by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
            #############
                apw_RS = 0.61
                slope_RS = 135
                ai_RS = 56.4    
                
                apw_min = 0.39
                apw_max = 0.83  
                ai_min = 43.2
                ai_max = 69.6
                slope_min = 68
                slope_max = 202
                
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
                    
                #for m in fourier:  
                #   if m > 4:
                #       pen =-10000
                #       print "Fourier-Penalty: -10000"
                #       break
            else:#mode = 2
            #############
            # general mean values:
            # from 'Electrophysical Classes of Cat Primary Visual Cortical Neurosns In Vivo as Revealed by Quantitative Analyses' 
            # by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
            #############
                apw_FS = 0.28
                slope_FS = 351
                ai_FS = 9.1
                
                apw_min = 0.2
                apw_max = 0.36  
                ai_min = -5.2
                ai_max = 23.4
                slope_min = 194
                slope_max = 508

                ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
                if ausgabe['mean_apw'] == -1:
                    apw = -1000*(max_gens - num_gens)/max_gens
                    print "Fehler in apw-Berechnung"
                else:
                    if m_apw< apw_max and m_apw > apw_min:  p = 0
                    else:                   p = -100    

                    if (m_apw-apw_FS) <=  0:    apw = (m_apw-apw_FS)*100/(apw_FS - apw_min)+p
                    else:                   apw = (m_apw-apw_FS)*(-100)/(apw_FS - apw_min)+p
                    
                if ausgabe['slope'] < 0:
                    slope = -1000*(max_gens - num_gens)/float(max_gens)
                else:
                    if s< slope_max and s > slope_min:  p = 0
                    else:                   p = -100    

                    if s-slope_FS <= 0: slope = (s-slope_FS)*100/(slope_FS - slope_min)+p
                    else:                   slope = (s-slope_FS)*(-100)/(slope_FS - slope_min)+p


                if a == -1:
                    ai = PaiFS*(max_gens - num_gens)/max_gens
                else:       
                    if a< ai_max and a > ai_min:    p = 0
                    else:               p = -100         

                    if (a-ai_FS) <= 0 : ai = (a-ai_FS)*100/(ai_FS - ai_min)+p
                    else:               ai = (a-ai_FS)*(-100)/(ai_FS - ai_min)+p
            print "--------------------"
            print "--------------------"
            #print "Fourier:", fourier
            print "apw: ", apw
            print "ai: ", ai
            print "slope: ", slope
            print "__________"
            fitness = 1*apw + 1*slope + 1*ai
            print "Fitness: ", fitness+pen
            print "__________"
            
            apw_list.append(apw)
            ai_list.append(ai)
            slope_list.append(slope)
        else: 
            apw_list = []
            ibf_list = []
            ir_list = []
            
            ausgabe = analysis.analyze_Burst()
            m_apw = ausgabe['mean_apw']; m_ibf = ausgabe['mean_ibf']; m_ir = ausgabe['mean_ir']
            fourier = ausgabe['Fourier']
            if modus == 3:

            #############
            # general mean values:
            # from 'Electrophysical Classes of Cat Primary Visual Cortical Neurosns In Vivo as Revealed by Quantitative Analyses' 
            # by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
            #############
                apw_IB = 0.6
                ibf_IB = 281
                ir_IB = 76.3    
                
                apw_min = 0.45
                apw_max = 0.75
                ibf_min = 225
                ibf_max = 337
                ir_min = 63.4
                ir_max = 89.2
                
                max_gens = 60
                num_gens = 30
            ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
                if m_apw == -1:
                    apw = -1000*(max_gens - num_gens)/float(max_gens)
                    print "Fehler in apw-Berechnung"
                else:
                    if m_apw< apw_max and m_apw > apw_min:  p = 0
                    else:                   p = -100    

                    if (m_apw-apw_IB) <=  0:apw = (m_apw-apw_IB)*100/(apw_IB - apw_min)+p
                    else:           apw = (m_apw-apw_IB)*(-100)/(apw_IB - apw_min)+p
                    
                
                if m_ibf == -1 and m_ir == -1:
                    print "keine Bursts:"
                    ibf = PibfIB + PirIB*(max_gens - num_gens)/max_gens
                    ir = 0
                elif m_ibf == -1:
                    ibf = PibfIB*(max_gens - num_gens)/max_gens
                    
                    #ir:

                    if m_ir < ir_max and m_ir > ir_min:     p = 0
                    else:                   p = -100    
            
                    if (m_ir-ir_IB) <= 0 :  ir = (m_ir-ir_IB)*100/(ir_IB - ir_min)+p
                    else:           ir = (m_ir-ir_IB)*(-100)/(ir_IB - ir_min)+p
                elif m_ir == -1:
                    ir = PirIB*(max_gens - num_gens)/max_gens
                    
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

            else: # modus = 4

            #############
            # general mean values:
            # from 'Electrophysical Classes of Cat Primary Visual Cortical Neurosns In Vivo as Revealed by Quantitative Analyses' 
            # by Nowak, Azouz, Sanchez-Vives, Gray, McCormick (Sept 2002)
            #############
                apw_CH = 0.31
                ibf_CH = 495    
                ir_CH = 53.9
                
                apw_min = 0.21
                apw_max = 0.41
                ibf_min = 410
                ibf_max = 580
                ir_min = 49
                ir_max = 58.8
                
            ### Normierung: Maximum: x = 0, Abweichungen im Rahmen von min/max: -100 <= x <= 0, Abweichungen außerhalb von min/max: x < -100
                if m_apw == -1:
                    apw = -1000*(max_gens - num_gens)/max_gens
                    print "Fehler in apw-Berechnung"
                else:
                    if m_apw < apw_max and m_apw > apw_min: p = 0
                    else:                   p = -100    

                    if (m_apw-apw_CH) <=  0:apw = (m_apw-apw_CH)*100/(apw_CH - apw_min)+p
                    else:           apw = (m_apw-apw_CH)*(-100)/(apw_CH - apw_min)+p


                if m_ibf == -1 and m_ir == -1:
                    print "keine Bursts:"
                    ibf = PibfCH+PirCH*(max_gens - num_gens)/max_gens
                    ir = 0
                elif m_ibf == -1:
                    ibf = PibfCH*(max_gens - num_gens)/max_gens
                    
                    #ir:
                    if m_ir < ir_max and m_ir > ir_min:     p = 0
                    else:                   p = -100    
            
                    if (m_ir-ir_CH) <= 0 :  ir = (m_ir-ir_CH)*100/(ir_CH - ir_min)+p
                    else:           ir = (m_ir-ir_CH)*(-100)/(ir_CH - ir_min)+p
                elif m_ir == -1:
                    ir = PirCH*(max_gens - num_gens)/max_gens
                    
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
                print "--------------------"
                print "--------------------"
                print "Fourier:", fourier
            print "----------"
            print "Bewertungen:"
            print "apw: ", apw
            print "ibf: ", ibf
            print "ir: ", ir
            fitness = 1*apw + 1*ibf+ 1*ir 
            print "Fitness: ", fitness
            apw_list.append(apw)
            ibf_list.append(ibf)
            ir_list.append(ir)
