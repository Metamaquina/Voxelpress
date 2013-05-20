
import sys, os, json, time
#config = sys.argv[1])
config = json.loads(os.environ["PRINTER_CONFIG"])

time.sleep(1)
motd = sys.stdin.read()


def debug(msg):
    sys.stderr.write("warmup: "+msg+"\n")


def poll(msg):
    debug(msg)
    sys.stdout.write(msg + "\n")
    last = ""
    response = ""
    while not response.startswith("ok"):
        time.sleep(.1)
        response = sys.stdin.readline()
        if response and not response == last:
            last = response
            debug(response.strip())


if config["advanced"]["endstops"]:
    debug("Endstops appear to be present...")
    poll("G28")
else:
    debug("Running without endstops...")
poll("M84")

debug("Warming up to 165 degrees celcius...")
poll("M109 S165")
#poll("M116")


debug("...ready?")
