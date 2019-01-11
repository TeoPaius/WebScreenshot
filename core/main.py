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
        # os.system(runCOmmand)