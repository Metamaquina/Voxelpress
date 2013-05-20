import uuid, socket
import time
from serial import Serial


class AcmDevice:
    """Wrapper for accessing usb serial devices."""

    def __init__(self, port, baud):
        self.__port = port
        self.__baud = baud
        self.__connection = Serial(port, baud, timeout=1)
        self.motd = "\n".join([line.strip() for line in self.__connection.readlines()])
        self.__connection.timeout = 0
        if not (self.__connection.readable() and self.__connection.writable()):
            raise IOError("Insufficient read/write permissions for port %s." % port)

    def disconnect(self, disconnected=False):
        """Close the serial connection."""
        if not disconnected:
            self.__connection.flushOutput()
        self.__connection.close()

    def flush(self):
        """Empties the output buffer."""
        self.__connection.flushOutput()

    def poll(self, wait_for_ok=True):
        """Poll the serial port for new data."""
        buf = ""
        response = []
        timeout = 1
        while True:
            poll = self.__connection.readlines()
            if poll:
                for line in poll:
                    buf += line
                    if line.endswith("\n"):
                        response.append(buf.strip())
                        buf = ""
                if response and response[-1].startswith("ok"):
                    break
            elif not wait_for_ok:
                if timeout > 0:
                    timeout -= 1
                else:
                    break
        if buf:
            response.append(buf.strip())
        return tuple(response)

    def send(self, line):
        """Send a line of text to the serial port.  Will automatically
        be terminated with a line end."""
        self.__connection.write(line.strip() + "\n\r")

    def make_uuid(self, firmware_name):
        """Deterministically generatse a uuid from this connection.
        Used by firmware drivers if the firmware doesn't specify one
        through other means."""

        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, socket.getfqdn())
        return uuid.uuid5(namespace, firmware_name+"@"+self.__port)

