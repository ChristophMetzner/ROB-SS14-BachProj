#!/usr/bin/env python2.7
# coding=utf-8
import sys
sys.path.append("./GenAlg/Programm/")

import simulatedAnnealing
import projConf

kwargs = {}
for item in projConf.cfg.items("GenAlgParameters"):
        kwargs[item[0]] = eval(item[1])

simulatedAnnealing.start(kwargs)
