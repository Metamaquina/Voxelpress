#!/usr/bin/env python

import os
import sys
import json
import dbus

VPD = dbus.SessionBus().get_object('org.voxelpress.daemon', '/org/voxelpress/daemon')


def list_printers():
    method = VPD.get_dbus_method("list_printers", "org.voxelpress.daemon")
    return json.loads(method())


def cue_job(printer_name, file_name):
    method = VPD.get_dbus_method("cue_job", "org.voxelpress.daemon")
    return method(json.dumps([printer_name, file_name]))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "list":
        for uuid, name, status in list_printers():
            prefix = " o"
            if status == "offline":
                prefix = " -"
            print prefix, name
        exit(0)

    elif len(sys.argv) == 5 and sys.argv[1] == "print" and sys.argv[3] == "to":
        path = sys.argv[2]
        target = sys.argv[4]

        if not os.path.isfile(path):
            print "Bad file path"
            exit(1)
        
        printers = list_printers()
        found = None
        for uuid, name, status in printers:
            if name == target:
                if status == "offline":
                    print name, "is offline!"
                    exit(1)
                else:
                    found = True
        if not found:
            print "Unknown printer"
            exit(1)

        else:
            cue_job(target, path)
            exit(0)

    else:
        print "Excepted usage:"
        print "vpp list"
        print "vpp print file to printer"
