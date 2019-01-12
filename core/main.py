# main driver module
# this has little application in real life usage
# i used this just to automate a set of inputs
#
# for each command this module launches a new subprocess which handles the respective command
# this allows the web client to be used independently if it is needes, just providing the command line arguments
# POSSIBLE COMMANDS:  'url' - takes a screenshot at the specified url
#                     'r url' - returns from db layer (now just the name of the saved file) but this can be
#                       replaced with an adapter for a visual interface to get the actual image
#                       added also an opencv visualization for this kind of queries
#                     'r *' - in the same manner gets all file names

from subprocess import Popen

inputfilename = "input.in"
ssServicePath = "../web/main.py"


file = open(inputfilename,'r')


for line in file:
    if line != '':

        # time.sleep(0.5)
        args = line.split(' ')
        runCommand = "python " + ssServicePath + ' ' + line
        Popen(['python', ssServicePath, *args])
        # print("ran command: " + runCommand)