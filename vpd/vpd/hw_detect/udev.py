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
import glob
import json
import subprocess
import gudev
import dbus
from hardware_kind import HardwareMonitorKind


class HardwareMonitor(HardwareMonitorKind):
    """This class implements the hardware monitor for systems in which
    udev is available.  Presumably that means just Linux."""

    def __init__(self):
        self.__udev = gudev.Client(["tty", "usb/usb_device"])
        self.__udev.connect("uevent", self.__udev_callback, None)
        self.__scan()

    def __udev_callback(self, client, action, device, user_data):
        hw_info = device.get_property("ID_SERIAL")
        subsystem = device.get_subsystem()

        if action == "add" and subsystem == "tty":
            usb_path = device.get_parent().get_parent().get_device_file()
            tty_path = device.get_device_file()
            self.__on_connect("tty", usb_path, tty_path, hw_info)
                
        elif action == "remove" and subsystem == "usb":
            usb_path = device.get_device_file()
            self.__on_disconnect("tty", usb_path)

    def __on_connect(self, hint, usb_path, tty_path, hw_info):
        self.__split("connect", hint, usb_path, tty_path, hw_info)

    def __on_disconnect(self, hint, usb_path):
        self.__split("disconnect", hint, usb_path)

    def __split(self, *args):
        """Spawn udev.py as a separate process and then return."""
        _args = ["python", __file__] + map(str, list(args))
        subprocess.Popen(_args, cwd=os.path.split(__file__)[0])    

    def __scan(self):
        """Iterate over available serial ports and try to find repraps."""
        for device in self.__udev.query_by_subsystem("tty"):
            hw_info = device.get_property("ID_SERIAL")
            if hw_info:
                try:
                    usb_path = device.get_parent().get_parent().get_device_file()
                    tty_path = device.get_device_file()
                except:
                    # FIXME ... not sure what to do =)
                    continue
                self.__on_connect("tty", usb_path, tty_path, hw_info)


class HardwareSubprocess:
    
    def __init__(self, state, hint, usb_path, tty_path=None, hw_info=None):
        self.__vpd = dbus.SessionBus().get_object(
            'org.voxelpress', '/org/voxelpress')
        
        if state == "connect":
            search_path = os.path.join(
                os.path.split(__file__)[0],
                "bootstrap", "*", "manifest.json")
            found = glob.glob(search_path)

            for m_path in found:
                config = self.__probe(m_path, usb_path, tty_path, hw_info)
                if config:
                    print "Printer detected! uuid=", config["uuid"]
                    config["usb_path"] = usb_path
                    config["hw_info"] = hw_info
                    self.__on_connect(config)
                    break

        elif state == "disconnect":
            self.__on_disconnect(usb_path)

    def __callback(self, handler, argument):
        callback = self.__vpd.get_dbus_method(handler, "org.voxelpress.events")
        callback(argument)

    def __probe(self, m_path, usb_path, tty_path, hw_info):
        print "probing:", "\n\t* ".join(["", m_path, usb_path, tty_path, hw_info])
        with open(m_path, "rb") as m_file:
            # FIXME ... log exceptions?
            manifest = json.load(m_file)
        cwd = os.path.split(m_path)[0]
        cmd = manifest['cmd']
        if type(cmd) != list:
            cmd = [cmd]
        try:
            output = subprocess.check_output(
                cmd + [tty_path, hw_info], cwd=cwd)
        except subprocess.CalledProcessError:
            return None
        return json.loads(output)

    def __on_connect(self, config):
        """Trigger the on_connect callback on the daemon."""
        self.__callback("on_connect", json.dumps(config))
        
    def __on_disconnect(self, usb_path):
        """Trigger the on_disconnect callback on the daemon."""
        self.__callback("on_disconnect", usb_path)


if __name__ == "__main__":
    # this should only happen because this was launched as a
    # subprocess.

    hws = HardwareSubprocess(*sys.argv[1:])
    
    
