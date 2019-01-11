import time
import sys
import os
import asyncio
from subprocess import Popen

inputfilename = "input.in"
ssServicePath = "../web/main.py"


file = open(inputfilename,'r')

for line in file:
    if line != '':

        # time.sleep(0.5)
        args = line.split(' ')
        runCOmmand = "python " + ssServicePath + ' ' + line
        Popen(['python', ssServicePath, *args])
        print("ran command: " + runCOmmand)
        # os.system(runCOmmand)