# coding=utf-8
import sys
import time

import math
import numpy
import scipy.optimize as optimization
import logClient

vorsprung = 0
logger = None

class Analysis(object):
    confDict = None
    proj_conf = None
    #-----------------------------------------------------------
    def __init__(self, proj_conf):
        global logger
        self.proj_conf = proj_conf
        logger = self.proj_conf.getClientLogger("analysis")
        self.confDict = self.proj_conf.parseProjectConfig()
    #-----------------------------------------------------------
    # Analysis for non-bursting neurons
    def analyze_Nonburst(self):
        currents=numpy.arange(self.confDict["startCurrent"], self.confDict["startCurrent"] + self.confDict["numCurrents"] * self.confDict["stepCurrent"], self.confDict["stepCurrent"])

        apw_array = numpy.zeros((self.confDict["numCurrents"], 1))
        freq_array = numpy.zeros((self.confDict["numCurrents"], 1))
        isi_list = []
        aps_list = []
        for j in range(self.confDict["numCurrents"]):
            filename = self.proj_conf.localPath(self.confDict["projName"], "simulations/multiCurrent_" + repr(j), "CellGroup_1_0.dat")
            check = False
            c = 0
            while not check:
                t = 0
                while not check and t < 15:
                    try:
                        opened_file = open(filename, 'r')
                        check = True
                    except:
                        logger.warning("File " + filename + " could not be opened for analysis (analyze_Nonburst).")
                        time.sleep(2)
                        t += 2
                if not check:
                    if c >= 2:
                        logger.error("Could not open " + filename + " even after restarting the simulation " + repr(c) + " times")
                        return {'P':0}
                    else:
                        c += 1
                        # Aufruf der Simulation:
                        self.proj_conf.invokeSimulation("current")
            data = []
            for line in opened_file:
                line = line.strip()
                try:
                    x=float(line)

                except:
                    pass
                data.append(x)
            opened_file.close()
            result = analyze_memtrace_NB(data[vorsprung:], self.confDict["dt"], self.confDict["duration"] - vorsprung * self.confDict["dt"])
            apw_array[j] = result['apw']    # laenge 3
            freq_array[j] = result['freq']  # laenge 3
            isi_list.append(result['isi'])  # 3xlen(isi)
            aps_list.append(result['aps'])  # 3xlen(aps)


        #####################
        # Steigung der f-I-Kurve:
        # - Steigung der Geraden: allg: delta_f = (f(x_N) - f(x_1)) / (x_N - x_1)
        # - Graph: Frequenz ist Funktion der Stromstärke:  f(I)
        # - also: delta_f = (f(I_N) - f(I_1)) / (I_N - I_1))
        #
        slope = (freq_array[-1]-freq_array[0]) / (currents[-1]-currents[0])

        ####################
        # Curve-fitting: Adaption-Index:
        #
        x0 = numpy.array([1, 1, -1])#M

        # func = a^(cx) + b:
        def func(x, a, b, c):
            return a**(c * x) + b

        ai = numpy.zeros((self.confDict["numCurrents"], 1))
        for k in range(self.confDict["numCurrents"]):

            logger.info("Strom: " + repr(currents[k]))
            logger.info("Anzahl an InterspikeIntervallen: " + repr(len(isi_list[k])))
            logger.info("Frequenz: " + repr(freq_array[k]))
            logger.info("----------------- ")

            # Frequenz: Quotient aus erstem InterspikeIntervall (ap_start(2)-ap_start(1)) und dem Zeitpunkt des Beginns der ersten Aktionspotentials
            # - also: F_1 = isi[0] / (ap_start[1] * self.confDict["dt"])
            # - und das für alle Aktionspotentiale
            if len(aps_list[k]) >= 4: #TODO: signifikant?

                #F_array= numpy.array([(isi_list[i] / (aps_list[i + 1] * self.confDict["dt"])) for i in range(len(aps_list)-1)])
                #F_array = numpy.array([1 / isi_list[k][i] for i in range(len(isi_list[k]))])
                F_array = numpy.array([1000 / isi for isi in isi_list[k]], dtype = float)#N


                if self.confDict["mode"] == "RS" or F_array[0] > 60: #and F_array[0] < 1000): # [Hz], laut Paper (bib:cat), sonst evtl nur spontane Aktivität
                    # ENTWEDER:
                    # time of spikes:
                    xdata = numpy.array([idx * self.confDict["dt"] for idx in aps_list[k][0:-1]])#N, ein aps weniger, da isi die zwischenräume zählt

                    # Curve-Fitting:
                    # abc = parameters of func
                    # cov = the estimated covariance of abc
                    try:
                        abc, cov = optimization.curve_fit(func, xdata, F_array, x0)
                        F_ad = abc[1] # = horizontal asymptote of exponential fit: adapted firing rate

                        ai1 =numpy.float( 100-(100 * F_ad / F_array[0])) #laut Paper
                    except:
                        ai[k] = -1
                        logger.info("Es konnte kein Fitting zur Exponentialkurve gefunden werden.")
                        continue

                    # ODER:
                    c = 0
                    for t in range(len(aps_list[k])):
                        if (aps_list[k][t] + vorsprung) * self.confDict["dt"] <= 100:
                            c = c + 1 #zählt die Aktionspotenziale in den ersten 100ms
                    F_ad = c / 0.1 # Feuerrate in den ersten 100ms [Hz]
                    ai2 = numpy.float(100-(100 * F_ad / F_array[0])) #laut Paper
                    if self.confDict["mode"] == "RS":
                        ai[k] = max(ai1, ai2)
                    else:
                        ai[k] = min(ai1, ai2)

                else:
                    ai[k] = -1
                    logger.info("nicht mode RS oder Frequenz zu niedrig")
                logger.info("F_1: " + repr(F_array[0]))
            else:
                ai[k] = -1
                logger.info("weniger als 4 APs")

        # Mittelwert der Adaptionsindices
        xsum = 0
        if -1 in ai:
            xsum = [x for x in ai if x != -1]
            if len(xsum) == 0:
                ai_mean = -1
            else:
                ai_mean = numpy.mean(xsum)
        else:
            ai_mean = numpy.mean(ai)

        # Mittelwert der Frequenzen:
        if len(freq_array)== 0:
            freq = 0
        else:
            freq = numpy.mean(freq_array)

        #Mittelwert der Aktionspotentialweiten:
        if len(apw_array)== 0:
            apw = -1
            sapw = -1
        else:
            apw = numpy.mean(apw_array)
            sapw = numpy.std(apw_array)

        # logarithmuische Histogrammdarstellung der ISIs:
        #logisi=numpy.log(isi_list)
        #mini = min(logisi);
        #maxi = max(logisi);
        #edges = arange(mini, maxi + ((maxi-mini) / 10), ((maxi-mini) / 10) )
        #hist, bin_edges = numpy.histogram(logisi, bins = edges)


        logger.info('apw = ' + repr(apw) + '\nslope = ' + repr(slope) + '\nai = ' + repr(ai_mean))

        del currents; del apw_array; del freq_array; del check; del data;
        del t; del result; del isi_list; del aps_list

        return {'mean_apw':apw , 'sd_apw':sapw, 'mean_freq':freq, 'slope':slope, 'ai':ai_mean, 'P':1}

    #-----------------------------------------------------------
    def analyze_Burst(self):
        """Analyzes bursting neurons."""
        apw_array = numpy.zeros((self.confDict["numCurrents"], 1))
        ibf_array = numpy.zeros((self.confDict["numCurrents"], 1))
        ir_array = numpy.zeros((self.confDict["numCurrents"], 1))

        for j in range(self.confDict["numCurrents"]):
            check = 0
            c = 0
            while check != 1:
                data = []

                # Potenzialdaten der Simulation:
                filename = self.proj_conf.localPath(self.confDict["projName"],
                                                    "simulations/multiCurrent_" + repr(j),
                                                    "CellGroup_1_0.dat")
                t = 0
                while t < 60:
                    try:
                        opened_file = open(filename, 'r')
                        t = 100
                        check = 1
                    except:
                        time.sleep(2)
                        t = t + 2
                if t == 60:
                    if c == 2:
                        logger.error("Simulation hat sich aufgehangen, Individuum wird entfernt")
                        return {'P':0}
                    c = c + 1
                    self.proj_conf.invokeSimulation("current");
            for line in opened_file:
                line = line.strip()
                try:
                    x=float(line)

                except:
                    pass
                data.append(x)
            opened_file.close()
            result = analyze_memtrace(data, self.confDict["dt"], self.confDict["duration"]-vorsprung * self.confDict["dt"])
            apw_array[j] = result['apw']
            ibf_array[j] = result['ibf']
            ir_array[j] = result['ir']
            isi_list = result['isi']

            logger.info("Strom: " + repr(self.confDict["startCurrent"] + self.confDict["stepCurrent"] * j))
            logger.info("Anzahl an InterspikeIntervallen: " + repr(len(isi_list)))
            logger.info("-----------------")

        if len(apw_array) == 0: # avoiding the division by zero error
            apw = -1
            stdapw = -1
        else:
            apw = numpy.mean(apw_array)
            stdapw = numpy.std(apw_array)

        logger.info('apw = ' + repr(apw) + '\nibf= ' + repr(numpy.mean(ibf_array)) + '\nir= ' + repr(numpy.mean(ir_array)))

        return {'mean_apw':apw , 'sd_apw':stdapw, 'mean_ibf':numpy.mean(ibf_array), 'sd_ibf':numpy.std(ibf_array), 'mean_ir':numpy.mean(ir_array), 'sd_ir':numpy.std(ir_array), 'P':1}
    #-----------------------------------------------------------
    def analyze_ISI(self, idx):
        # determining the interspike intervals (ISI)

        spiketrain = []
        filename = self.proj_conf.localPath(self.confDict["projName"], "simulations/PySim_" + repr(idx), "CellGroup_1_0.dat")
        check = 0
        z = 0
        t = 0
        while check != 1:
            if t < 15:
                try:
                    opened_file = open(filename, 'r')
                    check = 1
                except:
                    logger.warning("File " + filename + " could not be opened for analysis (analyze_ISI).")
                    time.sleep(2)
                    t = t + 2
            else:
                if z == 2:

                    logger.error("musste mehrfach von vorn anfangen zu simulieren")
                    check = 1
                    break
                z = z + 1
                self.proj_conf.invokeSimulation("conductance")
        for line in opened_file:
            line = line.strip()
            try:
                x=float(line) #so lassen!
            except:
                pass
            spiketrain.append(x) # das auch!!
        opened_file.close()
        data = spiketrain

        res = AP(data, self.confDict["duration"]-vorsprung * self.confDict["dt"], self.confDict["dt"])
        ap_start = res['aps']
        ap_end = res['ape']
        #logger.debug("aps: " + repr(ap_start))
        #logger.debug("ape: " + repr(ap_end))

        isi = []
        logisi = []
        if not len(ap_start) <= 2:
            for i in range(0, len(ap_start)-1):# erst ab dem 2. AP, da der Startzeitpunkt eig viel frueher, verfälscht Rechnung
                isi.append(determine_isi(self.confDict["dt"], ap_start[i], ap_start[i + 1]))
            if len(isi) == 0:
                isi.append(-1)
                logisi.append(-1)
            else:
                try:
                    logisi=numpy.log(isi)
                except:
                    for interval in isi:
                        logisi.append(math.log(interval))
        else:
            isi.append(-1)
            logisi.append(-1)

        if logisi[0] != -1:
            mini = min(logisi);logger.debug("mini: " + repr(mini))
            maxi = max(logisi);logger.debug("maxi: " + repr(maxi))
            if mini != maxi and maxi > 0:
                #edges = numpy.arange(mini, maxi + ((maxi-mini) / 10), ((maxi-mini) / 10) )
                edges = numpy.arange(0, (int(maxi * 10 + 1) + 1) / 10.0, 0.1)
                hist, bin_edges = numpy.histogram(logisi, bins = edges)
            else:
                hist = numpy.array([-1]) #wahrscheinlich nur 2 APs oder zu dicht beieinander
                edges = -1

        else:
            hist = numpy.array([-1])
            edges = -1

        del data; del check; del t; del ap_start; del ap_end;
        #list = [(i, j) for i in edges for j in hist]
        logger.info("-----------------------")
        logger.info("hist: " + repr(hist))
        logger.info("edges: " + repr(edges))

        return {'logISI':logisi, 'ISI':isi, 'hist':hist}


