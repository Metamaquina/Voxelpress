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
import tempfile
import subprocess
import multiprocessing
CPU_COUNT = multiprocessing.cpu_count()
CONFIG = json.loads(os.environ["FILTER_CONFIG"])["config_file"][2]
try:
    DISPLAY = os.environ["DISPLAY"]
except KeyError:
    DISPLAY = "unknown"




def cleanup(tmp_path):
    """Removes temporary files."""

    for path in glob.glob(os.path.join(tmp_path, "*")):
        os.remove(path)
    os.removedirs(tmp_path)


def slice(in_path, out_path, config_path, cpu_count, cmd="slic3r"):
    """Call the slic3r executable."""

    args = [
        cmd,
        "--load", config_path,
        "--output", out_path,
        "-j", cpu_count,
        in_path]

    return subprocess.call(
        args, 
        cwd=cwd,
        stdout=sys.stderr,
        stderr=sys.stderr)


def main():
    if not os.path.isfile(CONFIG):
        sys.stderr.write("FATAL: Config file not found.\n")
        return 1

    tmp_dir = tempfile.mkdtemp()
    in_path = os.path.join(tmp_dir, "input.stl")
    out_path = os.path.join(tmp_dir, "output.gcode")

    with open(in_path, "wb") as in_file:
        in_file.write(sys.stdin.read())
    
    slice(in_path, out_path, CONFIG, str(CPU_COUNT))
    count = 0
    with open(out_path, "rb") as out_file:
        for line in out_file.readlines():
            sys.stdout.write(line)
            count += 1
    cleanup(tmp_dir)
    if count == 0:
        sys.stderr.write("FATAL: Slic3r failed?.\n")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
