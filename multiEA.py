#! usr/local/lib/python2.7 python
# coding=utf-8

import sys
#sys.path.append("C:\Python27\GenAlg\Programm")
sys.path.append("./GenAlg/Programm/")

import profiler
import main_program


profiler.startTimer()

#Datei zum Ausführen mehrerer genetischer Algorithmen nacheinander mit:
# -> nichts notwendig, alles optional, sollte aber zusammenpassen!
#       OPT-Parameter:          Defaults:
# main_program.start(
            # proj_name         = "Pyr_RS",
            # sim_config        = "Default Simulation Configuration,
            # stimulation       = "Input_0",
            # cell              = "L5TuftedPyrRS",
            # duration          = 500,
            # dt                = 0.05,
            # currents          = [3,0.1,0.3],  #list [num, start, step]
        # for GA:
            # pop_size          = 50,
            # max_generations   = 30,
            # thrFourier        = 5,
            # penFourier        = -10000,
            #p_ai_RS            = -3500,
            #p_ai_FS            = -3500,
            #p_ibf_IB           = -2500,
            #p_ibf_CH           = -3500,
            #p_ir_IB            = -3500,
            #p_ir_CH            = -2500,
            #num_selected       = pop_size,
            #num_co_points      = 1,
            #mutation_strength  = 0.4
            #num_elites         = 1,
            #tournament_size    = 2,
            # mode:
                 # proj_name = pyr_RS: 1
                 # proj_name = pyr_IB: 3
                 # another project: please choose one mode:  1:RS, 2:FS, 3:IB, 4:CH

            # crossover_rate    = 1,
            # weights           = [1,1,1,1,1],  #List [apw, ibf, ir, ai, slope]
            # custom            = 0,    0: nein,1: ja (replacement, selection)
            # show              = 1             # Dokumentation des Verlaufs?
            #):


main_program.start(pop_size=4,
                   max_generations=2,
                   proj_name = "Pyr_RS",
                   mode = 1,
                   dt = 0.025,
                   num_selected = 4,
                   tournament_size = 4,
                   num_co_points = 2,
                   #crossover_rate = 0.25,
                   custom = 1,
                   #thrFourier = 4,
                   #penFourier = -10000, # an FS anpassen (groesser)
                   currents = [3,0.2,0.3],
                   mutation_strength = 0.15)# ... do something ...

# main_program.start(pop_size=50,
#                    max_generations=60,
#                    proj_name = "Pyr_IB",
#                    mode = 4,
#                    dt = 0.025,
#                    num_selected = 40,
#                    tournament_size = 5,
#                    num_co_points = 2,
#                    crossover_rate = 0.25,
#                    custom = 1,
#                    #thrFourier = 4,
#                    #penFourier = -10000, # an FS anpassen (groesser)
#                    currents = [3,0.2,0.3],
#                    mutation_strength = 0.05)

#main_program.start(    pop_size=50,
          #max_generations=60,
          #proj_name = "Pyr_RS",
          #mode = 1,
          #dt = 0.025,
          #num_selected = 40,
          #tournament_size = 5,
          #num_co_points = 2,
          #crossover_rate = 0.25,
          #custom = 1,
          #thrFourier = 4,
          #penFourier = -10000, # an FS anpassen (groesser)
          #currents = [3,0.2,0.3],
          #mutation_strength = 0.05)


profiler.printStats()
profiler.stopTimer()
