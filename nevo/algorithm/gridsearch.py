# coding=utf-8

import nevo.eval.fitness as fitness
import nevo.chromgen as chromgen

import math
import operator

from itertools import product

logger = None

QUEUESIZE = 100

#------------------------------------------------
def start(pconf, **args):
    mode = pconf.get("mode", "Simulation")
    global logger
    logger = pconf.get_logger("gridsearch")

    proj_name = pconf.parse_project_data()["proj_name"]
    num_currents = int(pconf.get_list("currents", "Simulation")[0])

    fitness_args = { "pconf"  : pconf,
                     "mode"       : mode,
                     "proj_name"  : proj_name,
                     "numCurrents": num_currents,
                   }
    for item in pconf.cfg.items("fitness.evaluate_param"):
        fitness_args[item[0]] = eval(item[1])
    
    (l_bounds, u_bounds, deltas) = ([], [], [])
    for channel in ["ar", "cal", "cat", "k2", "ka", "kahp", "hc", "alpha", "km", "naf", "nap", "pas"]:
        _range = map(eval, pconf.get(channel, "gridsearch").split(','))
        if len(_range) == 1:
            l_bounds.append(_range[0])
            u_bounds.append(_range[0])
            deltas.append(1)
        elif len(_range) == 3:
            l_bounds.append(_range[0])
            u_bounds.append(_range[1])
            deltas.append(_range[2])
        else:
            raise RuntimeError("Invalid parameters for channel " +repr(channel))

    grid = []
    gridmode = pconf.get("gridmode", "gridsearch")

    logger.info("Generating grid...")
    if(gridmode == "linear"):
        grid = generate_linear_grid(l_bounds, u_bounds, deltas)
    elif(gridmode == "exponential"):
        grid = generate_exponential_grid(l_bounds, u_bounds, deltas)
    else:
        raise RuntimeError("Invalid gridmode: " + repr(gridmode))

    logger.info("Generated " + gridmode + " grid:")
    logger.info("Lower bounds: " + repr(l_bounds))
    logger.info("Upper bounds: " + repr(u_bounds))
    logger.info("Steps       : " + repr(deltas))

    gs = GridSearch(pconf, fitness_args)
    best = gs.evaluate(grid)

    logger.info("Grid search complete.")
    logger.info("Best result:" +repr(best))
    
def generate_linear_grid(l_bounds, u_bounds, deltas):
    value_ranges = map(list, map(generate_steps, l_bounds, u_bounds, deltas))
    
    logger.info("Value ranges:")
    for x in value_ranges:
        logger.info(repr(x))

    logger.info("Grid size: " + repr(reduce(operator.mul, map(len, value_ranges), 1)))

    # return cartesian product, i.e. all combinations of values
    return product(*value_ranges)

#------------------------------------------------
def generate_exponential_grid(l_bounds, u_bounds, deltas):
    exp_l_bounds = map(math.log10, l_bounds)
    exp_u_bounds = map(math.log10, u_bounds)

    exp_value_ranges = map(generate_steps, exp_l_bounds, exp_u_bounds, deltas)
    value_ranges     = [map(lambda x:10**x, list(l)) for l in exp_value_ranges]

    # Special case: scalar in position 7:
    value_ranges[7] = list(generate_steps(l_bounds[7], u_bounds[7], deltas[7]))

    logger.info("Value ranges:")
    for x in value_ranges:
        logger.info(repr(x))

    logger.info("Grid size: " + repr(reduce(operator.mul, map(len, value_ranges), 1)))

    # return cartesian product, i.e. all combinations of values
    return product(*value_ranges)

#------------------------------------------------
def generate_steps(l_bound, u_bound, delta):
    while l_bound <= u_bound:
        yield l_bound
        l_bound += delta

#------------------------------------------------
class GridSearch(object):

    #------------------------------------------------
    def __init__(self, pconf, fitness_args):
        self.pconf = pconf
        self.fitness_args = fitness_args
        self.outfile = pconf.local_path("grid.csv")

        self.queue = []
        self.best  = ([], -20000)

    #------------------------------------------------
    def evaluate(self, grid):
        for point in grid:
            self.add(point)
        self.update()
        return self.best

    #------------------------------------------------
    def add(self, point):
        self.queue.append(list(point))

        if len(self.queue) > QUEUESIZE:
            results = fitness.evaluate_param(self.queue, self.fitness_args)
            with open(self.outfile, "a") as outfile:
                for i in range(len(results)):
                    outfile.write(self.queue[i] + ", " + results[i])
                    if results[i] > self.best[1]:
                        self.best = (queue[i], results[i])
            self.queue = []

   #------------------------------------------------
    def update(self):
        results = fitness.evaluate_param(self.queue, self.fitness_args)
        for i in range(len(results)):
            logger.info(repr((self.queue[i], results[i])))
            if results[i] > self.best[1]:
                self.best = (self.queue[i], results[i])
                logger.info("New best: " + repr(self.best))
        self.queue = []