#===============================================================================
# helping functionsp
#===============================================================================
def analyze_memtrace_NB(spiketrain, dt, duration):
# a function to determine several firing parameters from a given membrane potential trace
    data = spiketrain

    #ap_start = []
    #ap_end = []

    res = AP(data, duration, dt)
    ap_start = res['aps']
    ap_end = res['ape']
    threshold = res['thr']

    #zeitens = [r * dt for r in ap_start]
    #zeitene = [r * dt for r in ap_end]
    #logger.info("ap_start: " + repr(zeitens))
    #logger.info("ap_end: " + repr(zeitene))
    #logger.info("ap_start: " + repr(ap_start))
    #logger.info("ap_end: " + repr(ap_end))

    # determine AP width at half height of every single AP
    apw = []
    if len(ap_start) > 0 and len(ap_end) > 0 and len(threshold) > 0 :

        if len(ap_end) == len(ap_start) and len(ap_end) ==len(threshold):
            for i in range(len(ap_end)): # wenn, dann gibt es weniger 'end'-indices als 'start'-indices
                apw.append(determine_ap_width(data, dt, ap_start[i], ap_end[i], threshold[i]))
            #if len(apw) > 10:
            #   ap_width =numpy.mean(apw[0:10]) # Mittelung ueber die ersten 10 (wie im Paper)
            #else:
            ap_width =numpy.mean(apw)
        else:
            m = min(len(ap_end), len(ap_start), len(threshold))
            for i in range(m):
                apw.append(determine_ap_width(data, dt, ap_start[i], ap_end[i], threshold[i]))
            ap_width =numpy.mean(apw)

    else:
        ap_width = -1

    # determine ISIs (measured from threshold crossing to threshold crossing)
    isi = []

    if len(ap_start) > 2:
        for i in range(0, len(ap_start)-1):# erst ab dem 2. AP, da der Startzeitpunkt eig viel frueher, verfälscht Rechnung
            isi.append(determine_isi(dt, ap_start[i], ap_start[i + 1]))

        #ende = determine_isi(dt, ap_start[-1], endpoint) #Abstand zum Ende der Simulation...gegebenenfalls burst am anfang und lange linie
        #if ende >= numpy.mean(isi):
        #   isi.append(ende)
    else:
        isi.append(-1)

    # determine spike frequency
    if len(ap_start) <= 1 or len(ap_end)<=1:
        frequency = 0
    else:
        frequency = len(ap_start) / ((ap_end[-1] * dt) / 1000.0)


    return {'apw': ap_width, 'freq': frequency, 'aps': ap_start, 'isi': isi}
