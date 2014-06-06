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

DEFAULT_CONFIG_NAME = "settings.cfg"




def copyToOutput(proj_conf, logger):
    logger.info("Simulation directory '"
                + proj_conf.sim_path + "' used, moving to output folder...")
    output_path = projConf.normPath(".", proj_conf.get("result_directory"),
                                    time.strftime("%Y-%m-%d_%H-%M-%S-result"))
    shutil.copytree(proj_conf.sim_path, output_path)
    logger.info("Moved result to '" + output_path + "'")

def checkOutputDir(proj_conf, logger):
    """Check if result directory can be accessed before starting.
    """
    result_directory = projConf.normPath(".", proj_conf.get("result_directory"))
    if not os.path.isdir(result_directory):
        try:
            os.mkdir(result_directory, 0755)
        except:
            logger.error("Cannot access or create'"
                         + result_directory
                         + "', aborting")
            raise RuntimeError("Output directory not accessable: '"
                               + result_directory + "'")
    
def main():
    parser = argparse.ArgumentParser(description="Optimize conductance of"
                                     + " ion channels for computer modelled neuron cells.")
    parser.add_argument("-c", "--config",
                        required=True, nargs=1,
                        help="Path to the configuration file defining the parameters for this run")
    parser.add_argument("-n", "--no-temp",
                        action='store_false', dest="temp",
                        help="Do not create a temporary working directory in which all processing"
                        + " should take place. Results will be copied to result_directory (config)")
    args = parser.parse_args()


    config_file = projConf.normPath(args.config[0])
    if args.temp:
        sim_path = tempfile.mkdtemp(prefix="neuron_sim-")
        shutil.copyfile(config_file, projConf.normPath(sim_path, DEFAULT_CONFIG_NAME))
        config_file = projConf.normPath(sim_path, DEFAULT_CONFIG_NAME)
    else:
        sim_path = projConf.normPath(".")
    
    proj_conf = projConf.ProjConf(config_file=config_file, sim_path=sim_path)
    server = logServer.initFileLogServer(proj_conf.getLocalPath("log_server_file", "Logging"),
                                         int(proj_conf.get("log_server_port", "Logging")),
                                         int(proj_conf.get("log_server_level", "Logging")))
    server.start()
    logger = proj_conf.getClientLogger("multiEA")
    checkOutputDir(proj_conf, logger)
    
    if args.temp:
        # Populate temp folder
        project_name = "Pyr_" + eval(proj_conf.get("mode", "GenAlgParameters"))
        project_path = projConf.normPath(project_name)
        shutil.copytree(project_path, projConf.normPath(proj_conf.sim_path, project_name))

    try:
        start_time = time.time()
        logger.info("          =============================================")
        logger.info("          =============================================")
        logger.info("          =======    Starting new Simulation    =======")
        logger.info("          =============================================")
        logger.info("          =============================================")
        logger.info("Configuration used:")
        proj_conf.logConfig(logger)

        kwargs = {}
        for item in proj_conf.cfg.items("GenAlgParameters"):
                kwargs[item[0]] = eval(item[1])
        main_program.start(proj_conf, **kwargs)

        stop_time = time.time()
        logger.info("Time passed: " + str(stop_time - start_time) + " seconds")
    except Exception, e:
        logger.exception("Exception encountered, aborting.")
    finally:
        try:
            # Log messages after this are likely to be never saved.
            copyToOutput(proj_conf, logger)
            if args.temp:
                try:
                    shutil.rmtree(proj_conf.sim_path, ignore_errors=True)
                except:
                    logger.warning("Could not delete temporary folder: '"
                                   + proj_conf.sim_path + "'")
        except:
            logger.exception("Failed to move simulation folder '"
                             + sim_path + "'"
                             + "to the ouput directory '"
                             + projConf.normPath(".", proj_conf.get("result_directory")))
            sys.exit(1)
        finally:
            # Necessary to avoid hanging on open sockets
            logging.shutdown()
        


if __name__ == "__main__":
    main()
