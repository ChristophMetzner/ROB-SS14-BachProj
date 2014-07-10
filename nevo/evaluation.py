#fou coding=utf-8
"""Evaluate one neuron in detail using a finished simulation result.

The process consists of simulating the selected neuron,
then analyse and evaluate it. Plotting the resulst is also possible."""

import numpy
import subprocess
import glob
import shutil
from time import time, sleep, strftime

from nevo.eval import analysis
from nevo.util import projconf

EVAL_PREFIX = "eval_"

def evaluate(logger, pconf, candidates, cleanup = True):
    """Returns a list containing the neuron itself and its evaluation results."""
    pconf.invoke_neurosim(logger, type = "current", candidates = candidates, prefix = EVAL_PREFIX)
    try:
        for i in range(len(candidates)):
            offset = i * int(pconf.get_list("currents", "Simulation")[0])
            evaluate_neuron(logger, pconf, prefix = EVAL_PREFIX, offset = offset)
            pass
    finally:
        if cleanup:
            string = projconf.norm_path(pconf.get_sim_project_path(), "simulations", EVAL_PREFIX + "*")
            dirs = glob.glob(string)
            for dir in dirs:
                shutil.rmtree(dir)
#-----------------------------------------------------------
def evaluate_neuron(logger, pconf, prefix, offset):
    PaiRS = pconf.get_float("penalty_ai_RS", "fitness.evaluate_param")
    PaiFS = pconf.get_float("penalty_ai_FS", "fitness.evaluate_param")
    PibfIB = pconf.get_float("penalty_ibf_IB", "fitness.evaluate_param")
    PibfCH = pconf.get_float("penalty_ibf_CH", "fitness.evaluate_param")
    PirIB = pconf.get_float("penalty_ir_IB", "fitness.evaluate_param")
    PirCH = pconf.get_float("penalty_ir_CH", "fitness.evaluate_param")
    penalty = 0
    currents = pconf.get_list("currents", "Simulation")
    currents = [int(currents[0]), float(currents[1]), float(currents[2])]
    mode = pconf.get("mode", "Simulation")
    ana = analysis.Analysis(pconf)
    if mode == "RS" or mode == "FS":
        apw_list = []
        ai_list = []
        slope_list = []
        
        logger.info("Das Ergebnis wird analysiert.")
        ausgabe = ana.analyze_Nonburst(prefix = EVAL_PREFIX, offset = offset)
        
        max_gens = 40
        num_gens = 39
        m_apw = ausgabe['mean_apw']; s = ausgabe['slope']; a = ausgabe['ai']
        #fourier = ausgabe['Fourier']
        if mode == "RS":  
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
                logger.info("Fehler in apw-Berechnung")
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
            #       penalty =-10000
            #       logger.info("Fourier-Penalty: -10000")
            #       break
        else: # mode == "FS"
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
                logger.info("Fehler in apw-Berechnung")
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
        logger.info("--------------------")
        logger.info("--------------------")
        #logger.info("Fourier:" + repr(fourier))
        logger.info("apw: " + repr(apw))
        logger.info("ai: " + repr(ai))
        logger.info("slope: " + repr(slope))
        logger.info("__________")
        fitness = 1*apw + 1*slope + 1*ai
        logger.info("Fitness: " + repr(fitness+penalty))
        logger.info("__________")
        
        apw_list.append(apw)
        ai_list.append(ai)
        slope_list.append(slope)
    else: 
        apw_list = []
        ibf_list = []
        ir_list = []
        
        ausgabe = ana.analyze_Burst(prefix = EVAL_PREFIX, offset = currents[0] * i)
        m_apw = ausgabe['mean_apw']; m_ibf = ausgabe['mean_ibf']; m_ir = ausgabe['mean_ir']
        fourier = ausgabe['Fourier']
        if mode == "IB":

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
                logger.info("Fehler in apw-Berechnung")
            else:
                if m_apw< apw_max and m_apw > apw_min:  p = 0
                else:                   p = -100    

                if (m_apw-apw_IB) <=  0:apw = (m_apw-apw_IB)*100/(apw_IB - apw_min)+p
                else:           apw = (m_apw-apw_IB)*(-100)/(apw_IB - apw_min)+p
                
            
            if m_ibf == -1 and m_ir == -1:
                logger.info("keine Bursts:")
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

        else: # mode == "CH"

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
                logger.info("Fehler in apw-Berechnung")
            else:
                if m_apw < apw_max and m_apw > apw_min: p = 0
                else:                   p = -100    

                if (m_apw-apw_CH) <=  0:apw = (m_apw-apw_CH)*100/(apw_CH - apw_min)+p
                else:           apw = (m_apw-apw_CH)*(-100)/(apw_CH - apw_min)+p


            if m_ibf == -1 and m_ir == -1:
                logger.info("keine Bursts:")
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
            logger.info("--------------------")
            logger.info("--------------------")
            logger.info("Fourier:", fourier)
        logger.info("----------")
        logger.info("Bewertungen:")
        logger.info("apw: " + repr(apw))
        logger.info("ibf: " + repr(ibf))
        logger.info("ir: " + repr(ir))
        fitness = 1*apw + 1*ibf+ 1*ir
        logger.info("Fitness: " + repr(fitness))
        apw_list.append(apw)
        ibf_list.append(ibf)
        ir_list.append(ir)
