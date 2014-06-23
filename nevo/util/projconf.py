# coding=utf-8

from __future__ import with_statement

import subprocess
import os.path
import sys
import ConfigParser
import time
import StringIO
import errno

import logclient

DEFAULT_CONFIG = "default.cfg"

class ProjectConfiguration(object):
    cfg = None
    sim_path = None
    config_file = None
    suppress_logging = False
    logger_dict = None
    unrecognized_options = None

    # Stores section:key pairs describing the unknown options for logging.
    def __init__(self, config_file, sim_path = None):
        """Initializes this module to use a specific configuration file

        config_file is the path to the configuration file.
        sim_path sets the project directory in which the simulations
        will take place and is generated if None, but not written or
        created in any form.
        """
        self.logger_dict = {}
        self.unrecognized_options = {}
        self.config_file = config_file
        self._parse_config_file(DEFAULT_CONFIG, self.config_file)

        if sim_path is None:
            self.sim_path = None
        else:
            self.sim_path = norm_path(sim_path)
    #-----------------------------------------------------------
    def get(self, key, section = None):
        """Returns the value stored in the config.

        Raises an exception if not found.
        The default section is "Global".
        See getd() for a non throwing version.
        """
        if section is None: section = "Global"
        return self.cfg.get(section, key)
    #-----------------------------------------------------------
    def get_int(self, key, section = None):
        """Syntactic sugar for int(get(...))
        """
        return int(self.get(key, section))
    #-----------------------------------------------------------
    def get_float(self, key, section = None):
        """Syntactic sugar for float(get(...))
        """
        return float(self.get(key, section))
    #-----------------------------------------------------------
    def get_list(self, key, section = "Global"):
        """Parses value as comma separated list and returns the
        list of strings
        """
        string = self.get(key, section).strip()
        l = string.lstrip("[").rstrip("]").split(",")
        return [i.strip() for i in l]
    #-----------------------------------------------------------
    def getd(self, key, section = None, default = None):
        """Returns the value stored in the config or the default.

        See get() for a throwing version.
        """
        if section is None: section = "Global"
        if self.cfg.has_option(section, key):
            return self.cfg.get(section, key)
        return default
    #-----------------------------------------------------------
    def getd_int(self, key, section = None, default = 0):
        """Syntactic sugar for int(getd(...))
        """
        return int(self.getd(key, section, default))
    #-----------------------------------------------------------
    def getd_float(self, key, section = None, default = 0.0):
        """Syntactic sugar for float(getd(...))
        """
        return int(self.getd(key, section, default))
    #-----------------------------------------------------------
    def get_path(self, key, section = None):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current working directory,
        not the sim_path. Use get_local_path() for a variant
        relative to the simulation directory.
        """
        return norm_path(self.get(key, section))

    #-----------------------------------------------------------
    def get_local_path(self, key, section = None):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current sim_path for this
        function. Use get_path() for a variant relative to the
        script invokation.
        """
        return self.local_path(self.get(key, section))
    #-----------------------------------------------------------
    def local_path(self, *args):
        """Returns a normalized path, with the concatenated
        args. 

        Takes one or several node names or relative paths
        and assumes they are local to the simulation directory
        for this run (maybe a temporary directory).
        NOTE: when an absolute path is given, all relative paths
        before are ignored.
        """
        return norm_path(self.sim_path, *args)

    #-----------------------------------------------------------
    def generate_path_affixes(self):
        """Generates a timestamped path string, but does not create any directories.
        """
        prefix = time.strftime("%Y-%m-%d_%H-%M-%S_")
        suffix = self.getd("result_affix", default="result")
        result_path = norm_path(self.get_path("result_directory"))
        return (result_path, prefix, suffix)
    #-----------------------------------------------------------
    def set_sim_path(self, sim_path):
        """Changes the sim_path in which the simulations should run.

        NOTE: Changing this variable after starting the simulation
        should NEVER be done, as other modules depend on this path
        containing buffer and project files
        """
        self.sim_path = norm_path(sim_path)
    #-----------------------------------------------------------
    def set_config_file(self, config_file):
        """Changes the config_file in which will be propagated be
        passed on neuroConstruct invocation.

        NOTE: Changing this variable after starting the simulation
        should NEVER be done, as other modules depend on this file
        remaining unchanged.
        """
        self.config_file = norm_path(config_file)
    #-----------------------------------------------------------
    def parse_project_data(self):
        values = {}
        filename = self.get_local_path("projectConfig")
        with open(filename, 'r') as config:
            c = 0 #counter
            for line in config:
                line = line.strip()
                c = c+1
                if c == 1:
                    values.update(proj_name = line)
                elif c == 2:
                    values.update(proj_path = line)
                elif c == 3:
                    values.update(log_server_port = int(line))
        return values
    #-----------------------------------------------------------
    def write_project_data(self, log_server_port):
        proj_name = "Pyr_" + self.get("mode", "Simulation")
        proj_path = proj_name + "/" + proj_name + ".ncx"
        filename = self.get_local_path("projectConfig")
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError, exception:
            if exception.errno != errno.EEXIST:
                raise
        with open(filename, "w") as config:
            config.write(str(proj_name) + "\n"
                         + str(proj_path) + "\n"
                         + str(log_server_port) + "\n")
    #-----------------------------------------------------------
    def parse_index_file(self):
        """Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!"""
        filenameIndex = self.get_local_path("candidateIndex")
        with open(filenameIndex, "r") as indexFile:
            idx = []
            val = 0
            for line in indexFile:
                try:    
                    val=int(line.strip())
                    idx.append(val)
                except:
                    pass
            return idx
    #-----------------------------------------------------------
    def invoke_neurosim(self, logger, type, max_retry = 2):
        """Invokes neuroConstruct.

        type is the string passed to neurosim.py as the --type parameters.
        """
        max_retry = max(0, int(max_retry))
        command = [os.path.join(self.get("installPath", "NeuroConstruct"), "nC.sh"),
                   "-python", norm_path("nevo/neurosim.py"),
                   "--config", self.config_file,
                   "--sim-directory", self.sim_path,
                   "--type", type]
        for i in range(max_retry + 1):
            if self.suppress_logging:
                with open(os.devnull, "w") as fnull:
                    result = subprocess.call(command, stdout = fnull, stderr = fnull)
            else:
                result = subprocess.call(command)
            # Check if call was successful and exit if true.
            if result == 0:
                return
            else:
                logger.error("Invoking neuroConstruct failed. (Code: "
                             + str(result) + ")")
        raise RuntimeError("Invoking neuroConstruct with neurosim.py failed "
                           + str(max_retry + 1) + " time(s).")
    #-----------------------------------------------------------
    def get_logger(self, logger_name, log_server_port = None):
        """Wrapper for the logclient.initClientLogger method.

        Since the configuration is normally accessed with this class,
        the logger is easily configured using this helper method.
        """
        if logger_name not in self.logger_dict:
            if log_server_port is None:
                log_server_port = self.parse_project_data()["log_server_port"]

            kwargs = {"log_server_port" : log_server_port,
                      "console_level" : self.get_int("console_log_level", "Logging"),
                      "suppress_console_output" : self.suppress_logging,
                      "log_server_level" : min(self.get_int("file_log_level", "Logging"),
                                               self.get_int("console_log_level", "Logging"))}
            logger = logclient.initClientLogger(logger_name=logger_name, **kwargs)
            self.logger_dict[logger_name] = logger
            return logger
        else:
            return self.logger_dict[logger_name]
    #-----------------------------------------------------------
    def log_configuration(self, logger):
        logger.info("Current simulation path: " + self.sim_path)
        logger.info("Configuration file: " + self.config_file)
        sections = self.cfg.sections()
        sections.append("DEFAULT")
        for section in sections:
            items = self.cfg.items(section)
            if len(items) > 0:
                logger.info("  [" + section + "]")
                for item in items:
                    logger.info("   " + repr(item[0]) + " = " + repr(item[1]))
        for item in self.unrecognized_options.items():
            logger.warning("Unrecognzied option '" + item[1]
                                + "' in section '" + item[0] + "' found.")
        if len(self.unrecognized_options) > 0:
            logger.warning("Unrecognized options found in the configuration"
                                +", please see the default.cfg for valid options.")

    #-----------------------------------------------------------
    def _parse_config_file(self, default_config, config):
        self.cfg = ConfigParser.SafeConfigParser()
        # Enable case sensitive option keys:
        self.cfg.optionxform = str
        self.cfg.read(default_config)

        custom_cfg = ConfigParser.SafeConfigParser()
        custom_cfg.optionxform = str
        custom_cfg.read(config)

        for section in custom_cfg.sections():
            for item in custom_cfg.items(section):
                if not self.cfg.has_option(section, item[0]):
                    self.unrecognized_options[section]=item[0]
                self.cfg.set(section, item[0], item[1])

        
#-----------------------------------------------------------
def norm_path(*paths):
    """Accept one or several paths and returns the joined, normalized, absolute path."""
    return os.path.abspath(os.path.join(*paths))
