import sys
import argparse
import tempfile
import shutil
import time
import os.path
import subprocess
import logging

import main_program
import logServer
import logClient
import projConf
import ConfigParser
import simulatedAnnealing
import copytree

class Simulation(object):

    def __init__(self, config, temp):
        self.config_file = projConf.normPath(config)
        self.temp = temp
        self.proj_conf = projConf.ProjConf(config_file = self.config_file)
        
        
        # Create and set sim_path.
        if self.temp:
            temp_path = tempfile.mkdtemp(prefix="neuron_sim-")
            self.proj_conf.set_sim_path(temp_path)
        else:
            result_directory = self._mk_result_directory()
            self.proj_conf.set_sim_path(result_directory)
        
        # Copy configurations.
        full_config = projConf.normPath(self.proj_conf.sim_path, "full.cfg")
        with open(full_config, "w") as sim_config_file:
            self.proj_conf.cfg.write(sim_config_file)
        shutil.copy(projConf.normPath(projConf.DEFAULT_CONFIG), self.proj_conf.sim_path)
        custom_config = projConf.normPath(self.proj_conf.sim_path, "custom.cfg")
        shutil.copyfile(self.config_file, custom_config)
        self.proj_conf.set_config_file(custom_config)

        # Populate sim folder
        project_name = "Pyr_" + self.proj_conf.get("mode", "Simulation")
        project_path = projConf.normPath(project_name)
        shutil.copytree(project_path, projConf.normPath(self.proj_conf.sim_path, project_name))
        

    def run(self, quiet = False):
        """Runs the neuron generation and simulation.

        This may take some time, depending on the settings.
        Returns 0 if no error is encountered.
        """
        returncode = 0
        # Initialize logging.
        self.proj_conf.suppress_logging = quiet
        logger_server = logServer.initFileLogServer(log_file = self.proj_conf.get_local_path("log_server_file", "Logging"),
                                                    port = self.proj_conf.get_int("log_server_port", "Logging"),
                                                    file_level = self.proj_conf.get_int("file_log_level", "Logging"),
                                                    logger_name = "")
        logger_server.start()
        logger = self.proj_conf.getClientLogger("start_sim", logger_server.port)
        try:
            start_time = time.time()
            logger.info("          =============================================")
            logger.info("          =============================================")
            logger.info("          =======    Starting new Simulation    =======")
            logger.info("          =============================================")
            logger.info("          =============================================")
            version = subprocess.check_output(["git", "describe", "--always"])
            logger.info("Git project version: " + version.strip())
            logger.info
            logger.info("Configuration used:")
            self.proj_conf.logConfig(logger)
            if self.config_file == projConf.normPath(projConf.DEFAULT_CONFIG):
                logger.warning("The specified configuration file is the default configuration."
                               + " Please make any customization in a seperate file.")
            if self.temp:
                self._check_result_dir(logger)
            
            
            
            self.proj_conf.write_project_config(logger_server.port)

            # Start algorithm
            algorithm = self.proj_conf.get("algorithm", "Simulation")
            if algorithm == "annealing":
                simulatedAnnealing.start(self.proj_conf)
            elif algorithm == "genetic":
                main_program.main(self.proj_conf)
            else:
                raise RuntimeError("Unknown algorithm selected: '" + algorithm + "'")

            stop_time = time.time()
            logger.info("Time passed: " + str(stop_time - start_time) + " seconds")
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            logger.exception("Exception encountered, aborting.")
            returncode = 10
        finally:
            try:
                if self.temp:
                    # Log messages after this are likely to be never saved.
                    self._move_to_output(logger)
            except:
                logger.exception("Failed to move simulation folder '"
                                 + self.proj_conf.sim_path + "'"
                                 + "to the ouput directory '"
                                 + projConf.normPath(".", self.proj_conf.get("result_directory")))
                returncode += 20
            finally:
                # Necessary to avoid hanging on open sockets
                logger_server.stop()
        return returncode

    #-----------------------------------------------------------
    def _mk_result_directory(self):
        (result_dir, result_prefix, result_suffix) = self.proj_conf.generate_path_affixes()
        return tempfile.mkdtemp(prefix = result_prefix + result_suffix + "_",
                                dir=result_dir)
    #-----------------------------------------------------------
    def _move_to_output(self, logger):
        logger.info("Simulation directory '"
                    + self.proj_conf.sim_path + "', moving to output folder...")
        output_directory = self._mk_result_directory()
        copytree.copytree(self.proj_conf.sim_path, output_directory)
        logger.info("Moved result to '" + output_directory + "'")
        try:
            shutil.rmtree(self.proj_conf.sim_path, ignore_errors=True)
        except:
            logger.warning("Could not delete temporary folder: '"
                           + self.proj_conf.sim_path + "'")

    #-----------------------------------------------------------
    def _check_result_dir(self, logger):
        """Check if result directory can be accessed before starting.
        """
        result_directory = self.proj_conf.get_path("result_directory")
        if not os.path.isdir(result_directory):
            try:
                os.makedirs(result_directory, 0755)
            except:
                logger.error("Cannot access or create'"
                             + result_directory
                             + "', aborting")
                raise RuntimeError("Output directory not accessable: '"
                                   + result_directory + "'")
