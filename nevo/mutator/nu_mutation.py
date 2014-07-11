import copy

###################################### MUTATE_UNIFORM #####################################################
# 1:1 "abgeschrieben" von der inspyred-Funktion, Sie hat beim regulaeren Aufruf nicht funktioniert
def nuMutation(random, candidate, args):
    l_bound = args['lower_bound']
    u_bound = args['upper_bound']
    num_gens = args['_ec'].num_generations
    max_gens = args['max_generations']
    strength = args['mutation_strength']
    exponent = (1.0-num_gens/float(max_gens))**strength
    mutant = copy.copy(candidate)
    for i, (c,lo,hi) in enumerate(zip(candidate, l_bound, u_bound)):
        #if random.random() < args['mutation_rate']:
        if random.random() <= 0.5:
            new_value = c+(hi-c)*(1.0-random.random()**exponent)
        else:
            new_value = c-(c-lo)*(1.0-random.random()**exponent)
        mutant[i] = new_value
    return mutant
#endDEF
