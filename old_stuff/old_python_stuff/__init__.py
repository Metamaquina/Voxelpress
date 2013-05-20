
import subprocess
from serial import Serial
from arduino import acm_firmwares as firmware
from arduino.acm_device import AcmDevice


def get_serial_printer(port_file):
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

    found = None
    for baud in baud_rates[::-1]:
        try:
            found = auto_detect(port_file, baud)
            break
        except IOError:
            pass

    return found


