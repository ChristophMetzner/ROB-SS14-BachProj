# coding=utf-8
import math
import numpy
import sys
import random
from diptest_inst import DipTest

def HartigansDipTest(logger, xpdf):
    #logger.debug("starting HartigansDipTest")
    #function   [dip,xl,xu, ifault, gcm, lcm, mn, mj]=HartigansDipTest(xpdf)
    #
    # 
    # This is a translation by A. Kloskowski (May 31 2013)
    # into Python from MATLAB code from F. Mechler (August 27 2002) who had it from the original FORTRAN code of Hartigan's Subroutine DIPTST algorithm 
    # Ref: Algorithm AS 217 APPL. STATIST. (1985) Vol. 34. No.3 pg 322-325
    #
    # Appended by F. Mechler (September 2 2002) to deal with a perfectly unimodal input
    # This check the original Hartigan algorithm omitted, which leads to an infinite cycle
    #
    # Appended by A. Kloskowski (May 31 2013) please as input only one line vector (1xN) for each sample data set
    # All arrays start at index 1 (index 0 will be a random number)
    #
    # HartigansDipTest, like DIPTST, does the dip calculation for an ordered vector XPDF (1xN) using
    # the greatest convex minorant (gcm) and the least concave majorant (lcm),
    # skipping through the data using the change points of these distributions.
    # It returns the 'DIP' statistic, and 7 more optional results, which include
    # the modal interval (XL,XU), ann error flag IFAULT (>0 flags an error)
    # as well as the minorant and majorant fits GCM, LCM, and the corresponding support indices MN, and MJ

    # sort X in increasing order in column vector
    x = [0]
    for t in xpdf:
    
        x.append(t)
    #logger.debug('a')
    x = sorted(x)
    N = len(x)-1
    mn = numpy.zeros((N+1,1))
    mj = numpy.zeros((N+1,1))
    lcm = numpy.zeros((N+1,1))
    gcm = numpy.zeros((N+1,1))
    ifault = 0

    # Check that N is positive
    if N<=0:
        ifault = 1
        logger.warning('HartigansDipTest.    InputError :  ifault=%d'%ifault)
        return{'ifault':4, 'dip': 0}

    # Check if N is one
    if N==1:
        xl = x[1]
        xu = x[N]
        dip = 0.0
        ifault = 2
        logger.warning('HartigansDipTest.    InputError :  ifault=%d'%ifault)
        return{'ifault': 4, 'dip': dip}

    if N>1:
        #Check that x is sorted
        if x != sorted(x):
            ifault = 3
            logger.warning('HartigansDipTest.    InputError :  ifault=%d'%ifault)
            return{'ifault': 4, 'dip': 0}
        # check for all values of x identical OR for case 1<N<4
        if not (x[N] > x[1] and 4<=N):
            xl = x[1]
            xu = x[N]
            dip = 0.0
            ifault = 4
            logger.warning('HartigansDipTest.    InputError :  ifault=%d'%ifault)
            return{'ifault': 1, 'dip': dip}

    # Check if X is perfectly unimodal
    # Hartigan's original DIPTST algorithm did not check for this condition
    # and DIPTST runs into infinite cycle for a unimodal input
    # The condition that the input is unimodal is equivalent to having 
    # at most 1 sign change in the second derivative of the input p.d.f.
    xdiff = [0]
    for n in range(2,len(x)):
        xdiff.append(x[n]-x[n-1])
    
    #logger.debug('b')
    xsign = [0]
    for n in range(2,len(xdiff)):
            xsign.append(sign(xdiff[n]-xdiff[n-1])*(-1))
    #logger.debug('c')
    # This condition check below works even 
    # if the unimodal p.d.f. has its mode in the very first or last point of the input 
    # because then the boolean argument is Empty Matrix, and ANY returns 1 for an Empty Matrix
    posi = []
    negi = []
    for n,m in enumerate(xsign):
        if m>0:
            posi.append(n)
        else:
            negi.append(n)
    #logger.debug('d')
    all_smaller = 1
    for i in posi:
        if i < min(negi):
            pass
        else:
            all_smaller = 0
            break
    #logger.debug('e')
    if not posi or not negi or all_smaller:
        # An unimodal function is its own best unimodal approximation, with a zero corresponding dip
        xl = x[1]
        xu = x[N]
        dip = 0.0
        ifault = 5
        #logger.debug('            -> The input is a perfectly UNIMODAL input function')
        return{'ifault': 1, 'dip': dip}

    # LOW  contains the index of the current estimate of the lower end of the modal interval
    # HIGH contains the index of the current estimate of the upper end of the modal interval
    fn=float(N)
    low=1
    high=N
    dip=1.0/fn
    xl=x[low]
    xu=x[high]
    
    # establish the indices over which combination is necessary for the convex minorant fit
    mn[1] = 1
    for j in range(2,N+1):
        mn[j] = j-1
        # here is the beginning of a while loop
        mnj=int(mn[j])  
        mnmnj=int(mn[mnj]) 
        a=mnj-mnmnj 
        b=j-mnj     
        while not( (mnj==1) or ((x[j]-x[mnj])*a < (x[mnj]-x[mnmnj])*b)):
            mn[j]=mnmnj
            mnj=int(mn[j])
            mnmnj=int(mn[mnj])
            a=mnj-mnmnj
            b=j-mnj
    #logger.debug('f')
    # establish the indices over which combination is necessary for the concave majorant fit
    mj[N]=N
    na=N-1
    for jk in range(1,na+1):
        k=N-jk
        mj[k]=k+1
        # here is the beginning of a while loop
        mjk=int(mj[k])
        mjmjk=int(mj[mjk])
        a=mjk-mjmjk
        b=k-mjk
        while not( (mjk==N) or ((x[k]-x[mjk])*a < (x[mjk]-x[mjmjk])*b)):
            mj[k]=mjmjk
            mjk=int(mj[k])
            mjmjk=int(mj[mjk])
            a=mjk-mjmjk
            b=k-mjk
    #logger.debug('g')
    itarate_flag = 1
    iterCnt = 0
    # start the cycling of great RECYCLE
    while itarate_flag:
        if iterCnt > 100:
            break
        iterCnt = iterCnt + 1
        #logger.debug(repr(itarate_flag))
        # collect the change points for the GCM from HIGH to LOW
        # CODE BREAK POINT 40
        ic=1
        gcm[1]=high #N
        igcm1=int(gcm[ic])#N
        ic=ic+1
        gcm[ic]=int(mn[igcm1])
        while(gcm[ic] > low):
            igcm1=int(gcm[ic])
            ic=ic+1
            gcm[ic]=int(mn[igcm1])
        #logger.debug('h')
        icx=ic
        # collect the change points for the LCM from LOW to HIGH
        ic=1
        lcm[1]=low
        lcm1=int(lcm[ic])
        ic=ic+1
        lcm[ic]=int(mj[lcm1])
        
        while(lcm[ic] < high):
            lcm1=int(lcm[ic])
            ic=ic+1
            lcm[ic]=int(mj[lcm1])
        #logger.debug('i')
        icv=ic

        # ICX, IX, IG are counters for the convex minorant
        # ICV, IV, IH are counters for the concave majorant
        ig=icx
        ih=icv

        # find the largest distance greater than 'DIP' between the GCM and the LCM from low to high
        ix=icx-1
        iv=2
        d=0.0
        
        # Either GOTO CODE BREAK POINT 65 OR ELSE GOTO CODE BREAK POINT 50;
        if not ( (icx != 2) or (icv != 2)):
            d=1.0/fn
        else:
            iterate_BP50=1;
            while iterate_BP50:
                # CODE BREAK POINT 50
                igcmx=int(gcm[ix])
                lcmiv=int(lcm[iv])
                if not(igcmx > lcmiv):
                    # if the next point of either the GCM or LCM is from the LCM then calculate distance here
                    # OTHERWISE, GOTO BREAK POINT 55
                    lcmiv1=int(lcm[iv-1])
                    a=lcmiv-lcmiv1
                    b=igcmx-lcmiv1-1
                    dx=float((x[igcmx]-x[lcmiv1])*a)/(fn*(x[lcmiv]-x[lcmiv1]))-float(b)/fn
                    ix=ix-1
                    if(dx < d):
                        goto60 = 1
                    else:
                        d=dx
                        ig=ix+1
                        ih=iv
                        goto60 = 1

                else:
                    # if the next point of either the GCM or LCM is from the GCM then calculate distance here
                    # CODE BREAK POINT 55
                    lcmiv=int(lcm[iv])
                    igcm=int(gcm[ix])
                    igcm1=int(gcm[ix+1])
                    a=lcmiv-igcm1+1
                    b=igcm-igcm1
                    dx=float(a)/fn-float((x[lcmiv]-x[igcm1])*b)/(fn*(x[igcm]-x[igcm1]))
                    iv=iv+1
                    if not(dx < d):
                        d=dx
                        ig=ix+1
                        ih=iv-1
                    goto60 = 1

                if goto60:
                # CODE BREAK POINT 60
                    if (ix < 1):
                        ix=1
                    if (iv > icv):
                        iv=icv
                    iterate_BP50 = (gcm[ix] != lcm[iv])

        # CODE BREAK POINT 65
        itarate_flag = not(d < dip)
        if itarate_flag:
            # if itarate_flag is true, then continue calculations and the great iteration cycle
            # if itarate_flag is NOT true, then stop calculations here, and break out of great iteration cycle to BREAK POINT 100

            # calculate the DIPs for the corrent LOW and HIGH

            #% the DIP for the convex minorant
            dl=0.0
            # if not true, go to CODE BREAK POINT 80
            if ig != icx:
                icxa=icx-1
                for j in range(ig,icxa+1):
                    temp=1.0/fn
                    jb=int(gcm[j+1])
                    je=int(gcm[j])
                    # if not true either, go to CODE BREAK POINT 74
                    if not(je-jb <= 1):
                        if not(x[je]==x[jb]):
                            a=(je-jb)
                            const=float(a)/(fn*(x[je]-x[jb]))
                            for jr in range(jb,je+1):
                                b=jr-jb+1
                                t=float(b)/fn-(x[jr]-x[jb])*const
                                if (t>temp):
                                    temp=t 
                                
                    # CODE BREAK POINT 74
                    if (dl < temp):
                        dl=temp

            # the DIP for the concave majorant
            # CODE BREAK POINT 80
            du=0.0
            # if not true, go to CODE BREAK POINT 90
            if not (ih==icv):
                icva=icv-1
                for k in range(ih,icva+1):
                    temp=1.0/fn
                    kb=int(lcm[k])
                    ke=int(lcm[k+1])
                    # if not true either, go to CODE BREAK POINT 86
                    if not (ke-kb <= 1):
                        if not (x[ke] == x[kb]):
                            a=ke-kb
                            const=float(a)/(fn*(x[ke]-x[kb]))
                        for kr in range(kb,ke+1):
                            b=kr-kb-1
                            t=(x[kr]-x[kb])*const-float(b)/fn
                            if (t>temp):
                                temp=t
                        
                    # CODE BREAK POINT 86
                    if (du < temp): 
                        du=temp
        
            # determine the current maximum
            # CODE BREAK POINT 90
            dipnew=dl
            if (du > dl):
                dipnew=du
            if (dip < dipnew):
                dip=dipnew
            low=int(gcm[ig])
            high=int(lcm[ih])     

        # return to CODE BREAK POINT 40 or break out of great RECYCLE;


    # CODE BREAK POINT 100
    dip=0.5*dip
    xl=x[low]
    xu=x[high]
    #logger.debug('j')
    return {'dip':dip,'xlow':xl,'xup':xu, 'ifault':ifault, 'gcm':gcm, 'lcm':lcm, 'mn':mn, 'mj':mj}

