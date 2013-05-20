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
import time
import json
from printcore import printcore
CONFIG = json.loads(os.environ["FILTER_CONFIG"])
BAUD = int(CONFIG["hardware"]["baud"])
PORT = CONFIG["hardware"]["tty_path"]


def main(port, baud):
    print >> sys.stderr, "Attemping to print at {0} with baud {1}\n\n".format(
        port, baud)
    p = printcore(port, baud)
    p.loud = True
    time.sleep(2)


    print >> sys.stderr, "###", "Building gcode stream..."

    setup_codes = [
        "G28", # home
        "G0 X100 Y100",
        "M116", # wait
        "G28",
        "M18", # stfu
        

        "M21", # init sd card
        "M28 vppjob.gco", # begin write
        ]

    job_codes = [line.strip() for line in sys.stdin.readlines()]

    teardown_codes = [
        "M116",
        "M29", # stop writing to sd card
        #"M23 vppjob.gco", # select job
        "M24", # start print
        ]


    print >> sys.stderr, "###", "Sending Gcode stream to printer..."
    p.startprint(setup_codes + job_codes + teardown_codes)
    print >> sys.stderr, "###", "Done printing!"

if __name__ == "__main__":
    sys.exit(main(PORT, BAUD))