#-----------------------------------------------------------    
def analyze_memtrace(spiketrain, dt, duration):
    data = spiketrain

#   ap_start = []
#   ap_end = []

    res = AP(data, duration, dt)
    ap_start = res['aps']
    ap_end = res['ape']
    threshold = res['thr']

    # interspikeinterval (ap_start[i + 1] bis ap_start[i])
    #isi = []
    #for i in range(len(ap_start)-1):
    #   isi.append(determine_isi(dt, ap_start[i], ap_start[i + 1]))
    isi = []
    logisi = []
    if not len(ap_start) <= 2:
        for i in range(0, len(ap_start)-1):# erst ab dem 2. AP, da der Startzeitpunkt eig viel frueher, verfälscht Rechnung
            isi.append(determine_isi(dt, ap_start[i], ap_start[i + 1]))

        #ende = determine_isi(dt, ap_start[-1], endpoint) #Abstand zum Ende der Simulation...gegebenenfalls burst am anfang und lange linie
        #if ende >= numpy.mean(isi):
        #   isi.append(ende

        if len(isi) == 0:
            isi.append(-1)
            logisi.append(-1)
        else:
            try:
                logisi=numpy.log(isi)
            except:
                for interval in isi:
                    logisi.append(math.log(interval))
    else:
        isi.append(-1)
        logisi.append(-1)

    if logisi[0] != -1:
        mini = min(logisi)
        maxi = max(logisi)
        if mini != maxi and maxi >0:
            #edges = numpy.arange(mini, maxi + ((maxi-mini) / 10), ((maxi-mini) / 10) )
            #edges = range(0, int(math.ceil(maxi + 1)), 1)
            edges = numpy.arange(0, (int(maxi * 10 + 1) + 1) / 10.0, 0.1)
            hist, bin_edges = numpy.histogram(logisi, bins = edges)
        else:
            hist = numpy.array([-1]) #wahrscheinlich nur 2 APs
            edges = numpy.array([-1])

    else:
        hist = numpy.array([-1])
        edges = numpy.array([-1])
    logger.info("hist: " + repr(hist))
    logger.info("edges: " + repr(edges))

    # determine bursts
    bursts_start = [0]
    bursts_end = [0]
    burst_flag = 0
    burstcounter = 0
    save = 100
    #idx = numpy.argmax(hist[0:len(hist) / 2]) # hauptISI der Bursts holen (aus Log-Plot)
    #maximum = numpy.max(hist[0:len(hist) / 2])
    #thr = 10**(bin_edges[idx + int(10 * maximum / numpy.sum(hist))])
    #thr = 10**index] #umrechnen in ISIHistogramm
    #logger.info("max: " + repr(maximum))
    #logger.info("idx: " + repr(idx))
    #logger.info("burstThr: " + repr(thr))

    thr = 11 # TODO: find appropriate threshold for isi to define a burst!!

    for i in range(1, len(isi)-1):


        if isi[i-1] < thr:
            if burst_flag == 1:
                if save == burstcounter:
                    bursts_end.pop()
                bursts_end.append(i + 1)
                save = burstcounter
                if isi[i] >= thr:
                    burst_flag = 0
                    burstcounter = burstcounter + 1
            else:
                if save == burstcounter:
                    bursts_end.pop()
                bursts_end.append(i)
                bursts_start.append(i-1)
                burst_flag = 1
                save = burstcounter

    ibf = [0]
    if not len(bursts_start) == 1 and not len(bursts_end) == 1:
        for i in range(1, len(bursts_start)):
            burstlength = bursts_end[i] - bursts_start[i]
            ibf.append(1000 / numpy.mean(isi[bursts_start[i]:bursts_end[i]])) #[1 / ms] * 1000 = [1 / s] = Hz
        try:
            ibf_mean = numpy.mean(ibf)
        except:
            ibf_mean = 0; logger.error("mean(ibf) hat nicht funktioniert, analysis-Zeile-408")
    else:
        ibf_mean = -1

    overall_bursts = len(bursts_end)-1
    firsthalf_bursts = 0
    if len(ap_start) != 0:
        burst_time = ap_start[0] * dt

        j = 0
        if not overall_bursts == 0:
            while j <= bursts_end[1]:
                burst_time = burst_time + isi[j]
                j = j + 1
            for i in range(1, overall_bursts):
                if burst_time < (len(spiketrain) * dt / 2):
                    firsthalf_bursts = firsthalf_bursts +1
                    if i < overall_bursts:
                        #j = 0
                        while j <= bursts_end[i + 1]:
                            burst_time = burst_time + isi[j]
                            j = j + 1
    else:
        logger.info(repr(ap_start))
    try:
        inactivation_rate = 100 * float(firsthalf_bursts) / overall_bursts
        #logger.info("first half:" + repr(firsthalf_bursts))
        #logger.info("overall:" + repr(overall_bursts))
    except:
        inactivation_rate = -1

    # determine AP width at half height of every single AP
    apw = []
    if len(bursts_start) > 1 and len(ap_end) == len(ap_start):
        for burst in bursts_start:
            apw.append(determine_ap_width(data, dt, ap_start[burst], ap_end[burst], threshold[burst]))
        ap_width =numpy.mean(apw)
    else:
        ap_width = -1


    return {'apw':ap_width, 'ibf':ibf_mean, 'ir':inactivation_rate, 'isi':isi}
