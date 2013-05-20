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
import dbus
from hardware_kind import HardwareMonitorKind


class HardwareMonitor(HardwareMonitorKind):
    """This is a dummy hardware monitor that doesn't doesn't do device
    detection on hardware events.  Likely this means that hardware
    detection will be triggered by other events.  Ideally this is
    should not result in a loss of functionality, though it may be
    slower than a more intelligent system."""

