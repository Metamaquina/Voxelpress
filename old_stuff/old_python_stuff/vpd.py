#!/usr/bin/env python

import daemon

from threading import Lock

import os, glob, json
import socket, uuid
import gobject
import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop

import hardware
from printers import VoxelpressPrinter


class VoxelpressServer(dbus.service.Object):

    def __init__(self, main_loop):
        self.__loop = main_loop
        namespace = "org.voxelpress.daemon"
        bus_name = dbus.service.BusName(namespace, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/" + namespace.replace(".", "/"))
        self.devices = {}
        self.printers = {}

        self.__device_lock = Lock()

        saved_printers = glob.glob("settings/*.json")
        for path in saved_printers:
            puuid = uuid.UUID(os.path.split(path)[1][:-5])
            self.printers[puuid] = VoxelpressPrinter(puuid)


    def hw_connect_event(self, device):
        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, socket.getfqdn())
        device.uuid = uuid.uuid5(namespace, device.hw_info+"."+device.driver)

        printer = None
        self.__device_lock.acquire()
        try:
            if self.printers.has_key(device.uuid):
                printer = self.printers[device.uuid]
            else:
                driver_cpath = os.path.join("hardware/drivers", device.driver, "config.json")
                with open(driver_cpath, "r") as config_file:
                    config = json.load(config_file)
                printer_cpath = os.path.join("settings", str(device.uuid) + ".json")
                with open(printer_cpath, "w") as config_file:
                    json.dump(config, config_file)
                printer = VoxelpressPrinter(device.uuid)
        except IOError:
            print "Config file could not be opened."
            print "Either:", driver_cpath, "or", printer_cpath
        except ValueError:
            print "Config file contained invalid json..."
            print "Probably", driver_capth

        if printer:
            self.devices[device.hw_path] = device
            print "New device attached:"
            print "  driver:", device.driver
            print "    hwid:", device.hw_path
            print "    uuid:", device.uuid
            printer.on_connect(device)
        self.__device_lock.release()


    def hw_disconnect_event(self, hw_path):
        if self.devices.has_key(hw_path):
            device = self.devices[hw_path]
            device.on_disconnect()
            del self.devices[hw_path]
            self.printers[device.uuid].on_disconnect()


    @dbus.service.method("org.voxelpress.daemon", out_signature='s')
    def list_printers(self):
        found = [(str(p.uuid), p.name, p.get_state()) for p in self.printers.values()]
        return json.dumps(found)


    @dbus.service.method("org.voxelpress.daemon", in_signature='s')
    def cue_job(self, json_args):
        named_printer, job_path = json.loads(json_args)

        for printer in self.printers.values():
            if printer.name == named_printer:
                printer.pdq_print_job(job_path)


if __name__ == "__main__":
    main_loop = gobject.MainLoop()
    DBusGMainLoop(set_as_default=True)
    voxelpress = VoxelpressServer(main_loop)
    hardware.CONNECT_HW_EVENTS(voxelpress)
    hardware.SCAN_HW(voxelpress)
    main_loop.run()


