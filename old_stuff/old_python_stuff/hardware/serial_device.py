
from serial import Serial
from device_kind import DeviceKind
import drivers



class SerialDevice(DeviceKind):
    """Serial device backend."""

    baud_rates = (
        2400,
        9600,
        19200,
        38400,
        57600,
        115200,
        250000,
        )


    def __init__(self, *args, **kwords):
        DeviceKind.__init__(self, *args, **kwords)
        self.__path = None
        self.__baud = None
        self.__usb = None
        self.__com = None
        self.state = "busy"


    def __detect_driver(self, baud):
        """Used by on_connect to attempt to discover the baud rate of
        the port and applicable firmware."""

        def connect():
            return Serial(self.__path, baud)

        return drivers.select_driver("serial", connect)


    def warm_up(self, config):
        """Notifies the driver to run any setup code."""

        if not self.__com:
            self.__com = Serial(self.__path, self.__baud)
        self.state = "busy"
        driver = drivers.DeviceDriver(self.driver, self.__com)
        driver.warm_up(config)
        self.state = "ready"

    
    def run_job(self, config, job_file):
        """Runs a print job."""

        self.state = "busy"
        driver = drivers.DeviceDriver(self.driver, self.__com)
        driver.run_job(config, job_file)
        self.state = "jammed"
        

    def on_connect(self, tty_path):
        self.__path = tty_path

        for baud in self.baud_rates[::-1]:
            try:
                print "trying baud", baud
                self.driver = self.__detect_driver(baud)
                if self.driver:
                    self.__baud = baud
                    self.state = "ready"
                    break
            except IOError:
                continue

        if self.driver:
            return True
