#fou coding=utf-8
"""Evaluate one neuron in detail using a finished simulation result.

The process consists of simulating the selected neuron,
then analyse and evaluate it. Plotting the resulst is also possible."""

import numpy
import subprocess
import os.path
import shutil
from time import time, sleep, strftime

from nevo.util.callable import parse_callable
from nevo.util import projconf
from nevo import chromgen


EVAL_PREFIX = "eval_"

def evaluate(logger, pconf, candidates, cleanup = False):
    """Returns a list containing the neuron itself and its evaluation results."""
    #pconf.invoke_neurosim(logger, type = "current", candidates = candidates, prefix = EVAL_PREFIX)
    try:
        parsed_kwargs = {"pconf" : pconf, "mode" : pconf.get("mode", "Simulation")}
        evaluator_section = pconf.get("evaluator", "Simulation")
        evaluator, parsed_kwargs = parse_callable(pconf, logger, evaluator_section, parsed_kwargs)

        # Change representation of the candidates
        chromosomes = []
        for i in range(len(candidates)):
            chromosomes.append(chromgen.channels_to_chromosome(candidates[i]))
        return evaluator(chromosomes, parsed_kwargs)
        # for i in range(len(candidates)):
        #     offset = i * int(pconf.get_list("currents", "Simulation")[0])
        #     evaluate_neuron(logger, pconf, prefix = EVAL_PREFIX, offset = offset)
        #     pass
    finally:
        if cleanup:
            dir = projconf.norm_path(pconf.get_sim_project_path(), "simulations")
            if os.path.isdir(dir):
                shutil.rmtree(dir)
