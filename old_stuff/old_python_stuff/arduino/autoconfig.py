import sys
from glob import glob
from . import acm_firmwares as firmware
from .acm_device import AcmDevice


def find_repraps():
    """Runs various autodetection methods, and returns a tuple of
    printers found."""

    pool = []
    pool += list(find_acm_repraps())
    # ...
    return tuple(pool)


def find_acm_repraps():
    """This function attempts to automatically detect, connect to, and
    initialize Repraps that appear as USB serial devices."""

    baud_rates = (
        2400,
        9600,
        19200,
        38400,
        57600,
        115200,
        250000,
        )

    def auto_detect(port, baud):
        serial = AcmDevice(port, baud)
        err = ""
        if serial.motd:
            printer = firmware.select_firmware(serial)
            if printer:
                return printer
            else:
                err="No printer dectected at {0} with baud rate {1}"
        else:
            err="Unable to connect to port {0} with baud rate {1}"
        serial.disconnect()
        raise IOError(err.format(port,baud))

    search = []
    if sys.platform == "linux2":
        search += glob("/dev/ttyACM*")
        search += glob("/dev/ttyUSB*")
    elif sys.platform == "darwin":
        search += glob("/dev/*.usbmodem*")
        search += glob("/dev/*.usbserial*")
    else:
        raise NotImplementedError(
            "I'm sorry, but your operating system doesn't seem to be currently supported.")
    found = []
    if search:
        for port in search:
            for baud in baud_rates[::-1]:
                try:
                    found.append(auto_detect(port, baud))
                    break
                except IOError:
                    continue
    return tuple(found)
