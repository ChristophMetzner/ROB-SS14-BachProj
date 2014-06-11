import projConf
import fitness
import random

class Dummy:
    num_generations = 1

def start(proj_conf, **args):
    algorithm = SimulatedAnnealing(proj_conf, **args)
    result = algorithm.simulate_annealing()
    
    algorithm.logger.debug(repr(result))

class SimulatedAnnealing(object):
    
    upper_bounds = [ -7, -7, -6, -5, -5, -5, -5, -3, -4, -3, -5, -5]
    lower_bounds = [-14,-14,-14,-14,-14,-14,-14, -5,-11, -5,-14,-15]
    fitness_args = None
    proj_conf = None
    logger = None
    
    def __init__(self, proj_conf, **args):
        self.proj_conf = proj_conf
        self.logger = self.proj_conf.getClientLogger("simulatedAnnealing")

        # Pass proj_conf on to fitness.
        args["proj_conf"] = proj_conf
        self.fitness_args = args
    
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
        return [10**random.uniform(x,y) for (x,y) in zip(self.lower_bounds, self.upper_bounds)]
        
    def calculate_energies(self, state_list):
        return fitness.evaluate_param(state_list, self.fitness_args)
        
    def calculate_temperature(self, r):
        return 1
        
    def neighbourList(self, state):
        return [self.init_state()]
        
    def probability(self, energy, new_energy, temperature):
        return 0.5
    
