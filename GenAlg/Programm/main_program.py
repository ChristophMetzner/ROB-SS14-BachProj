#! usr/local/lib/python2.7 python
# coding=utf-8

import os
import errno
import numpy
import subprocess
from random import Random
from time import time, sleep, strftime
import inspyred
import itertools
import copy


# verwendete eigene Module
import HartigansDipDemo
from dipTestInst import dipTest
import analysis


"""
 Diese Datei führt eine Evolutionary Computation zur Optimierung von Leitfähigkeiten von Neuronen aus.
 Dabei muss immer angegeben werden, welche Art von Neuronen gewünscht ist.
 Unterteilt werden diese Klassen in Modi ('modus') chattering(4), intrinsic bursting(3), regular (1) und fast spiking (2).
"""

#################### EINGABEN: ##########################
def start(proj_name         = None, 
        proj_path           = None, 
        sim_config          = None, 
        stimulation         = None, 
        cell                = None, 
        duration            = None, 
        dt                  = None, 
        currents            = None, #list [num, start, step]
    # for GA
        pop_size            = None, 
        max_generations     = None, 
        mode                = None,
        crossover_rate      = None,
        mutation_strength   = None,
        mutation_rate       = None,
        num_selected        = None,
        num_co_points       = None,
        num_elites          = None,
        tournament_size     = None,
        thrFourier          = None,
        weights             = None, #List [apw, ibf, ir, ai, slope]
        penalty_ai_RS       = None,
        penalty_ai_FS       = None,
        penalty_ibf_IB      = None,
        penalty_ibf_CH      = None,
        penalty_ir_IB       = None,
        penalty_ir_CH       = None, 
        penFourier          = None,
        custom              = None,
        BS                  = None,
        anhang              = None,
        show                = None):

    #Defaults:
    if BS is None: BS = 1 #1:linux, 2:windows   
    if proj_name is None:            proj_name = "Pyr_RS"
    
    if BS == 1:
        if proj_path is None:        proj_path = proj_name+"/"+proj_name+".ncx"
    else:
        if proj_name is "Pyr_RS":
            if proj_path is None:    proj_path = "C:\Python27\Pyr_RS\Pyr_RS.ncx"
        else:
            if proj_path is None:    proj_path = "C:\Python27\Pyr_IB\Pyr_IB.ncx"
            
    if sim_config is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": sim_config = "Default Simulation Configuration"
        else: print "proj_name not known: Be sure, that you chose the right Simulation Configuration!"
        
    if stimulation is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": stimulation = "Input_0"
        else: print "proj_name not known: Be sure, that you chose the right Stimulation!"
        
    if cell is None:
        if proj_name is "Pyr_RS" or proj_name is "Pyr_IB": cell = "L5TuftedPyrRS"
        else: print "proj_name not known: Be sure, that you chose the right Cell!"
        
    if duration is None:              duration = 500
    if dt is None:                    dt = 0.05
    if currents is None:              currents = [3,0.2,0.3]
    if custom is None:                custom = 0
    if anhang is None:                anhang = " "
    
    if pop_size is None:              pop_size = 50
    if max_generations is None:       max_generations = 30
    
    if mode is None:
        if proj_name is "Pyr_RS":     mode = 1
        elif proj_name is "Pyr_IB":   mode = 3
        else: print "proj_name not known: Be sure, that you chose the right mode!"
        
    if crossover_rate is None:        crossover_rate = 1
    if thrFourier is None:            thrFourier = 5
    if mutation_strength is None:     mutation_strength = 0.4
    if mutation_rate is None:         mutation_rate = 1/12.0
    if num_selected is None:          num_selected = pop_size
    if num_co_points is None:         num_co_points = 1
    if num_elites is None:            num_elites = 1
    if tournament_size is None:       tournament_size = 2
    if weights is None:               weights = [1,1,1,1,1]      #[apw, ibf, ir, ai, slope]
    if penalty_ai_RS is None:         penalty_ai_RS = -3500
    if penalty_ai_FS is None:         penalty_ai_FS = -3500
    if penalty_ibf_IB is None:        penalty_ibf_IB = -2500
    if penalty_ibf_CH is None:        penalty_ibf_CH = -3500
    if penalty_ir_IB is None:         penalty_ir_IB = -3500
    if penalty_ir_CH is None:         penalty_ir_CH = -2500
    if penFourier is None:            penFourier = -10000

    if show is None:                  show = 1
    ###############################
    
    
    # Speichern der Konfiguraton für die Simulation in "Config.txt":
    if BS == 1:
        filename = "./GenAlg/Programm/Speicher/Config.txt"; 
    else:
        filename = "C:\Python27\GenAlg\Programm\Config.txt"
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    config = open(filename, "w")
    config.write(str(proj_name)+"\n"+str(proj_path)+"\n"
                    +str(sim_config)+"\n"
                    +str(stimulation)+"\n"
                    +str(cell)+"\n"
                    +str(duration)+"\n"
                    +str(dt)+"\n"
                    +str(currents)+"\n"
                    +str(mode))
    config.close()  
    ###############################
    
    
    # Leeren der Dateien, da spaeter die Werte >angehaengt< werden:
    if BS == 1:
        channel = open("./GenAlg/Programm/Speicher/channel.txt","w")
        location = open("./GenAlg/Programm/Speicher/location.txt","w")
        density = open("./GenAlg/Programm/Speicher/density.txt","w")
    else:
        channel = open("C:\Python27\GenAlg\Programm\Analyse\channel.txt","w") 
        location = open("C:\Python27\GenAlg\Programm\Analyse\location.txt","w")
        density = open("C:\Python27\GenAlg\Programm\Analyse\density.txt","w")
    channel.close(); location.close(); density.close()
    ###############################
    
    
    # Aufruf des Evolutionären Algorithmus:
    main(   pop_size, 
            max_generations, 
            mode, 
            crossover_rate,
            mutation_strength,
            mutation_rate,
            num_selected,
            num_co_points,
            num_elites,
            tournament_size,
            weights,
            thrFourier,
            penFourier,
            penalty_ai_RS,
            penalty_ai_FS,
            penalty_ibf_IB,
            penalty_ibf_CH,
            penalty_ir_IB,
            penalty_ir_CH, 
            currents,
            custom,
            BS,
            show,
            anhang)
