import json, os


class PrintJob():
    """A pending or active print job."""

    def __init__(self):
        self.status = None
        self.job_name = None
        self.job_file = None


class VoxelpressPrinter():
    
    def __init__(self, uuid):
        self.uuid = uuid
        self.__queue = []
        self.__config = json.load(open(os.path.join("settings", str(uuid) + ".json")))
        self.__connected = None

        self.name = str(self.uuid)
        if self.__config.has_key("printer name"):
            self.name = self.__config["printer name"]

    
    def __save(self):
        """Save the running config."""
        json.dump(self.__config, open(os.path.join("settings", str(uuid) + ".json")),"w")


    def get_state(self):
        """Returns a string indicating the status of the printer."""
        if self.__connected:
            return self.__connected.get_state()
        else:
            return "offline"

    
    def pdq_print_job(self, job_path):
        """Adds a print job into the queue..."""
        
        self.__queue.append(job_path)
        if self.__connected:
            self.__connected.warm_up(self.__config)
            while self.__queue and self.__connected.get_state() in ["ready", "unknown"]:
                self.__connected.run_job(self.__config, self.__queue.pop(0))

    def on_connect(self, device):
        """A device that matches this config was connected."""
        self.__connected = device
        print self.name, "is now online."


    def on_disconnect(self):
        """The associated device is now offline."""
        self.__connected = None
        print self.name, "is now offline."
