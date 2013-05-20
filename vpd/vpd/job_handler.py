#!/usr/bin/env python

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
sys.path.insert(1, os.path.abspath(os.path.split(__file__)[0]))

import json
import shutil
import pickle
import subprocess
import tempfile
import dbus


FILTER_PATH = os.path.join(os.path.split(__file__)[0], "filters")
JOB_STATES = (
    "pending",
    "printing",
    "complete",
    "error",
)


def wake_up(printer_id):
    """
    Creates a subprocess that runs the print queue until it dries up
    or hits an error.
    """
    printer_dir = get_printer_dir(printer_id)
    subprocess.Popen(map(str, ["python", __file__, printer_id]), cwd=printer_dir)


def get_var_dir():
    # FIXME subprocess cwd should be in /var/voxelpress/[printer_id]
    # and only the fake var folder for this project if access can't be
    # had to /var/voxelpress
    var_dir = os.path.join(os.path.split(__file__)[0], "..", "..", "var")
    if not os.path.isdir(var_dir):
        os.mkdir(var_dir)
    return os.path.abspath(var_dir)


def get_printer_dir(printer_id):
    var_dir = get_var_dir()
    printer_dir = os.path.join(var_dir, str(printer_id))
    if not os.path.isdir(printer_dir):
        os.mkdir(printer_dir)
    queue_dir = os.path.join(printer_dir, "queue")
    if not os.path.isdir(queue_dir):
        os.mkdir(queue_dir)
    return printer_dir


def stash_file(printer_id, file_path):
    """
    Copy the provided file into a temporary file and return the path.
    """

    assert os.path.isfile(file_path)
    printer_dir = get_printer_dir(printer_id)
    tmp_dir = os.path.join(printer_dir, "queue")
    tmp_file = tempfile.mkstemp(dir=tmp_dir)
    shutil.copyfile(file_path, tmp_file[1])
    return tmp_file[1]


def debug(*args):
    msg = " ".join(map(str, args))
    sys.stderr.write("{0}\n".format(msg))


class PrintJob:
    
    def __init__(self, printer_id, file_path, tmp_path, settings, context_env):
        self.printer_id = printer_id
        self.file_path = file_path
        self.tmp_path = tmp_path
        self.settings = settings
        self.context = context_env
        self.state = 0
        self.__tmpfile = None

    def __init_pipeline(self, hw_target):
        """Create the actual printing pipeline of subprocesses."""
        assert hw_target["terminus"] == self.settings[-1]["filter"]
        self.settings[-1]["hardware"] = hw_target

        pipeline = []
        last = self.__tmpfile
        for stage in self.settings:
            cwd = os.path.join(FILTER_PATH, stage["filter"])
            env = self.context
            env["FILTER_CONFIG"] = json.dumps(stage)

            with open(os.path.join(cwd, "manifest.json"), "r") as manifest_file:
                manifest = json.load(manifest_file)

            pipeline.append(
                subprocess.Popen(manifest["cmd"],
                                 cwd=cwd, env=env,
                                 stdin=last,
                                 stdout=subprocess.PIPE,
                                 #stderr=subprocess.PIPE
                                 stderr=sys.stderr
                                 ))
            last = pipeline[-1].stdout
        return pipeline

    def activate(self, hw_target):
        self.state = 1
        self.__tmpfile = open(self.tmp_path, "rb")
        print >> sys.stderr, "Creating pipeline..."
        pipeline = self.__init_pipeline(hw_target)

        count = 0
        for process in pipeline:
            count += 1
            print >> sys.stderr, "Waiting for filter #{0}...".format(count)
            ret = process.wait()
            #for msg in process.stderr.readlines():
            #    debug(msg)
            if ret != 0:
                print >> sys.stderr, "Printer is now in an error state."
                self.state = 2
                break
        print >> sys.stderr, "Job finished...?"

        if self.state == 1:
            self.state = 3
        
        self.__tmpfile.close()
        os.unlink(self.tmp_path)
        for proc in pipeline:
            try:
                proc.kill()
            except OSError:
                continue




class PrintPipeline:
    
    def __init__(self):
        self.__printer_id = sys.argv[1]
        self.__vpd = dbus.SessionBus().get_object(
            'org.voxelpress', '/org/voxelpress')
        self.run_jobs()

    def __vpd_callback(self, handler, argument, ext):
        callback = self.__vpd.get_dbus_method(handler, "org.voxelpress." + ext)
        return callback(argument)

    def util(self, method, argument):
        return self.__vpd_callback(method, argument, "util")

    def event(self, event, argument):
        return self.__vpd_callback(event, argument, "events")

    def get_hw_config(self):
        return json.loads(self.util("get_hw_config", self.__printer_id))

    def get_next(self):
        queue = pickle.loads(self.util("dump_queue", self.__printer_id))
        if len(queue) > 0:
            return queue[0]
        else:
            return None

    def run_jobs(self):
        """Prints jobs until either the queue runs dry, or the printer
        goes into an error state."""

        job = self.get_next()
        while job:
            job.activate(self.get_hw_config())

            if job.state == 2:
                job = self.get_next()
            else:
                break




if __name__ == "__main__":
    # this should only happen because this was launched as a
    # subprocess.
    
    pipeline = PrintPipeline()
