

class DeviceKind():
    """Baseclass for all printer device backends."""
    
    def __init__(self, hw_path, hw_info):
        self.hw_path = hw_path
        self.hw_info = hw_info
        self.driver = None
        self.uuid = None
        self.state = "unknown"


    def get_state(self):
        """Returns a string indicating the printer's state, as
        reported by the device."""

        return self.state


    def warm_up(self, config):
        """Notifies the driver to run any setup code."""
        pass

    
    def run_job(self, config, job_file):
        """Runs a print job."""
        
        self.state = "busy"


    def on_connect(self):
        """Called when the device is first connected to the system.
        Return False if no useful configurating can be determined."""

        return False


    def on_disconnect(self):
        """Called when the device is physically disconected for
        cleanup purposes."""

        pass
