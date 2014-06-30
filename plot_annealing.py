#!/usr/bin/env python2.7
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():

    try:
        if len(sys.argv) == 2:
            file = sys.argv[1]
            print repr(file)
        else:
            print "Only filename expected as parameter."
            return 2
    except Exception as ex:
        print ex.message
        return 1

    with open(file) as f:
        data = f.read()

    data = data.split("\n")
    data = [str.split(", ") for str in  data]

    print data

    fitness = [x[0] for x in data]
    temperature = [x[1] for x in data]

    fitness = map(float, fitness)
    temperature = map(float, temperature)

    print fitness
    print temperature

    fig = plt.figure()

    fitness_plot = fig.add_subplot(121)
    fitness_plot.plot(fitness)

    fitness_plot.set_title("Simulated Annealing Fitness")
    fitness_plot.set_xlabel("Step")
    fitness_plot.set_ylabel("Fitness")

    temperature_plot = fig.add_subplot(122)
    temperature_plot.plot(temperature)

    temperature_plot.set_title("Simulated Annealing Temperature")
    temperature_plot.set_xlabel("Step")
    temperature_plot.set_ylabel("Temperature")

    plt.show()

if __name__ == "__main__":
    main()
