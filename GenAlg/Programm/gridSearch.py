# coding=utf-8

import fitness
import chromgen

import math
import operator

from itertools import product

logger = None

QUEUESIZE = 10

#------------------------------------------------
def start(proj_conf, **args):
    mode = proj_conf.get("mode", "Simulation")
    global logger
    logger = proj_conf.getClientLogger("gridSearch")

    proj_name = proj_conf.parseProjectConfig()["proj_name"]
    num_currents = int(proj_conf.get_list("currents", "Simulation")[0])

    fitness_args = { "proj_conf"  : proj_conf,
                     "mode"       : mode,
                     "proj_name"  : proj_name,
                     "numCurrents": num_currents,
                   }
    for item in proj_conf.cfg.items("fitness.evaluate_param"):
        fitness_args[item[0]] = eval(item[1])
    
    l_bounds = map(eval, proj_conf.get("lower_bounds", "gridsearch").split(','))
    u_bounds = map(eval, proj_conf.get("upper_bounds", "gridsearch").split(','))
    deltas = map(eval, proj_conf.get("deltas", "gridsearch").split(','))

    logger.info("Generating exponential grid:")
    logger.info("Lower bounds: " + repr(l_bounds))
    logger.info("Upper bounds: " + repr(u_bounds))

    grid = []
    gridmode = proj_conf.get("gridmode", "gridsearch")

    if(gridmode == "linear"):
        grid = generate_linear_grid(l_bounds, u_bounds, deltas)
        logger.info("Steps (linear)" + repr(deltas))
    elif(gridmode == "exponential"):
        grid = generate_exponential_grid(l_bounds, u_bounds, deltas)
        logger.info("Steps (exponential)" + repr(deltas))
    else:
        raise RuntimeError("Invalid gridmode: " + repr(gridmode))

    gs = GridSearch(proj_conf, fitness_args)
    gs.update_grid(grid)

    logger.info("Grid search complete.")
    logger.info("Best result:" +repr(gs.best))
    
def generate_linear_grid(l_bounds, u_bounds, deltas):
    value_ranges = map(generate_steps, l_bounds, u_bounds, deltas)

    logger.info("Grid size: " + repr(reduce(operator.mul, map(len, value_ranges), 1)))

    # return cartesian product, i.e. all combinations of values
    return prodcut(*value_ranges)

#------------------------------------------------
def generate_exponential_grid(l_bounds, u_bounds, deltas):
    exp_l_bounds = map(math.log10, l_bounds)
    exp_u_bounds = map(math.log10, u_bounds)

    exp_value_ranges = map(generate_steps, exp_l_bounds, exp_u_bounds, deltas)
    value_ranges     = [map(lambda x:10**x, list(l)) for l in exp_value_ranges]

    # Special case: scalar in position 7:
    value_ranges[7] = list(generate_steps(l_bounds[7], u_bounds[7], deltas[7]))

    logger.info("Grid size: " + repr(reduce(operator.mul, map(len, value_ranges), 1)))

    # return cartesian product, i.e. all combinations of values
    return product(*value_ranges)

#------------------------------------------------
def generate_steps(l_bound, u_bound, delta):
    step = l_bound
    yield step

    while step <= u_bound:
        step = step + delta
        yield step

#------------------------------------------------
class GridSearch(object):

    #------------------------------------------------
    def __init__(self, proj_conf, fitness_args):
        self.proj_conf = proj_conf
        self.fitness_args = fitness_args

        self.queue = []
        self.best  = ([], -20000)

    #------------------------------------------------
    def update_grid(self, grid):
        for point in grid:
            self.add(point)

    #------------------------------------------------
    def add(self, point):
        self.queue.append(list(point))
        chromgen.write_channel_data(self.proj_conf)

        if len(self.queue) > QUEUESIZE:
            results = fitness.evaluate_param(self.queue, self.fitness_args)
            for i in range(len(results)):
                if results[i] > self.best[1]:
                    self.best = (queue[i], results[i])
                    logger.info("New best: " + repr(self.best))
            self.queue = []
    
