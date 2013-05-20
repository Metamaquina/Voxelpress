

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


from os.path import abspath, join, split
import sys

ROOT = abspath(join(split(__file__)[0], ".."))


def setup_path():
    sys.path.insert(1, join(ROOT, "bin"))
    sys.path.insert(1, join(ROOT, "sbin"))
    sys.path.insert(1, join(ROOT, "lib", "voxelpress"))
