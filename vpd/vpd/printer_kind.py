

# This file is part of VoxelPress.
#
# VoxelPress is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# VoxelPress is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VoxelPress.  If not, see <http://www.gnu.org/licenses/>.
#
# Have a nice day!


import os
import sys
LIBPATH = os.path.split(os.path.abspath(__file__))[0]
import glob
import uuid
import json
import pickle
from job_handler import wake_up, stash_file, PrintJob


PRINTER_STATES = (
    "offline",
    "idle",
    "printing",
    "error",
    )


class VoxelpressPrinter:
    
    def __init__(self, uuid):
        self.__uuid = uuid
        self.name = "Unknown Printer"
        self.state = 0
        self.hardware_config = {}
        self.pipeline_config = {}
        self.queue = []

        config_name = str(uuid) + ".json"
        self.__config_path = os.path.join(
            LIBPATH, "../../etc/voxelpress/printers/", config_name)

        self.__load_config()

    def __load_config(self):
        """
        Load a saved configuration for this printer, if such exists.
        """
        try:
            with open(self.__config_path, "rb") as config_file:
                config = json.load(config_file)
        except IOError:
            return

        if config.has_key("name"):
            self.name = config["name"]
        if config.has_key("filter_settings"):
            for filter_config in config["filter_settings"]:
                try:
                    filter_name = filter_config["filter"]
                    self.pipeline_config[filter_name] = filter_config
                except:
                    # FIXME maybe log the error?
                    pass
            
    def __save_config(self):
        """
        Save the configuration for this printer.
        """
        printer_config = {
            "name" : self.name,
            "filter_settings" : [ f for f in self.pipeline_config.values() ],
            }
        with open(self.__config_path, "wb") as config_file:
            json.dump(printer_config, config_file)

    def __get_or_load_filter(self, filter_name):
        if not self.pipeline_config.has_key(filter_name):
            # FIXME error if filter doesn't exist
            path = os.path.join(LIBPATH, "filters", filter_name, "options.json")
            with open(path, "rb") as config_file:
                defaults = json.load(config_file)
            defaults["filter"] = filter_name
            self.pipeline_config[filter_name] = defaults
        return self.pipeline_config[filter_name]

    def get_pipeline(self, mime_type):
        """
        Creates a basic configuration for a given print job mime type.
        This is indirectly called by the user interface prior to
        requesting a print job.
        """

        # FIXME totally cheating by hardcoding a pipeline =(
        pipeline = [
            self.__get_or_load_filter("org.slic3r"),
            self.__get_or_load_filter("org.reprap.sprinter"),
            ]
        return pipeline 

    def __set_pipeline(self, pipeline):
        """
        Updates the stored settings for individual filters.  This
        would be called after a print job is created.
        """
        
        for config in pipeline:
            self.pipeline_config[config["filter"]] = config
        self.__save_config()

    def request_job(self, path, config, context_env):
        """
        Called to (attempt to) start a print job.
        """
        
        self.__set_pipeline(config)
        tmp_file = stash_file(self.__uuid, path)
        job = PrintJob(self.__uuid, path, tmp_file, config, context_env)

        if self.state == 0:
            return "Printer is offline."

        elif self.state == 1:
            self.state = 2
            self.queue.append(job)
            wake_up(self.__uuid)
            return "Sent job to printer."

        else:
            self.queue.append(job)
            return "Job has been queued."

    def on_connect(self, device_config):
        self.__load_config()
        self.hardware_config = device_config
        self.state = 1
        print "Printer connected:", self.name

    def on_disconnect(self):
        self.__save_config()
        self.state = 0
        print "Printer disconnected:", self.name
