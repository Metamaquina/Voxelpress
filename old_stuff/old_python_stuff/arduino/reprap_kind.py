import re
from threading import Thread


class ReprapKind():
    """Baseclass for all Pepraps."""

    def __init__(self, *args, **kargs):
        pass

    def shutdown(self, disconnected=False):
        """Callback used to turn off the backend and release any
        resources."""

        pass

    def parse_value_pairs(self, response_str):
        """Takes a response from the printer and parses out value
        pairs.  Returns a dictionary."""
        
        pairs = re.findall(r'\S*:.*?(?=(?= \S*:)|$)', response_str)
        data = {}
        for pair in pairs:
            key, value = map(lambda x:x.strip().lower(), pair.split(":"))
            data[key] = value
        return data

    def gcode(self, line):
        """Send a line of gcode to the printer, and returns data if
        applicable."""
        raise NotImplementedError()

    def run_job(self, target):
        """Run a print job.  Target can be a file path or file-like
        object."""
        raise NotImplementedError()

    def relative(self):
        """Sets positioning to relative coordinates."""
        self.gcode("G91")

    def absolute(self):
        """Sets positioning to absolute coordinates."""
        self.gcode("G90")

    def home(self):
        """Moves the printer to the minimum value on all axises.  Only
        should work if endstops are installed, as this is used to zero
        the printer."""
        self.gcode("G28")

    def x_home(self):
        """Moves the x-axis home."""
        self.gcode("G28 X0")

    def y_home(self):
        """Moves the y-axis home."""
        self.gcode("G28 Y0")

    def z_home(self):
        """Moves the x-axis home."""
        self.gcode("G28 Z0")

    def hush(self):
        """Stops the idle hold on all axis and the extruder.  This can
        some times stop an annoying high pitched noise, but is best
        only done between jobs."""
        self.gcode("M84")

    def hold(self):
        """Wait for all temperatures and other slowly-changing values
        to arrive at their set values."""
        self.gcode("M116")

    def move(self, x, y):
        """Moves the print head to the given coordinate pair.
        Coordinates are absolute, not relative."""
        self.absolute()
        self.gcode("G0 X{0} Y{1}".format(x, y))

    def z_move(self, z):
        """Move along the z axis."""
        self.absolute()
        self.gcode("G0 Z%s" % str(z))

    def temp(self):
        """Temperature report."""
        raise NotImplementedError()

    def warm_up(self, extruder_1, *params, **kwords):
        """Warm up the hot bits."""
        raise NotImplementedError()

    def extrude(self, amount=3, feed=200):
        """Extrude fillament."""
        self.relative()
        self.gcode("G1 E{0} F{1}".format(amount,feed))
