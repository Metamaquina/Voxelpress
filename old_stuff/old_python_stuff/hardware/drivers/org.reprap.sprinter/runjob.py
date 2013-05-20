
import sys, json, time
#config = json.loads(sys.argv[1])

time.sleep(1)
motd = sys.stdin.read() # should be blank, I guess


def debug(msg):
    sys.stderr.write("print job: "+msg+"\n")


def poll(msg, silent=False):
    if not silent:
        debug(msg)
    sys.stdout.write(msg + "\n")
    last = ""
    response = ""
    while not response.startswith("ok"):
        time.sleep(.1)
        response = sys.stdin.readline()
        if response and not response == last and not silent:
            last = response
            debug(response.strip())


#debug("Warming up to 165 degrees celcius...")
#poll("M109 S165")

with open(sys.argv[1], "r") as job:
    poll("begin job")
    for line in job:
        cmd = line.split(";")[0].strip()
        if cmd:
            poll(cmd, silent=True)
    poll("done!")
