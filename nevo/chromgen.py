# coding=utf-8

from __future__ import with_statement

import copy

"""
######################################## GENERATE_CONDUCTANCE #######################################################
Instanzen bilden:
verschiedene Ionenkanäle mit unterschiedlichen Leitfähigkeiten
"""
def get_bounds(mode):
    """Returns bounds applicable to the chromosome form (with 'alpha' instead of 'k_dr')
    """
    if mode  == "RS":
        # Values are:   ar      cal      cat       k2       ka     kahp
        u_bound = [10** -7, 10** -7, 10** -6, 10** -5, 10** -5, 10** -5,
        #               kc    alpha       km      naf      nap      pas
                   10** -5,     1.5, 10** -4, 10** -3, 10** -5, 0.00002]
        
        # Values are:   ar      cal      cat       k2       ka     kahp
        l_bound = [10**-14, 10**-14, 10**-14, 10**-14, 10**-14, 10**-14,
        #               kc    alpha       km      naf      nap      pas
                   10**-14,     0.5, 10**-11, 10** -5, 10**-14, 0.00002]
    elif mode == "FS":
        # Values are:   ar      cal      cat       k2       ka     kahp
        u_bound = [10** -7, 10** -7, 10** -6,       0, 10** -5,       0,
        #               kc    alpha       km      naf      nap      pas
                   10** -5,       2,       0, 10** -3,       0, 0.00002]

        # Values are:   ar      cal      cat       k2       ka     kahp
        l_bound = [10**-14, 10**-14, 10**-14,       0, 10**-14,       0,
        #               kc    alpha       km      naf      nap      pas
                   10**-14,       1,       0, 10** -5,       0, 0.00002]
    elif mode == "CH":
        # Values are:   ar      cal      cat       k2     kaib     kahp
        u_bound = [10** -7, 10** -9, 10** -7, 10** -5, 10** -5, 10** -5,
        #               kc    alpha       km      naf      nap      pas
                   10** -5,     1.5, 10** -7, 10** -3, 10** -5, 0.00002]

        # Values are:   ar      cal      cat       k2     kaib     kahp
        l_bound = [10**-14, 10**-12, 10**-12, 10**-12, 10**-12, 10**-12,
        #               kc    alpha       km      naf      nap      pas
                   10**-12,     0.5, 10**-11, 10** -5, 10**-12, 0.00002]
    else:
        # Values are:   ar      cal      cat       k2     kaib     kahp
        u_bound = [10** -7, 10** -9, 10** -7, 10** -5, 10** -5, 10** -5,
        #               kc    alpha       km      naf      nap      pas
                   10** -5,     1.5, 10** -7, 10** -3, 10** -5, 0.00002]

        # Values are:   ar      cal      cat       k2     kaib     kahp
        l_bound = [10**-14, 10**-12, 10**-12, 10**-12, 10**-12, 10**-12,
        #               kc    alpha       km      naf      nap      pas
                   10**-12,     0.5, 10**-11, 10** -5, 10**-12, 0.00002]
    return (l_bound, u_bound)
#-----------------------------------------------------------
def chromosome_to_channels(chromosome):
    """Transforms the chromosome representation with 'alpha' instead of 'k_dr'
    into the channel form.

    Returns only a copy without modifying the given chromosome.
    """
    copy_chrom = copy.deepcopy(chromosome)
    copy_chrom[7] = copy_chrom[9] * copy_chrom[7]
    return copy_chrom
#-----------------------------------------------------------
def channels_to_chromosome(channels):
    """Transforms the channels representation with 'k_dr' to its chromosome
    form with 'alpha'

    Returns only a copy without modifying the given chromosome.
    """
    copy_chrom = copy.deepcopy(channels)
    copy_chrom[7] =  copy_chrom[7] / copy_chrom[9]
    return copy_chrom
#-----------------------------------------------------------
def generate_chromosome(random, args):
    pconf = args["pconf"]
    chromosome = []
    mode = args["mode"]

    l_bound, u_bound = get_bounds(mode)
    chromosome = [random.uniform(x,y) for (x,y) in zip(l_bound, u_bound)]

    return chromosome
#endDEF
#-----------------------------------------------------------
def get_channel_data(mode):
    """Returns channel data as a list of strings"""
    if mode == "RS" or mode == "FS":
        channel = ['ar', 'ar', 'ar',
                   'cal', 'cal',
                   'cat', 'cat',
                   'k2', 'k2',
                   'ka', 'ka', 'ka',
                   'kahp_deeppyr', 'kahp_deeppyr',
                   'kc', 'kc',
                   'kdr', 'kdr', 'kdr',
                   'km', 'km', 'km',
                   'naf', 'naf', 'naf', 'naf',
                   'nap', 'nap',
                   'pas', 'pas', 'pas', 'pas']

    else: #Bursting
        channel = ['ar', 'ar', 'ar',
                   'cal', 'cal',
                   'cat', 'cat',
                   'k2', 'k2',
                   'ka_ib', 'ka_ib', 'ka_ib',
                   'kahp_deeppyr', 'kahp_deeppyr',
                   'kc', 'kc',
                   'kdr', 'kdr', 'kdr',
                   'km', 'km', 'km',
                   'naf', 'naf', 'naf', 'naf',
                   'nap', 'nap',
                   'pas', 'pas', 'pas', 'pas']
    return channel