def HartigansDipSignifTest(logger, xpdf,nboot):
    #logger.debug("starting HartigansDipSignifTest")
    #  function     [dip,p_value,xlow,xup]=HartigansDipSignifTest(xpdf,nboot)
    #
    # calculates Hartigan's DIP statistic and its significance for the empirical p.d.f  XPDF (vector of sample values)
    # This routine calls the matlab routine 'HartigansDipTest' that actually calculates the DIP
    # NBOOT is the user-supplied sample size of boot-strap
    # Matlab-Code by F. Mechler (27 August 2002)
    # Python-Code by A. Kloskowski (Jun 3 2013)

    # calculate the DIP statistic from the empirical pdf

    result1 = HartigansDipTest(logger, xpdf)
    if result1['ifault'] == 4:
        logger.debug('zu wenig')
        return {'dip':0, 'p':2}
    elif result1['ifault'] == 1:
        return {'dip': 0, 'p':0.01}
    N=len(xpdf)

    # calculate a bootstrap sample of size NBOOT of the dip statistic for a uniform pdf of sample size N (the same as empirical pdf)
    boot_dip=numpy.zeros((nboot+1,1))
    for i in range(1, nboot+1):
        #logger.debug(repr(i))
        unif = [random.uniform(0,1) for j in range(N)]
        unifpdfboot=sorted(unif);
        resultunif=HartigansDipTest(logger, unifpdfboot);
        boot_dip[i] = resultunif['dip']
        
    N=len(xpdf)
    
    boot_dip=sorted(boot_dip)
    sum_true = 0.0
    for s in range(1, len(boot_dip)):
        if result1['dip'] < boot_dip[s]:
            sum_true = sum_true+1
    p_value=sum_true/nboot
    
    return {'dip':result1['dip'], 'p':p_value} #'xlow':result1['xlow'], 'xup':result1['xup']}