#endDEF








"""
######################################## GENERATE_CONDUCTANCE #######################################################
Instanzen bilden:
verschiedene Ionenkanäle mit unterschiedlichen Leitfähigkeiten
"""
def generate_conductance(random, args):

    chromosome = []
### klassenspezifische Kanaele:
    if args.get('modus')==2 or args.get('modus')==1:

        if args.get('modus')==1:  # RS
            chromosome = [10**int(random.uniform(-11, -9)), #ar
                       10**int(random.uniform(-11, -9)), #cal
                       10**int(random.uniform(-11, -8)), #cat
                       10**int(random.uniform(-11, -7)), #k2
                       10**int(random.uniform(-11, -7)), #ka
                       10**int(random.uniform(-11, -7)), #kahp
                       10**int(random.uniform(-11, -7)), #kc 
                       10**int(random.uniform(-5, -3)),  #kdr  AP
                       10**int(random.uniform(-8, -5)),  #km
                       10**int(random.uniform(-5, -3)),  #naf  AP
                       10**int(random.uniform(-11, -7)), #nap
                       10**int(random.uniform(-12, -7))  #pas
                    ]
        else: # modus = 2: FS
            chromosome = [10**int(random.uniform(-11, -9)), #ar
                       10**int(random.uniform(-11, -9)), #cal
                       10**int(random.uniform(-11, -8)), #cat
                       10**int(random.uniform(-11, -7)), #k2
                       10**int(random.uniform(-11, -7)), #ka
                       10**int(random.uniform(-11, -10)), #kahp Adaption
                       10**int(random.uniform(-11, -7)), #kc
                       10**int(random.uniform(-5, -3)),  #kdr   AP
                       10**int(random.uniform(-8, -7)),  #km    Adaption
                       10**int(random.uniform(-5, -3)),  #naf   AP
                       10**int(random.uniform(-11, -7)), #nap
                       10**int(random.uniform(-12, -7))  #pas
                    ]

                    
        # Ort und Name für Simulation in Textdateien schreiben 
        if args.get('BS') == 1:
            channel = open("./GenAlg/Programm/Speicher/channel.txt","a")
            location = open("./GenAlg/Programm/Speicher/location.txt","a")
        else:
            channel = open("C:\Python27\GenAlg\Programm\Analyse\channel.txt","a") 
            location = open("C:\Python27\GenAlg\Programm\Analyse\location.txt","a")

        location.write('soma_dendrite\nsoma2\ndendrite_group\n'+ #ar
                'soma2\ndendrite_group\n'+ #cal
                'soma2\ndendrite_group\n'+ #cat
                'dendrite_group\nsoma_group\n'+ #k2
                'dendrite_group\nsoma2\naxon_group\n'+ #ka
                'soma2\ndendrite_group\n'+ #kahp
                'dendrite_group\nsoma2\n'+ #kc
                'dendrite_group\nsoma2\naxon_group\n'+ #kdr
                'axon_group\ndendrite_group\nsoma2\n'+ #km
                'all\ndendrite_group\nsoma2\naxon_group\n'+ #naf
                'dendrite_group\nsoma2\n'+ #nap
                'all\naxon_group\nsoma2\ndendrite_group\n') #pas
                        
        channel.write('ar\nar\nar\n'+ #5
                'cal\ncal\n'+ #6
                'cat\ncat\n'+ #3
                'k2\nk2\n'+ #4
                'ka\nka\nka\n'+ #5
                'kahp_deeppyr\nkahp_deeppyr\n'+ #3
                'kc\nkc\n'+ #5
                'kdr\nkdr\nkdr\n'+ #5
                'km\nkm\nkm\n'+ #5
                'naf\nnaf\nnaf\nnaf\n'+ #8
                'nap\nnap\n'+#6
                'pas\npas\npas\npas\n') #5
        location.write('#\n '); channel.write('#\n ')
        location.close(); channel.close()


    else: #Bursting
    
        if args.get('modus')==4: # CH
            chromosome = [10**int(random.uniform(-11, -8)), #ar
                   10**int(random.uniform(-13, -9)), #cal
                   10**int(random.uniform(-11, -6)), #cat
                   10**int(random.uniform(-11, -6)), #k2
                   10**int(random.uniform(-11, -5)), #kaib
                   10**int(random.uniform(-11, -7)), #kahp
                   10**int(random.uniform(-11, -6)), #kc
                   10**int(random.uniform(-3, -2)),  #kdr
                   10**int(random.uniform(-10, -7)),  #km
                   10**int(random.uniform(-4, -2)),  #naf
                   10**int(random.uniform(-11, -7)), #nap
                   10**int(random.uniform(-12, -6))  #pas
                    ]
        else: # modus = 3: IB
            chromosome = [10**int(random.uniform(-11, -8)), #ar
                   10**int(random.uniform(-13, -9)), #cal
                   10**int(random.uniform(-11, -6)), #cat
                   10**int(random.uniform(-11, -6)), #k2
                   10**int(random.uniform(-11, -5)), #kaib
                   10**int(random.uniform(-11, -7)), #kahp
                   10**int(random.uniform(-11, -6)), #kc
                   10**int(random.uniform(-3, -2)),  #kdr
                   10**int(random.uniform(-10, -7)),  #km
                   10**int(random.uniform(-4, -2)),  #naf
                   10**int(random.uniform(-11, -7)), #nap
                   10**int(random.uniform(-12, -6))  #pas
                    ]
                    
        # Ort und Name fuer Simulation in Textdateien schreiben         
        if args.get('BS') == 1:     
            channel = open("./GenAlg/Programm/Speicher/channel.txt","a")
            location = open("./GenAlg/Programm/Speicher/location.txt","a")
        else:
            channel = open("C:\Python27\GenAlg\Programm\Analyse\channel.txt","a") 
            location = open("C:\Python27\GenAlg\Programm\Analyse\location.txt","a")
        
        location.write('soma_dendrite\nsoma2\ndendrite_group\n'+ #ar
                'dendrite_group\nsoma2\n'+ #cal
                'soma2\ndendrite_group\n'+ #cat
                'dendrite_group\nsoma_group\n'+ #k2
                'soma_group\ndendrite_group\naxon_group\n'+ #kaib
                'soma2\ndendrite_group\n'+ #kahp
                'dendrite_group\nsoma2\n'+ #kc
                'dendrite_group\nsoma2\naxon_group\n'+ #kdr
                'dendrite_group\nsoma2\naxon_group\n'+ #km
                'all\ndendrite_group\nsoma2\naxon_group\n'+ #naf

                'dendrite_group\nsoma2\n'+ #nap
                'all\naxon_group\nsoma2\ndendrite_group\n') #pas
                        
        channel.write('ar\nar\nar\n'+ #5
                'cal\ncal\n'+ #6
                'cat\ncat\n'+ #3
                'k2\nk2\n'+ #4
                'ka_ib\nka_ib\nka_ib\n'+ #3
                'kahp_deeppyr\nkahp_deeppyr\n'+ #3
                'kc\nkc\n'+ #5
                'kdr\nkdr\nkdr\n'+ #5
                'km\nkm\nkm\n'+ #5
                'naf\nnaf\nnaf\nnaf\n'+ #8
                'nap\nnap\n'+ #6
                'pas\npas\npas\npas\n') #5
        location.write('#\n '); channel.write('#\n ')
        location.close(); channel.close()

    return chromosome
