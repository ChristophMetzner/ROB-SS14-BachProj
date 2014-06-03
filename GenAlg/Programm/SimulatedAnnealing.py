import projConf
import fitness
import random

class Dummy:
    num_generations = 1

def start(args):
    result = SimulatedAnnealing(args).simulateAnnealing()
    
    print result

class SimulatedAnnealing(object):
    
    upper_bounds = [ -7, -7, -6, -5, -5, -5, -5, -3, -4, -3, -5, -5]
    lower_bounds = [-14,-14,-14,-14,-14,-14,-14, -5,-11, -5,-14,-15]
    fitnessArgs  = None
    
    def __init__(self, args):
        self.fitnessArgs = args
    
    def simulateAnnealing(self):
        state = self.initState()
        energy = self.calculateEnergies([state])
        
        best_state = state
        best_energy = energy
        
        step = 0
        stepmax = 3
        
        while step < stepmax:
            temperature = self.calculateTemperature(step/stepmax)
            
            new_state_candidates = self.neighbourList(state)
            new_state_energies = self.calculateEnergies(new_state_candidates)
            
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
    
    def initState(self):
        return [10**random.uniform(x,y) for (x,y) in zip(self.lower_bounds, self.upper_bounds)]
        
    def calculateEnergies(self, state_list):
        return fitness.evaluate_param(state_list, self.fitnessArgs)
        
    def calculateTemperature(self, r):
        return 1
        
    def neighbourList(self, state):
        return [self.initState()]
        
    def probability(self, energy, new_energy, temperature):
        return 0.5
    
