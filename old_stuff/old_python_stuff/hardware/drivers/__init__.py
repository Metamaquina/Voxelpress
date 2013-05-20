
import os
import glob
import json
import subprocess


def __find_installed_drivers():
    """Find available device drivers."""

    registry = {}
    search = [os.path.split(path)[0] for path in
              glob.glob("hardware/drivers/*/driver.json")]

    for path in search:
        namespace = os.path.split(path)[1]
        driver = json.load(open(os.path.join(path, "driver.json"), "r"))

        if driver:
            registry[namespace] = driver

    return registry
    

DRIVER_REGISTRY = __find_installed_drivers()



class DeviceDriver():
    def __init__(self, uri, device_fileob):
        self.__uri = uri
        self.__defs = DRIVER_REGISTRY[uri]
        self.__device = device_fileob


    def __call(self, name, config, cmd_args=[]):
        if self.__defs.has_key(name):
            old_path = os.getcwd()
            os.chdir(os.path.join("hardware/drivers/", self.__uri))
            _args = self.__defs[name] + cmd_args
            _environ = {
                "PRINTER_CONFIG" : json.dumps(config)
                }
            proc = subprocess.Popen(
                _args, env=_environ, stdin=self.__device, stdout=self.__device)
            proc.communicate()
            os.chdir(old_path)


    def warm_up(self, printer_config):
        self.__call("warmup cmd", printer_config)
        print "...done"
 

    def run_job(self, printer_config, job_path):
        self.__call("print cmd", printer_config, cmd_args=[job_path])
        print "...done"
    



def select_driver(hint, connect):
    """Given a hint and a file object, run each applicable driver's
    detection test, and return the namespace of the first one that
    passes."""

    for namespace, driver in DRIVER_REGISTRY.items():
        if not driver["backend"] == hint:
            continue
        old_dir = os.getcwd()
        arguments = driver["detect cmd"]
        fileob = connect()
        try:
            os.chdir(os.path.join("hardware/drivers", namespace))
            call = subprocess.Popen(arguments, stdin=fileob, stdout=fileob)
            call.communicate()
            result = call.returncode
        except OSError:
            result = 1
        finally:
            fileob.close()
            os.chdir(old_dir)
        if result == 0:
            return namespace

    return None
