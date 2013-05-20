import uuid
from .acm_kind import ReprapACM


class SprinterReprap(ReprapACM):
    """Represents a Reprap running the Sprinter firmware."""
    
    def __init__(self, *args, **kargs):
        kargs["firmware"] = "Sprinter"
        ReprapACM.__init__(self, *args, **kargs)
        
        info = self.gcode("M115")
        for key, value in self.parse_value_pairs(info[0]).items():
            self.info[key] = value

        _uuid = uuid.UUID(info[1].strip())
        if _uuid != uuid.UUID(int=0):
            self.info["uuid"] = _uuid

        self.gcode("G21") # set units to mm
        self.home()
        self.hush()

    def temp(self):
        """Temperature report."""
        temps = self.gcode("M105")[0]
        if temps != "ok":
            return self.parse_value_pairs(temps)
        else:
            return {}

    def warm_up(self, extruder_1, *params, **kwords):
        """Warm up the hot bits."""
        try:
            bed = kwords["bed"]
        except KeyError:
            bed = None
        extruders = [extruder_1] + list(params)

        if len(extruders) == 1:
            self.gcode("M104 S{0}".format(extruder_1))
        else:
            raise NotImplementedError("multiple extruders")        
        if bed:
            raise NotImplementedError("hot bed")