#-----------------------------------------------------------
def get_location_data(mode):
    """Returns location data as a list of strings"""
    
    if mode == "RS" or mode == "FS":
        location = ['soma_dendrite', 'soma2', 'dendrite_group',
                    'soma2', 'dendrite_group',
                    'soma2', 'dendrite_group',
                    'dendrite_group', 'soma_group',
                    'dendrite_group', 'soma2', 'axon_group',
                    'soma2', 'dendrite_group',
                    'dendrite_group', 'soma2',
                    'dendrite_group', 'soma2', 'axon_group',
                    'axon_group', 'dendrite_group', 'soma2',
                    'all', 'dendrite_group', 'soma2', 'axon_group',
                    'dendrite_group', 'soma2',
                    'all', 'axon_group', 'soma2', 'dendrite_group']
    else: #Bursting
        location = ['soma_dendrite', 'soma2', 'dendrite_group',
                    'dendrite_group', 'soma2',
                    'soma2', 'dendrite_group',
                    'dendrite_group', 'soma_group',
                    'soma_group', 'dendrite_group', 'axon_group',
                    'soma2', 'dendrite_group',
                    'dendrite_group', 'soma2',
                    'dendrite_group', 'soma2', 'axon_group',
                    'dendrite_group', 'soma2', 'axon_group',
                    'all', 'dendrite_group', 'soma2', 'axon_group',
                    'dendrite_group', 'soma2',
                    'all', 'axon_group', 'soma2', 'dendrite_group']
    return location

"""
Berechnen der Leitfähigkeiten aus den oben randomisiert bestimmten Zehnerpotenzen und den exakten Werten der Ionenkanäle
"""
def calc_dens(channels, mode):
    # channels = [ar, cal, cat, k2, ka,(kaib), kahp, kc, kdr, km, naf, nap, pas]
    list = []
    
    if mode == "RS" or mode == "FS":
        ar = [-1.0, 1.0, 2.0] 
        for v in ar:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[0])
        cal = [1.6, 0.32] 
        for v in cal:
            list.append(v*channels[1])
        cat = [1.0, 2.0]
        for v in cat:
            list.append(v*channels[2])
        k2 = [1.0,0.5] 
        for v in k2:
            list.append(v*channels[3])
        ka = [1.6, 2.0, 0.06] 
        for v in ka:
            list.append(v*channels[4])
        kahp = [2.0, 4.0]
        for v in kahp:
            list.append(v*channels[5])
        kc = [1.2, 2.88] 
        for v in kc:
            list.append(v*channels[6])
        kdr = [1.5, 1.7, 4.5]
        for v in kdr:
            list.append(v*channels[7])
        km = [ 3.0, 0.75, 0.85] 
        for v in km:
            list.append(v*channels[8])
        naf = [ -1.0, 1.875, 2.0, 4.5] 
        for v in naf:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[9])
        nap = [ 1.0, 1.6] 
        for v in nap:
            list.append(v*channels[10])
        pas = [-1.0, 1.0, 0.02, 0.3] 
        for v in pas:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[11])
                
    else: # IB, CH
        ar = [-1.0, 1.0, 2.0] 
        for v in ar:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[0])
        cal = [6.0, 6.0] 
        for v in cal:
            list.append(v*channels[1])
        cat = [1.0, 2.0]
        for v in cat:
            list.append(v*channels[2])
        k2 = [1.0, 0.5] 
        for v in k2:
            list.append(v*channels[3])
        kaib = [ 2.0, 1.6, 0.06] 
        for v in kaib:
            list.append(v*channels[4])
        kahp = [2.0, 4.0]
        for v in kahp:
            list.append(v*channels[5])
        kc = [ 0.3,0.72] 
        for v in kc:
            list.append(v*channels[6])
        kdr = [ 1.7, 1.7, 4.5] 
        for v in kdr:
            list.append(v*channels[7])
        km = [ 3.0, 3.4, 6.0]
        for v in km:
            list.append(v*channels[8])
        naf = [-1.0, 2.0, 2.0, 4.5] 
        for v in naf:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[9])
        nap = [ 4.0, 6.4] 
        for v in nap:
            list.append(v*channels[10])
        pas = [-1.0, 1.0, 0.02, 0.3] 
        for v in pas:
            if v == -1.0:
                list.append(v)
            else:
                list.append(v*channels[11])
    return list
#endDEF