#-----------------------------------------------------------
def determine_ap_width(data, dt, start, fin, thr):

    apdata=data[start:fin]
    if len(apdata) != 0:
        maximum = max(apdata)
        index = apdata.index(maximum) + 1
        maximum = maximum-thr # + 20.0
        halfmax = (maximum / 2)
        halfmax = halfmax + thr # - 20.0
        apdata_abs_halfmax = []
        apdata_abs_len_halfmax = []

        #Linke Seite
        for i in range(0, index):
            apdata_abs_halfmax.append(absolute(apdata[i] - halfmax))
        lindex = apdata_abs_halfmax.index(min(apdata_abs_halfmax)) + 1

        # rechte Seite
        for i in range(index, len(apdata) - 1):
            apdata_abs_len_halfmax.append(absolute(apdata[i] - halfmax))
        if len(apdata_abs_len_halfmax) != 0:
            rindex = apdata_abs_len_halfmax.index(min(apdata_abs_len_halfmax)) + 1
        else:
            rindex = lindex + 1

        width=((index + rindex + 1) - lindex) * dt

    else:
        width = 0

    return width

#-----------------------------------------------------------
def absolute(x):
    if type(x) is int or type(x) is float:
        if x >= 0:
            return x
        else:
            return -x
    elif type(x) is numpy.ndarray or type(x) is list:
        for i in range(len(x)):
            if x[i] >= 0:
                pass
            else:
                x[i] = x[i] * (-1)
        return x
    else:
        return x

