#!/usr/bin/env python2.7
# coding=utf-8
import logging
import sys
import argparse
import tempfile
import shutil
import time
import os.path

sys.path.append("./GenAlg/Programm/")

import main_program
import logServer
import logClient
import projConf
import ConfigParser
import simulatedAnnealing

def move_to_output(proj_conf, logger):
    logger.info("Simulation directory '"
                + proj_conf.sim_path + "', moving to output folder...")
    output_directory = proj_conf.generate_output_path()
    shutil.copytree(proj_conf.sim_path, output_directory)
    logger.info("Moved result to '" + output_directory + "'")
    try:
        shutil.rmtree(proj_conf.sim_path, ignore_errors=True)
    except:
        logger.warning("Could not delete temporary folder: '"
                       + proj_conf.sim_path + "'")

#-----------------------------------------------------------
def check_result_dir(proj_conf, logger):
    """Check if result directory can be accessed before starting.
    """
    result_directory = proj_conf.getPath("result_directory")
    if not os.path.isdir(result_directory):
        try:
            os.makedirs(result_directory, 0755)
        except:
            logger.error("Cannot access or create'"
                         + result_directory
                         + "', aborting")
            raise RuntimeError("Output directory not accessable: '"
                               + result_directory + "'")

#-----------------------------------------------------------    
def main():
    parser = argparse.ArgumentParser(description="Optimize conductance of"
                                     + " ion channels for computer modelled neuron cells.")
    parser.add_argument("config",
                        nargs=1,
                        help="Path to the configuration file defining the parameters for this run")
    parser.add_argument("-t", "--temp",
                        action='store_true', dest="temp",
                        help="Create a temporary working directory in which all processing"
                        + " should take place. Results will be copied to result_directory specified in the config)")
    parser.add_argument("-a", "--algorithm", dest="algorithm",
                        choices=["genetic", "annealing"], default="genetic",
                        help="The algorithm used to generate the parameters for the target neuron.")
    args = parser.parse_args()


    config_file = projConf.normPath(args.config[0])
    
    proj_conf = projConf.ProjConf(config_file=config_file)
    if args.temp:
        temp_path = tempfile.mkdtemp(prefix="neuron_sim-")
        proj_conf.set_sim_path(temp_path)
    else:
        output_directory = proj_conf.sim_path
        os.makedirs(output_directory, 0755)
    
    try:
        start_time = time.time()

        logger_server = logServer.initFileLogServer(proj_conf.getLocalPath("log_server_file", "Logging"),
                                                int(proj_conf.get("log_server_port", "Logging")),
                                                int(proj_conf.get("log_server_level", "Logging")))
        logger_server.start()
        logger = proj_conf.getClientLogger("multiEA")

        logger.info("          =============================================")
        logger.info("          =============================================")
        logger.info("          =======    Starting new Simulation    =======")
        logger.info("          =============================================")
        logger.info("          =============================================")
        logger.info("Configuration used:")
        proj_conf.logConfig(logger)
        if config_file == projConf.normPath(projConf.DEFAULT_CONFIG):
            logger.warning("The specified configuration file is the default configuration."
                           + " Please make any customization in a seperate file.")
        print
        if args.temp:
            check_result_dir(proj_conf, logger)
        
        
        # Populate sim folder
        project_name = "Pyr_" + eval(proj_conf.get("mode", "Simulation Parameters"))
        project_path = projConf.normPath(project_name)
        shutil.copytree(project_path, projConf.normPath(proj_conf.sim_path, project_name))
        shutil.copyfile(config_file, projConf.normPath(proj_conf.sim_path, "custom.cfg"))
        shutil.copy(projConf.normPath(projConf.DEFAULT_CONFIG), proj_conf.sim_path)

        # Start algorithm
        kwargs = {}
        for item in proj_conf.cfg.items("Simulation Parameters"):
                kwargs[item[0]] = eval(item[1])
        
        if args.algorithm == "annealing":
            simulatedAnnealing.start(proj_conf, **kwargs)
        elif args.algorithm == "genetic":
            main_program.start(proj_conf, **kwargs)
        else:
            raise RuntimeError("Unhandled algorithm selected.")

        stop_time = time.time()
        logger.info("Time passed: " + str(stop_time - start_time) + " seconds")
    except Exception, e:
        logger.exception("Exception encountered, aborting.")
    finally:
        try:
            if args.temp:
                # Log messages after this are likely to be never saved.
                move_to_output(proj_conf, logger)
        except:
            logger.exception("Failed to move simulation folder '"
                             + proj_conf.sim_path + "'"
                             + "to the ouput directory '"
                             + projConf.normPath(".", proj_conf.get("result_directory")))
            sys.exit(1)
        finally:
            # Necessary to avoid hanging on open sockets
            logging.shutdown()

#-----------------------------------------------------------
if __name__ == "__main__":
    main()