#endDEF





"""
Berechnen der Leitfähigkeiten aus den oben randomisiert bestimmten Zehnerpotenzen und den exakten Werten der Ionenkanäle
"""
def calc_dens(chromosome,finish,args):
    # chromosome = [ar, cal, cat, k2, ka,(kaib), kahp, kc, kdr, km, naf, nap, pas]
    list = []
    
    if args.get('modus') == 1 or args.get('modus') == 2: # RS, FS
        ar = [-1.0, 1.0, 2.0] 
        for v in ar:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[0])
        cal = [1.6, 0.32] 
        for v in cal:
            list.append(v*chromosome[1])
        cat = [1.0, 2.0]
        for v in cat:
            list.append(v*chromosome[2])
        k2 = [1.0,0.5] 
        for v in k2:
            list.append(v*chromosome[3])
        ka = [1.6, 2.0, 0.06] 
        for v in ka:
            list.append(v*chromosome[4])
        kahp = [2.0, 4.0]
        for v in kahp:
            list.append(v*chromosome[5])
        kc = [1.2, 2.88] 
        for v in kc:
            list.append(v*chromosome[6])
        kdr = [1.5, 1.7, 4.5]
        for v in kdr:
            list.append(v*chromosome[7])
        km = [ 3.0, 0.75, 0.85] 
        for v in km:
            list.append(v*chromosome[8])
        naf = [ -1.0, 1.875, 2.0, 4.5] 
        for v in naf:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[9])
        nap = [ 1.0, 1.6] 
        for v in nap:
            list.append(v*chromosome[10])
        pas = [-1.0, 1.0, 0.02, 0.3] 
        for v in pas:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[11])
                
    else: # IB, CH
        ar = [-1.0, 1.0, 2.0] 
        for v in ar:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[0])
        cal = [6.0, 6.0] 
        for v in cal:
            list.append(v*chromosome[1])
        cat = [1.0, 2.0]
        for v in cat:
            list.append(v*chromosome[2])
        k2 = [1.0, 0.5] 
        for v in k2:
            list.append(v*chromosome[3])
        kaib = [ 2.0, 1.6, 0.06] 
        for v in kaib:
            list.append(v*chromosome[4])
        kahp = [2.0, 4.0]
        for v in kahp:
            list.append(v*chromosome[5])
        kc = [ 0.3,0.72] 
        for v in kc:
            list.append(v*chromosome[6])
        kdr = [ 1.7, 1.7, 4.5] 
        for v in kdr:
            list.append(v*chromosome[7])
        km = [ 3.0, 3.4, 6.0]
        for v in km:
            list.append(v*chromosome[8])
        naf = [-1.0, 2.0, 2.0, 4.5] 
        for v in naf:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[9])
        nap = [ 4.0, 6.4] 
        for v in nap:
            list.append(v*chromosome[10])
        pas = [-1.0, 1.0, 0.02, 0.3] 
        for v in pas:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*chromosome[11])
                
                
    # Speichern der Werte in einer Textdatei, ebenfalls fuer die Simulation         
    if args.get('BS') == 1:
        density = open("./GenAlg/Programm/Speicher/density.txt","a")
    else:
        density = open("C:\Python27\GenAlg\Programm\Analyse\density.txt","a")
    string = ''
    for e in list:
        string += str(e)+'\n'
        #print e
    density.write(string+'#\n ')
    density.close()
    
