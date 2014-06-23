import sys
import argparse
import tempfile
import shutil
import time
import os.path
import subprocess
import logging
import ConfigParser

import nevo.util.logserver as logserver
import nevo.util.projconf as projconf
import nevo.algorithm.annealing as annealing
import nevo.algorithm.gridsearch as gridsearch
import nevo.algorithm.evolution as evolution

class Simulation(object):

    def __init__(self, config, temp):
        self.config_file = projconf.norm_path(config)
        self.temp = temp
        self.pconf = projconf.ProjectConfiguration(config_file = self.config_file)
        
        
        # Create and set sim_path.
        if self.temp:
            temp_path = tempfile.mkdtemp(prefix="neuron_sim-")
            self.pconf.set_sim_path(temp_path)
        else:
            result_directory = self._mk_result_directory()
            self.pconf.set_sim_path(result_directory)
        
        # Copy configurations.
        full_config = projconf.norm_path(self.pconf.sim_path, "full.cfg")
        with open(full_config, "w") as sim_config_file:
            self.pconf.cfg.write(sim_config_file)
        shutil.copy(projconf.norm_path(projconf.DEFAULT_CONFIG), self.pconf.sim_path)
        custom_config = projconf.norm_path(self.pconf.sim_path, "custom.cfg")
        shutil.copyfile(self.config_file, custom_config)
        self.pconf.set_config_file(custom_config)

        # Populate sim folder
        project_name = "Pyr_" + self.pconf.get("mode", "Simulation")
        project_path = projconf.norm_path(self.pconf.get("resources"), project_name)
        shutil.copytree(project_path, projconf.norm_path(self.pconf.sim_path, project_name))
        

    def run(self, quiet = False):
        """Runs the neuron generation and simulation.

        This may take some time, depending on the settings.
        Returns 0 if no error is encountered.
        """
        returncode = 0
        # Initialize logging.
        self.pconf.suppress_logging = quiet
        logger_server = logserver.initFileLogServer(log_file = self.pconf.get_local_path("log_server_file", "Logging"),
                                                    port = self.pconf.get_int("log_server_port", "Logging"),
                                                    file_level = self.pconf.get_int("file_log_level", "Logging"),
                                                    logger_name = "")
        logger_server.start()
        logger = self.pconf.get_logger("simulation", logger_server.port)
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
            self.pconf.log_configuration(logger)
            if self.config_file == projconf.norm_path(projconf.DEFAULT_CONFIG):
                logger.warning("The specified configuration file is the default configuration."
                               + " Please make any customization in a seperate file.")
            if self.temp:
                self._check_result_dir(logger)
            
            
            
            self.pconf.write_project_data(logger_server.port)

            # Start algorithm
            algorithm = self.pconf.get("algorithm", "Simulation")
            if algorithm == "annealing":
                annealing.start(self.pconf)
            elif algorithm == "genetic":
                evolution.start(self.pconf)
            elif algorithm == "gridsearch":
                gridsearch.start(self.pconf)
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
                                 + self.pconf.sim_path + "'"
                                 + "to the ouput directory '"
                                 + projconf.norm_path(".", self.pconf.get("result_directory")))
                returncode += 20
            finally:
                # Necessary to avoid hanging on open sockets
                logger_server.stop()
        return returncode

    #-----------------------------------------------------------
    def _mk_result_directory(self):
        (result_dir, result_prefix, result_suffix) = self.pconf.generate_path_affixes()
        return tempfile.mkdtemp(prefix = result_prefix + result_suffix + "_",
                                dir=result_dir)
    #-----------------------------------------------------------
    def _move_to_output(self, logger):
        output_directory = self._mk_result_directory()
        logger.info("Simulation directory '"
                    + self.pconf.sim_path + "', moving to output folder: " + output_directory)
        # Begin moving files
        src = self.pconf.sim_path
        names = os.listdir(src)
        for name in names:
            shutil.move(os.path.join(src, name), output_directory)

        logger.info("Moving finished.")
        try:
            shutil.rmtree(self.pconf.sim_path, ignore_errors=True)
        except:
            logger.warning("Could not delete temporary folder: '"
                           + self.pconf.sim_path + "'")

    #-----------------------------------------------------------
    def _check_result_dir(self, logger):
        """Check if result directory can be accessed before starting.
        """
        result_directory = self.pconf.get_path("result_directory")
        if not os.path.isdir(result_directory):
            try:
                os.makedirs(result_directory, 0755)
            except:
                logger.error("Cannot access or create'"
                             + result_directory
                             + "', aborting")
                raise RuntimeError("Output directory not accessable: '"
                                   + result_directory + "'")
