
# coding=utf-8

from __future__ import division
import random
import math

import projConf
import fitness
import chromgen

from itertools import product as cart_product

def start(proj_conf, **args):
    algorithm = GridSearch(proj_conf, **args)
    result = algorithm.search_grid()

    algorithm.logger.info(repr(result))

#-----------------------------------------------------------
class GridSearch(object):

    l_bound = None
    u_bound = None
    logger = None
    mode = None
    proj_conf = None
    fitness_args = None
    parsed_kwargs = None

    #-----------------------------------------------------------
    def __init__(self, proj_conf, **args):

        self.mode = proj_conf.get("mode", "Simulation")

        (l_bound, u_bound) = chromgen.get_bounds(mode)

        self.proj_conf = proj_conf
        self.logger = self.proj_conf.getClientLogger("gridSearch")
        self.fitness_args = { "proj_conf": proj_conf, "mode": self.mode}

        # Parameters for fitness evaluation
        self.parsed_kwargs = {}
        for item in proj_conf.cfg.items("fitness.evaluate_param"):
            self.parsed_kwargs[item[0]] = eval(item[1])
        numCurrents = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["numCurrents"] = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["proj_name"] = proj_conf.parseProjectConfig()["proj_name"]
        self.fitness_args.update(self.parsed_kwargs)

    #-----------------------------------------------------------
    def search_grid(self):
        best_state = []
        best_fitness = -20000
        
        grid = generate_grid()
        fitnesses = fitness.evaluate_param(grid)

        for i in range(0,len(fitnesses)):
            if fitnesses[i] > best_fitness:
                best_fitness = fitnesses[i]
                best_state   = grid[i]

        return (best_state, best_fitness) 
    #-----------------------------------------------------------
    def generate_grid(self):

        ar   = generate_exponential_steps(l_bound[0], u_bound[0], delta)
        cal  = generate_exponential_steps(l_bound[1], u_bound[1], delta)
        cat  = generate_exponential_steps(l_bound[2], u_bound[2], delta)
        k2   = generate_exponential_steps(l_bound[3], u_bound[3], delta)
        ka   = generate_exponential_steps(l_bound[4], u_bound[4], delta)
        kahp = generate_exponential_steps(l_bound[5], u_bound[5], delta)
        kc   = generate_exponential_steps(l_bound[6], u_bound[6], delta)
        alpha = generate_steps(l_bound[7], u_bound[7], 0.1)
        km   = generate_exponential_steps(l_bound[8], u_bound[8], delta)
        naf  = generate_exponential_steps(l_bound[9], u_bound[9], delta)
        nap  = generate_exponential_steps(l_bound[10], u_bound[10], delta)
        pas  = generate_exponential_steps(l_bound[11], u_bound[11], delta)

        return list(cart_product(ar, cal, cat, k2, ka, kahp, kc, alpha, km, naf, nap, pas))
        
    #-----------------------------------------------------------
    def generate_steps(self, lower, upper, delta):
        step = lower
        while step <= upper:
            yield step
            step = step + delta
    
    #-----------------------------------------------------------
    def generate_exponential_steps(self, lower, upper, delta):
        step = lower
        while step <= upper:
            yield step
            step = step * delta
