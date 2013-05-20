from glob import glob
from ..reprap_kind import ReprapKind


class ReprapACM(ReprapKind):
    """Repraps which are controlled by an ACM device of some kind
    (usually an Arduino)."""
    
    def __init__(self, connection, firmware="Unknown", *args, **kargs):
        self.__serial = connection
        self.__buffer = False
        self.info = {}
        # Set a plausible printer uuid, which may be overridden by the
        # firmware driver.
        self.info["uuid"] = self.__serial.make_uuid(firmware)
        ReprapKind.__init__(self, *args, **kargs)

    def shutdown(self, disconnected=False):
        """Callback used to turn off the backend and release any
        resources."""

        self.__serial.disconnect(disconnected)

    def gcode(self, line):
        """Send a line of gcode to the printer, and returns data if
        applicable."""
        self.__serial.send(line)
        return self.__serial.poll()

    def __stream(self, fobject):
        """Extracts gcode commands from a file like object, removes
        comments and blank lines, and then streams the commands to the
        printer."""
        self.hold()
        for line in fobject:
            if line.startswith(";"):
                continue
            code = line.split(";")[0].strip()
            self.gcode(code)

    def run_job(self, target):
        """Run a print job.  Target can be a file path or file-like
        object."""
        fobject = None
        if type(target) in [unicode, str]:
            found = glob(target)
            if found:
                # FIXME, should cue up multiple jobs, not just do one...?
                fobject = open(found[0])
        if fobject:
            self.__stream(fobject)