#endDEF
    






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
        calc_dens(chromosome,0, args) 

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
        sleep(10) #damit er fertig läuft
    else:
        uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Programm\MultiConductance.py"'] # muessen alles Strings sein 
        externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
        p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) )
        p.wait()
        sleep(50) #damit er fertig läuft




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
                sleep(14) 
            else:
                uebergabeWerte = ["-python", '"C:\Python27\GenAlg\Programm\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) ); p.wait()
                sleep(20) #damit er fertig läuft

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
                sleep(20) #damit er fertig läuft
            else:
                uebergabeWerte = [  "-python", 
                            '"C:\Python27\GenAlg\Programm\MultiCurrent.py"'] # muessen alles Strings sein 
                externesProgramm = "C:\Users\Anne\Downloads\Programme\NeuroConstruct_1.6.0\NeuroConstruct_1.6.0\NC.bat" 
                p = subprocess.Popen( externesProgramm + " " + " ".join(uebergabeWerte) ); p.wait() 
                sleep(20) #damit er fertig läuft

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
            reason.appemd("Fiel die ganze Zeit ???")
            M.append(0)
    return{'P':Fpenalty, 'R':reason, 'M':M}
#DEFend


        
###################################### MUTATE_COND #####################################################
""" Mutation der Leitfähigkeiten   
#   damit die Verhältnisse in den einzenlen Kanälen erhalten bleiben:
#       es muss gelten : 
#                       x1/x2 = (x1+k1)/(x2+k2)
#       also:(wenn x1, x2 und k1 geben)
#                          k2 = x2/x1*k1
#       oder allgemein:
#                          ki = xi/x1*k1
#   mit k1 := add,  x1:=inst[start], xi:=inst[j],   
#
#def mutate_cond(random, candidates, args):
#   if args.get('show') == 1:
#       print "================================="
#       print strftime("%d.%m.%Y %H:%M:%S")+": there are "+str(len(candidates))+" individuals for mutation"
#       print strftime("%d.%m.%Y %H:%M:%S")+": there are "+str(len(candidates)/2)+" pairs for crossover"
#       #print "================================="
#
#   mutants = []
#   for inst in candidates:
#       for chan in inst:
#           chan.mutate()
#       mutants.append(inst)
#   return mutants
#endDEF 
"""



###################################### MUTATE_UNIFORM #####################################################
# 1:1 "abgeschrieben" von der inspyred-Funktion, Sie hat beim regulären Aufruf nicht funktioniert
def nuMutation(random, candidate, args):

    
        
    l_bound = args.get('lower_bound')
    u_bound = args.get('upper_bound')
    num_gens = args['_ec'].num_generations
    max_gens = args.get('max_generations')
    strength = args.get('mutation_strength')
    exponent = (1.0-num_gens/float(max_gens))**strength
    mutant = copy.copy(candidate)
    for i, (c,lo,hi) in enumerate(zip(candidate, l_bound, u_bound)):
        #if random.random() < args.get('mutation_rate'):
        if random.random() <= 0.5:
            new_value = c+(hi-c)*(1.0-random.random()**exponent)
        else:
            new_value = c-(c-lo)*(1.0-random.random()**exponent)
        mutant[i] = new_value

    return mutant
#endDEF




#################################### CROSS #########################################################
""" crossover soll verschiedene Kanäle austauschen je nach crossover_rate und num_allel
#def cross(random, mom, dad, args):
#   #if args.get('show') == 1:
#       #print "================================="
#       #print strftime("%Y.%m.%d %H:%M:%S")+": crossing over"
#       #print "================================="
#
#   os1 = mom
#   os2 = dad
#   randL = int(random.uniform(0, len(mom)-args.get('num_allel')+1))
#   for i in range(args.get('num_allel')):
#       os1[randL+i] = dad[randL+i]
#       os2[randL+i] = mom[randL+i]
#   return [os1, os2]
#endDEF 
""" 




####################################### MAIN #########################################################
"""
In der Main wird der Genetische Algorithmus aufgerufen und gestartet. Mit den Eingabeparametern, die am Anfang übergeben wurden, werden nun die nötigen Einstellungen vorgenommen.
Die Module für generation, variator(mutation, crossover),selection, observer und replacement werden hier initialisiert und aufgerufen.
Zum Schluss wird die finale Population und deren Eigenschaften bzw. die EIngabeparameter ausgegeben und gespeichert.
"""
# Beginn der Main:
def main(   population, 
        generations, 
        mode, 
        crossover, 
        mutation,
        mut_rate,
        selected,
        points,
        elite,
        tsize,
        weights,
        thrF,
        penF,
        penalty_ai_RS,
        penalty_ai_FS,
        penalty_ibf_IB,
        penalty_ibf_CH,
        penalty_ir_IB,
        penalty_ir_CH, 
        Currents,
        custom,
        BetrSys,
        doc,
        anhang):
    #print Currents
    rand = Random()
    rand.seed(int(time()))
    
    t = strftime("%d.%m.%Y-%H:%M:%S")   

    EC = inspyred.ec.EvolutionaryComputation(rand)
    #EC.analysis = inspyred.ec.analysis.generation_plot

    
    # Variator: braucht 'crossover_rate', 'num_crossover_points'; 'mutation_strength'
    EC.variator = [inspyred.ec.variators.n_point_crossover, inspyred.ec.variators.mutator(nuMutation)]

    if mode == 1:
    #           ar  cal cat k2  ka  kahp    kc  kdr km  naf nap pas
        u_bound = [10**-7,  10**-7, 10**-6, 10**-5, 10**-5, 10**-5, 10**-5, 10**-3, 10**-4, 10**-3, 10**-5, 10**-5]
        l_bound = [10**-14, 10**-14,10**-14,10**-14,10**-14,10**-14,10**-14,10**-5, 10**-11,10**-5, 10**-14,10**-15]
    elif mode == 2:
    #           ar  cal cat k2  ka  kahp    kc  kdr km  naf nap pas
        u_bound = [10**-7,  10**-7, 10**-6, 10**-5, 10**-5, 10**-9, 10**-5, 10**-3, 10**-6, 10**-3, 10**-5, 10**-5]
        l_bound = [10**-14, 10**-14,10**-14,10**-14,10**-14,10**-11,10**-14,10**-5, 10**-8,10**-5,  10**-14,10**-15]
    elif mode == 4:
        #       ar  cal cat k2  ka_ib   kahp    kc  kdr km  naf nap pas
        u_bound = [10**-7,  10**-9, 10**-7, 10**-5, 10**-5, 10**-5, 10**-5, 10**-3, 10**-7, 10**-3, 10**-5, 10**-5]
        l_bound = [10**-14, 10**-12,10**-12,10**-12,10**-12,10**-12,10**-12,10**-4, 10**-11,10**-5, 10**-12,10**-13]
    else:
        #       ar  cal cat k2  ka_ib   kahp    kc  kdr km  naf nap pas
        u_bound = [10**-7,  10**-9, 10**-7, 10**-5, 10**-5, 10**-5, 10**-5, 10**-3, 10**-7, 10**-3, 10**-5, 10**-5]
        l_bound = [10**-14, 10**-12,10**-12,10**-12,10**-12,10**-12,10**-12,10**-4, 10**-11,10**-5, 10**-12,10**-13]

    # braucht statistics_file und individuals_file für analysis
    EC.observer = inspyred.ec.observers.file_observer
    if custom == 1:
        if mode == 1 or mode == 2:
            EC.selector = inspyred.ec.selectors.tournament_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement # erstellt neue Generation
            anhang = anhang+"tournament_selection und truncation_replacement"
        else:
            EC.selector = inspyred.ec.selectors.truncation_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement
            anhang = anhang+"truncation_selection und truncation_replacement"

    else:
        if mode == 1 or mode == 2:
            EC.selector = inspyred.ec.selectors.tournament_selection #truncation_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.random_replacement #truncation_replacement#random_replacement# # erstellt neue Generation
            anhang = anhang+"tournament_selection und random_replacement"
        else:
            EC.selector = inspyred.ec.selectors.truncation_selection # sucht Eltern aus
            EC.replacer = inspyred.ec.replacers.truncation_replacement
            anhang = anhang+"truncation_selection und truncation_replacement"
        


    # terminator: braucht 'max_generations', 'tolerance'
    EC.terminator = inspyred.ec.terminators.generation_termination

    if BetrSys == 1:
        final_pop = EC.evolve(generator =  inspyred.ec.generators.diversify(generate_conductance),
                  evaluator =evaluate_param,
                  #statistics_file = open('./GenAlg/Programm/Speicher/inspyred-statistics-{0}.csv'.format(strftime('%m%d-%H%M')),'w'),
                  statistics_file = open('./GenAlg/Programm/Speicher/inspyred-statistics-{0}.csv'.format(strftime('%m%d-%H%M')),'w'),
                  #individuals_file = open('./GenAlg/Programm/Speicher/inspyred-individuals-{0}.csv'.format(strftime('%m%d-%H%M')),'w'),
                  individuals_file = open('./GenAlg/Programm/Speicher/inspyred-individuals-{0}.csv'.format(strftime('%m%d-%H%M')),'w'),
                  #filename = './GenAlg/Programm/Speicher/inspyred-inspyred-statistics-{0}.csv'.format(strftime('%m%d-%H%M')),
                  filename = './GenAlg/Programm/Speicher/inspyred-inspyred-statistics-{0}.csv'.format(strftime('%m%d-%H%M')),
                  errorbars = False,
                  lower_bound = l_bound,
                  upper_bound = u_bound,
                  pop_size = population,
                  max_generations = generations,
                  crossover_rate = crossover,
                  num_crossover_points = points,
                  num_selected = selected,
                  num_elites = elite,
                  tournament_size = tsize,
                  mutation_strength = mutation, # higher values correspond to greater variation
                  mutation_rate = mut_rate,
                  modus = mode, 
                  thrFourier = thrF,
                  penFourier = penF,
                  p_ai_RS = penalty_ai_RS,
                  p_ai_FS = penalty_ai_FS,
                  p_ibf_IB = penalty_ibf_IB,
                  p_ibf_CH = penalty_ibf_CH,
                  p_ir_IB = penalty_ir_IB,
                  p_ir_CH = penalty_ir_CH,
                  W_apw = weights[0],
                  W_ibf = weights[1],
                  W_ir = weights[2],
                  W_ai = weights[3],
                  W_slope = weights[4],
                  BS = BetrSys,
                  numCurrents = Currents[0],
                  show = doc)
    else:
        final_pop = EC.evolve(generator =  inspyred.ec.generators.diversify(generate_conductance),
                  evaluator =evaluate_param,
                  statistics_file = open('C:\Python27\GenAlg\plots\inspyred-statistics.csv','w'),
                  individuals_file = open('C:\Python27\GenAlg\plots\inspyred-individuals.csv','w'),
                  filename = 'C:\Python27\GenAlg\plots\inspyred-inspyred-statistics.csv',
                  errorbars = False,
                  lower_bound = l_bound,
                  upper_bound = u_bound,
                  pop_size = population,
                  max_generations = generations,
                  crossover_rate = crossover,
                  num_crossover_points = points,
                  num_selected = selected,
                  num_elites = elite,
                  tournament_size = tsize,
                  mutation_strength = mutation, # higher values correspond to greater variation
                  mutation_rate = mut_rate,
                  modus = mode, 
                  thrFourier = thrF,
                  penFourier = penF,
                  p_ai_RS = penalty_ai_RS,
                  p_ai_FS = penalty_ai_FS,
                  p_ibf_IB = penalty_ibf_IB,
                  p_ibf_CH = penalty_ibf_CH,
                  p_ir_IB = penalty_ir_IB,
                  p_ir_CH = penalty_ir_CH,
                  W_apw = weights[0],
                  W_ibf = weights[1],
                  W_ir = weights[2],
                  W_ai = weights[3],
                  W_slope = weights[4],
                  numCurrents = Currents[0],
                  BS = BetrSys,
                  show = doc)
    final_pop.sort(reverse=True)

    print strftime("%Y.%m.%d %H:%M:%S")+":\nDie Eigenschaften des besten Individuums mit Fitness "\
            +str(final_pop[0].fitness)+" koennen in ErgebnisDens.txt gefunden werden."
    if doc == 1: print "========================================="

    
    #schreibt Ergebnisse in Datei zur späteren Auswertung!
    if BetrSys == 1:
        d = open("./GenAlg/Programm/Speicher/ErgebnisDens.txt", "a")
    else:
        d = open("C:\Python27\GenAlg\Programm\Analyse\ErgebnisDens.txt", "a")

    string = "Anfang: "+t+" Ende: "+strftime("%d.%m.%Y %H:%M:%S")+": Ergebnis der EC mit: Fitness"+str(final_pop[0].fitness)+"[2. "+ str(final_pop[1].fitness)+", 3. "+str(final_pop[2].fitness)+"]"


    string = string+" modus = "+str(mode)
    string = string+"; pop_size = "+str(population)
    string = string+"; max_generations = "+str(generations)
    string = string+"; currents = "+str(Currents[0])+str(Currents[1])+str(Currents[2])
    string = string+"; crossover_rate = "+str(crossover)
    string = string+"; mutation_strength = "+str(mutation)
    string = string+"; mutation_rate = "+str(mut_rate)
    string = string+"; tournament_size = "+str(tsize)
    string = string+"; num_selected = "+str(selected)
    string = string+"; num_co_points = "+str(points)
    string = string+"; weights = "+str(weights)
    string = string+"; thrFourier = "+str(thrF)
    string = string+"; penFourier = "+str(penF) 
    string = string+"; PaiRS = "+str(penalty_ai_RS)
    string = string+"; PaiFS = "+str(penalty_ai_FS)
    string = string+"; PibfIB = "+str(penalty_ibf_IB)
    string = string+"; PibfCH = "+str(penalty_ibf_CH)
    string = string+"; PirIB = "+str(penalty_ir_IB)
    string = string+"; PirCH = "+str(penalty_ir_CH)
    string = string+"; Anhang = "+anhang
    string = string+"\n#\n"

    d.write(string)

    returnCount = min(population,10)
    
    for i in xrange(0,returnCount):
        item = final_pop[i]
        for v in item.candidate:
            d.write(str(v)+"\n")
        d.write("#\n\n")
    d.write("#####\n\n")
    d.close()

    #best = final_pop[0]
    #second = final_pop[1]
    #third = final_pop[2]
    #fourth = final_pop[3]
    #fifth = final_pop[4]
    #sixth = final_pop[5]
    #seventh = final_pop[6]
    #achter = final_pop[7]
    #neunter = final_pop[8]
    #tenth = final_pop[9]

    #for v in best.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in second.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in third.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in fourth.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in fifth.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in sixth.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in seventh.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in achter.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in neunter.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#\n\n")
    #for v in tenth.candidate:
    #    d.write(str(v)+"\n")
    #d.write("#####\n\n")
    #d.close()

#endDEF