#-----------------------------------------------------------
def determine_isi(dt, start1, start2):

    ISinterval=(start2 - start1) * dt;
    return ISinterval

#-----------------------------------------------------------
#Aktionspotenziale:
def AP(data, duration, dt):
    ap_start = []
    ap_end = []

    #Calculating the threshold (by Nowak (bib:cat)):
    #Über Anstieg der Steigung dV/dt, 3*SD
    #
    #Steigung von Zeitschritt zu Zeitschritt berechnen:
    threshold = []
    steigOUT = []
    std = []
    t = 0
    for i in range(len(data) - 1):

        if i < t: continue # AP überspringen

        steigOUT.append((data[i + 1] - data[i]) / dt)
        if steigOUT[-1] < 0:
            steigOUT.pop()
            continue
        if len(steigOUT) > 10:
            mu = numpy.mean(steigOUT[-10:])
            std.append(numpy.std(steigOUT[-10:]))
        else:
            mu = numpy.mean(steigOUT)
            std.append(numpy.std(steigOUT))

        if len(std) > 1:

            if mu >= 3 * std[-2]: # [-2], da std vom letzten Iterationsschritt gebraucht wird
                threshold.append(data[i])
                ap_start.append(i)

                steigIN = [0] #fuer steigIN[-2]
                t = i
                notGood = 0
                tsave = []
                up = 0
                while steigIN[-1] >= 0: #steigender abschnitt

                    if steigIN[-1] > 1: # korrigiert später niedrige steigung im steigenden Abschnitt nach rasantem Aufstieg!
                        up = 1
                    if steigIN[-1] < 0.25:
                        if up == 1:
                            notGood = 0
                            tsave.append(t)
                        else:
                            notGood =notGood + 1
                            tsave = []
                    else:
                        notGood = 0
                        tsave.append(t)
                    if notGood >= 8 / dt:
                        break
                    if t > len(data) - 2:
                        break
                    steigIN.append((data[t + 1]-data[t]) / dt)
                    del steigIN[0]
                    t = t+1

                if t > len(data)-1:
                    break
                elif notGood >= 80:
                    if len(ap_start) != 0:
                        ap_start.pop()
                        threshold.pop()
                    continue

                if not tsave and notGood < 80:
                    if len(ap_start) != 0:
                        ap_start.pop()
                        threshold.pop()
                    continue
                else:
                    if not tsave:
                        continue
                    else:
                        if len(ap_start)!=0:
                            ap_start.pop()
                            threshold.pop()
                        threshold.append(data[tsave[0]])
                        ap_start.append(tsave[0])

                notGood = 0
                m = max(data[ap_start[-1]:t])
                down = 0
                if m >= threshold[-1] + 20: #TODO: signifikanz
                    while steigIN[-1] < 0: #fallender Abschnitt
                        if steigIN[-1] > -1:# korrigiert später niedriges Gefälle im fallenden Abschnitt nach rasantem Abfall!
                            down = 1
                        if steigIN[-1] < -1:
                            if down == 1:
                                notGood = 0
                            else:
                                notGood =notGood + 1
                        else:
                            notGood = 0
                        if notGood >= 80:
                            if len(ap_start) != 0:
                                ap_start.pop()
                                threshold.pop()
                            break

                        if t > len(data)-1:
                            break
                        steigIN.append((data[t + 1] - data[t]) / dt)
                        del steigIN[0]
                        t = t+1
                    if t > len(data)-1:
                        ap_end.append(t)
                        break
                    elif notGood >= 80:
                        if len(ap_start) != 0:
                            ap_start.pop()
                            threshold.pop()
                        continue
                    else:
                        ap_end.append(t)
                else:
                    if len(ap_start) != 0:
                        ap_start.pop()
                        threshold.pop()
                steigOUT = []
                std = []
                continue
            else:
                continue
    if len(ap_start) > len(ap_end):
        if len(ap_start) != 0:
            ap_start.pop()
            threshold.pop()



    return {'aps':ap_start, 'ape':ap_end, 'thr':threshold}

#-----------------------------------------------------------
