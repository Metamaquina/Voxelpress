

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


import json
import uuid
from mock import patch
import util
util.setup_path()
import vpd


def test_device_connect():
    with patch('dbus.service.Object') as dbus:
        with patch('printer_kind.VoxelpressPrinter') as printerkind:      
            _uuid = uuid.UUID(int=0)
            server = vpd.VoxelpressServer()
            device = {
                "uuid" : str(_uuid),
                "name" : "Phoney Pony",
                "usb_path" : "/dev/null",
                }
            server.on_connect(json.dumps(device))

            assert server.devices.has_key("/dev/null")
            assert server.printers.has_key(_uuid)