def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0    
    
def main(pconf, ISIvalues, idx):
    logger = pconf.get_logger("hartigans_dip_demo")
    #logger.debug(repr(i))
    
    #### Anzahl der Kandidaten aus Datei lesen #####
    # index = open("C:\Python27\Analyse\index.txt","r")
    # len_cand = 0
    # for line in index:
        # line = line.strip()               
        # try:  
            # len_cand=int(line[-1])
        # except:
            # pass
    # index.close()
    # pop_size = len_cand
    
    #reads data from file to analyze with HartiganDipSigniTest
    # Code by A. Kloskowski [Jun 3 2013]

    # lines = []
    # inst = []
    # for i in range(pop_size):
        # filename = "C:\Users\Anne\Documents\Luebeck\Uni-Vorlesung\BACHELORARBEIT\Pyr_RS\simulations\PySim_"+repr(i)+"\CellGroup_1_0.dat"
        # file = open(filename, 'r')
        # for line in file:
            # line = line.strip()               
            # try:  
                # x=float(line)
            # except:
                # pass
            # lines.append(x)   
        # data = lines[0:1000]  


    nboot = 1000
    result = HartigansDipSignifTest(logger, ISIvalues, nboot)
    inst = DipTest(idx, result['dip'], result['p'])
    
    return inst 


