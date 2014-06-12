# coding=utf-8

import projConf
import fitness
import random
import chromgen

class Dummy:
    num_generations = 1

def start(proj_conf, **args):
    algorithm = SimulatedAnnealing(proj_conf, **args)
    result = algorithm.simulate_annealing()

    algorithm.logger.debug(repr(result))

class SimulatedAnnealing(object):

    u_bound = None
    l_bound = None
    logger = None
    mode = None
    proj_conf = None
    fitness_args = None
    parsed_kwargs = None

    def __init__(self, proj_conf, **args):

        self.mode = proj_conf.get("mode", "Simulation")

        if self.mode  == "RS":
            # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
            u_bound = [10**x for x in [ -7, -7, -6, -5, -5, -5, -5, -3, -4, -3, -5, -5]]
            l_bound = [10**x for x in [-14,-14,-14,-14,-14,-14,-14, -5,-11, -5,-14,-15]]
        elif self.mode == "FS":
            # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
            u_bound = [10**x for x in [ -7, -7, -6, -5, -5, -9, -5, -3, -6, -3, -5, -5]]
            l_bound = [10**x for x in [-14,-14,-14,-14,-14,-11,-14, -5, -8, -5,-14,-15]]
        elif self.mode == "CH":
            # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
            u_bound = [10**x for x in [ -7, -9, -7, -5, -5, -5, -5, -3, -7, -3, -5, -5]]
            l_bound = [10**x for x in [-14,-12,-12,-12,-12,-12,-12, -4,-11, -5,-12,-13]]
        else:
            # Values are:               ar cal cat  k2  ka kahp kc kdr  km naf nap pas
            u_bound = [10**x for x in [ -7, -9, -7, -5, -5, -5, -5, -3, -7, -3, -5, -5]]
            l_bound = [10**x for x in [-14,-12,-12,-12,-12,-12,-12, -4,-11, -5,-12,-13]]

        self.proj_conf = proj_conf
        self.logger = self.proj_conf.getClientLogger("simulatedAnnealing")
        self.fitness_args = { "proj_conf": proj_conf, "mode": self.mode}

        self.parsed_kwargs = {}
        for item in proj_conf.cfg.items("fitness_evaluate_param"):
            self.parsed_kwargs[item[0]] = eval(item[1])
        numCurrents = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["numCurrents"] = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["proj_name"] = proj_conf.parseProjectConfig()["proj_name"],

        self.fitness_args.update(self.parsed_kwargs)

        print self.fitness_args

    def simulate_annealing(self):
        state = self.init_state()
        energy = self.calculate_energies([state])

        best_state = state
        best_energy = energy

        step = 0
        stepmax = 3

        while step < stepmax:
            temperature = self.calculate_temperature(step/stepmax)

            new_state_candidates = self.neighbourList(state)
            new_state_energies = self.calculate_energies(new_state_candidates)

            for i in range(len(new_state_candidates)):
                if(self.probability(energy, new_state_energies[i], temperature) > random.random()):
                    state = new_state_candidates[i]
                    energy = new_state_energies[i]
                    break

            if energy > best_energy:
                best_state = state
                best_energy = energy

            step = step + 1

        return (best_state, best_energy)

    def init_state(self):
        chromosome = chromgen.generate_conductance(random, self.fitness_args)

        chromosome[11] = 0.00002

        if self.mode == "RS" or self.mode == "FS":
            chromosome[1] = 0
            chromosome[2] = 0

        if self.mode == "FS":
            chromosome[5] = 0
            chromosome[8] = 0

            if (chromosome[9] / chromosome[7]) > 1 or (chromosome[9] / chromosome[7]) < (1/2):
                chromosome[7] = 1.5 * chromosome[9]

        elif (chromosome[9] / chromosome[7]) > 2 or (chromosome[9] / chromosome[7]) < (2/3):
            chromosome[7] = chromosome[9]

        chromgen.calc_dens(chromosome, None, self.fitness_args)

        return chromosome

    def calculate_energies(self, state_list):
        return fitness.evaluate_param(state_list, self.fitness_args)

    def calculate_temperature(self, r):
        return 1

    def neighbourList(self, state):

        allele = random.randint(0,10)

        if self.mode == "RS":
            while allele in [1,2]:
                allele = random.randint(0,10)

        if self.mode == "FS":
            while allele in [1,2,5,8]:
                allele = random.randint(0,10)

        r_1 = random.random()
        r_2 = random.random()

        if r_1 < 0.5:
            new_value = (self.u_bound[allele] - state[allele]) * r_2

        else:
            new_value = (state[allele] - self.l_bound[allele]) * r_2

        ### TODO: Verhältnis auf Grenzen setzen
        """
        if self.mode == "FS":
            if (state[9] / state[7]) > 1:
                if allele == 9:

            elif (state[9] / state[7]) < (1/2):
                state[7] = 1.5 * state[9]

        elif (state[9] / state[7]) > 2 or (state[9] / state[7]) < (2/3):
            state[7] = state[9]
        """

        return [self.init_state()]

    def probability(self, energy, new_energy, temperature):
        return 0.5

