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
sys.path.insert(
    1, os.path.abspath(os.path.join(sys.argv[0], "../../../vpd/vpd")))

import argparse
import json
import dbus

from printer_kind import PRINTER_STATES

VPD = dbus.SessionBus().get_object('org.voxelpress', '/org/voxelpress')




def vpd_call(method, *args, **kwords):
    method = VPD.get_dbus_method(method, 'org.voxelpress.api')
    if len(args) == 0:
        if len(kwords.keys()):
            return method(json.dumps(kwords))
        else:
            return method()
    elif len(args) == 1:
        return method(args[0])
    else:
        return method(json.dumps(args))


def lookup_by_uuid(uuid_):
    return json.loads(vpd_call("get_printer_info", uuid_))


def lookup_all():
    uuids = json.loads(vpd_call("get_printers"))
    return [lookup_by_uuid(p) for p in uuids]
    

def list_printers(args=None):
    for printer in lookup_all():
        name = printer["name"]
        state = PRINTER_STATES[printer["state"]]
        print " - {0} ( {1} )".format(name, state)


def request_print(args):
    printers = lookup_all()
    selected = None
    if args.p:
        for printer in printers:
            if printer["name"] == args.p:
                selected = printer
        if not selected:
            print "No printers match \"{0}\"".format(args.p)
            exit()
    elif len(printers) == 1:
        selected = printers[0]
    if not selected:
        print "Unable to determine where to send this job."
        exit()
    else:
        if os.path.isfile(args.file):
            pipeline = json.loads(vpd_call("get_pipeline", selected["uuid"], args.file))
            print vpd_call("request_print", 
                           uuid = selected["uuid"],
                           config = pipeline,
                           env = dict(os.environ),
                           path = args.file)
        else:
            print "No such file:", args.file
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="vpp is used to submit files to voxelpress for 3D printing.")
    subparsers = parser.add_subparsers(
        help='sub-command help')
    
    # parser for 'list' command
    parser_list = subparsers.add_parser(
        "list", help="List known printers and their current states.")
    parser_list.set_defaults(func=list_printers)
    
    # parser for 'print' command
    parser_print = subparsers.add_parser(
        "print", help="Send a print job to a printer.")
    parser_print.add_argument("file")
    parser_print.add_argument("-p", metavar="printer")
    parser_print.set_defaults(func=request_print)

    args = parser.parse_args()
    args.func(args)
