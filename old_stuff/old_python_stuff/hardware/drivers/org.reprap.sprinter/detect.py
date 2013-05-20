#!/usr/bin/env python

from sys import stdin, stdout, stderr
import time
time.sleep(1)

motd = "\n".join([line.strip() for line in stdin.readlines()])
if motd.count("Sprinter") or motd.count("Marlin"):
    exit(0)
else:
    exit(1)

