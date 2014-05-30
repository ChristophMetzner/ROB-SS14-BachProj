#! usr/local/lib/python2.7 python
# coding=utf-8

import projConf

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
        with open(projConf.getPath("locationFile", "GenAlg"), "a") as location:
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
            location.write('#\n ');
        with open(projConf.getPath("channelFile", "GenAlg"), "a") as channel:
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
            channel.write('#\n ')


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
        with open(projConf.getPath("locationFile", "GenAlg"), "a") as location:
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
            location.write('#\n ');
                                       
        with open(projConf.getPath("channelFile", "GenAlg"), "a") as channel:
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
            channel.write('#\n ')
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
    with open(projConf.getPath("densityFile", "GenAlg"), "a") as density:
        string = ''
        for e in list:
            string += str(e)+'\n'
            #print e
        density.write(string+'#\n ')
#endDEF
