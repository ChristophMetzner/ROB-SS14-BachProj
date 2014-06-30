# coding=utf-8

from __future__ import division
import random
import math

import nevo.util.projconf as projconf
import nevo.eval.fitness as fitness
import nevo.chromgen as chromgen

class Dummy:
    num_generations = 1

def start(pconf, **args):
    algorithm = SimulatedAnnealing(pconf, **args)
    result = algorithm.simulate_annealing()

    algorithm.logger.info(repr(result))

#-----------------------------------------------------------
class SimulatedAnnealing(object):

    logger = None
    mode = None
    pconf = None
    fitness_args = None
    output_file = None

    stepmax = None
    step = None
    start_temperature = None
    cooling_schedule = None
    cooling_schedule_alpha = None
    neighbour_count = None

    #-----------------------------------------------------------
    def __init__(self, pconf, **args):

        self.mode = pconf.get("mode", "Simulation")

        self.pconf = pconf
        self.logger = self.pconf.get_logger("annealing")
        self.fitness_args = {"pconf": pconf, "mode": self.mode}
        self.output_file = pconf.local_path("statistics.csv")

        # Parameters for fitness evaluation
        self.parsed_kwargs = {}
        for item in pconf.cfg.items("fitness.evaluate_param"):
            self.parsed_kwargs[item[0]] = eval(item[1])
        numCurrents = int(pconf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["numCurrents"] = int(pconf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["proj_name"] = pconf.parse_project_data()["proj_name"]
        self.fitness_args.update(self.parsed_kwargs)

        # Parameters for simulated annealing algorithm
        self.stepmax = pconf.get_int("stepmax", "annealing")
        self.start_temperature = pconf.get_int("start_temperature", "annealing")
        self.cooling_schedule = pconf.get("cooling_schedule", "annealing")
        self.cooling_schedule_alpha = pconf.get_float("cooling_schedule_alpha", "annealing")
        self.neighbour_count = pconf.get_int("neighbour_count", "annealing")

    #-----------------------------------------------------------
    def simulate_annealing(self):
        state = self.init_state()
        energy = self.calculate_energies([state])[0]

        best_state = state
        best_energy = energy
        self.logger.info("Starting with state " + str(state) + " and energy " + str(energy))

        self.step = 0
        temperature = self.start_temperature

        if self.cooling_schedule_alpha >= 1 or self.cooling_schedule_alpha <= 0:
            self.cooling_schedule_alpha = 0.9
            self.logger.info("Cooling schedule alpha out of range, set to 0.9")

        while self.step < self.stepmax:

            new_state_candidates = self.neighbour_list(state, self.neighbour_count)
            new_state_energies = self.calculate_energies(new_state_candidates)

            for i in range(len(new_state_candidates)):

                if self.step >= self.stepmax:
                    break

                self.step = self.step + 1

                self.logger.info("Beggining step " + str(self.step) + " of " + str(self.stepmax))
                temperature = self.calculate_temperature(self.step / self.stepmax)
                self.logger.info("New temperature is " + str(temperature))

                with open(self.output_file, "a") as file:
                    if self.step > 1:
                        file.write("\n")
                    file.write(str(energy) + ", " + str(temperature) + ", " + str(state))

                if(self.probability(energy, new_state_energies[i], temperature) > random.random()):
                    state = new_state_candidates[i]
                    energy = new_state_energies[i]
                    self.logger.info("New state with energy " + str(energy) + " accepted")
                    break
                else:
                    self.logger.info("New state with energy " + str(new_state_energies[i]) + " NOT accepted")

            if energy > best_energy:
                best_state = state
                best_energy = energy

        return (best_state, best_energy)

    #-----------------------------------------------------------
    def init_state(self):

        chromosome = chromgen.generate_chromosome(random, self.fitness_args)
        return chromosome

    #-----------------------------------------------------------
    def calculate_energies(self, state_list):
        return fitness.evaluate_param(state_list, self.fitness_args)

    #-----------------------------------------------------------
    def calculate_temperature(self, r):

        if self.cooling_schedule == "exponential":
            temperature = self.start_temperature * pow(self.cooling_schedule_alpha, self.step)

        else:
            temperature = (1 - r) * self.start_temperature

        return temperature

    #-----------------------------------------------------------
    def neighbour_list(self, state, number):

        neighbours = []

        for i in range(0, number):
            neighbours.append(self.get_neighbour(state))

        return neighbours

    #-----------------------------------------------------------
    def get_neighbour(self, state):

        # Select an allele to change
        allele = random.randint(0, 10)

        if self.mode == "RS":
            while allele in [1, 2]:
                allele = random.randint(0, 10)

        if self.mode == "FS":
            while allele in [1, 2, 5, 8]:
                allele = random.randint(0, 10)

        # Random values determining the new value of the allele
        r_1 = random.random()
        r_2 = random.random()

        if r_1 < 0.5:
            new_value = ((chromgen.get_bounds(self.mode)[1])[allele] - state[allele]) * r_2
        else:
            new_value = (state[allele] - (chromgen.get_bounds(self.mode)[1])[allele]) * r_2

        state[allele] = new_value

        self.logger.info("Changing allele " + str(allele) + " to " + str(state[allele]))

        chromgen.write_channel_data(self.pconf)
        return state

    #-----------------------------------------------------------
    def probability(self, energy, new_energy, temperature):

        if new_energy >= energy:
            probability = 1

        else:
            probability = math.exp(-(energy - new_energy) / temperature)

        self.logger.info("Accepting probability: " + str(probability))

        return probability

