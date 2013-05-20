from .acm_kind import ReprapACM


class MarlinReprap(ReprapACM):
    """Represents a Reprap running the Marlin firmware."""

    def __init__(self, *args, **kargs):
        kargs["firmware"] = "Marlin"
        ReprapACM.__init__(self, *args, **kargs)
        
        info = self.gcode("M115")
        for key, value in self.parse_value_pairs(info[0]).items():
            self.info[key] = value
