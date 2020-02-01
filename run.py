import sys
import os
import platform
import subprocess
import shutil
import copy
from distutils.file_util import copy_file
from distutils.dir_util import mkpath

def run(command, in_env = None):
	process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT, env=in_env)

	exitCode = process.wait()

	if exitCode != 0:
		print('Command \'' + command + '\' failed!')
		print('Expected error code 0, got ' + str(exitCode))
		sys.exit(1)

def run_save_out(command, out_file, print_to_stdout = False, in_env = None):
	file = open(out_file, "wb")
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=in_env)

	if not print_to_stdout:
		print("Running command \"" + command + "\" with output appending to \"" + out_file + "\". Dots will be printed to indicate progress")

	while process.poll() is None:
		buf = process.stdout.read(128)
		if len(buf) == -1:
			break
		file.write(buf)
		if print_to_stdout:
			sys.stdout.buffer.write(buf)
		else:
			sys.stdout.write(".")

	exitCode = process.wait()
	file.close()

	if exitCode != 0:
		print('Command \'' + command + '\' failed!')
		print('Expected error code 0, got ' + str(exitCode))
		sys.exit(1)


def copyALlInDir(src, dest):
	for root, dirs, files in os.walk(src, topdown=False):
		for name in files:
			destFile = os.path.join(os.path.join(dest, root[len(src):]), name)
			print('loop file ' + root + ' ' + name + ' cp to ' + destFile)
			mkpath(os.path.abspath(os.path.join(destFile, '..')))
			copy_file(os.path.join(root, name), destFile)


CI = False

if len(sys.argv) != 3:
	print("Command line arguments either incorrect or not specifyed. Reverting to defaults")
	osName = platform.system().lower()
	if osName == "windows":
		compiler = "msvc"
	elif osName == "linux":
		compiler = "gcc"
	elif osName == "darwin":
		osName = "macosx"
		compiler = "clang"
	else:
		osName = "unknown"

else:
	print("Using command line arguments!")
	osName = sys.argv[1]
	compiler = sys.argv[2]
	if "-travis" in osName:
		osName = osName[:-len("-travis")]
		CI = True
		print("Detected CI enviorment")

print('')
print('osName ' + osName)
print('compiler ' + compiler)
print('')


premakeCommand = ''
if osName == 'linux':
	premakeCommand += 'premake5 '

elif osName == 'windows':
	premakeCommand += 'call vendor\\premake\\bin\\premake5.exe '

elif osName == 'macosx':
	print('osx is unsupported for now!')
	sys.exit(1)

else:
	print('Unknown OS! ' + osName)
	sys.exit(1)

premakeCommand += '--ci '

if compiler == 'msvc':
	if CI:
		premakeCommand += '--os=windows --compiler=msc vs2017'
	else:
		premakeCommand += '--os=windows --compiler=msc vs2019'

elif compiler == 'gcc':
	premakeCommand += '--os=' + osName + ' --compiler=gcc gmake2'

elif compiler == 'clang':
	premakeCommand += '--os=' + osName + ' --compiler=gcc gmake2'

elif compiler == 'emcc':
	premakeCommand += '--os=emscripten --scripts=Hazel/vendor/premake/scripts gmake2'

else:
	print('Unknown compiler! ' + compiler)
	sys.exit(1)

print('running premake: \"' + premakeCommand + '\"')
run(premakeCommand)

#Project files have been generated compile CPP

if osName == 'windows':
	command = 'MSBuild.exe /m /p:Configuration=release NodeCppBench.sln'
else:
	command = 'make -j2 config=release'

print('running: ' + command)	
print('compiling...')

if osName == 'windows':
	s = ';'
else:
	s = ':'

env = os.environ.copy()
origionalPath = env["PATH"]
env["PATH"] = ''


if osName == 'windows':
	if CI:
		env["PATH"] += "c:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\MSBuild\\15.0\\Bin" + s
	else:
		env["PATH"] += "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\MSBuild\\Current\\Bin" + s

env["PATH"] += origionalPath

env.pop("CC", None)
env.pop("CXX", None)
env.pop("AR", None)

#Compile

#TIME SWITCH
reRun = True

if reRun:
	run(command, env)

if osName == 'windows':
	s = '\\'
else:
	s = '/'

command = "bin" + s + "Release-" + osName + "-x86_64" + s + "Test" + s + "Test"

command += " -r xml"


if reRun:
	run_save_out(command, "out/CppBench.xml")

#Parse Cpp Output

import xml.etree.ElementTree as ET
root = ET.parse("out/CppBench.xml").getroot()

data = {}

for group in root.findall("Group"):
	for case in group.findall("TestCase"):
		name = case.attrib.get('name')
		results = case.find("BenchmarkResults")
		meanTag = results.find('mean')
		mean = int(meanTag.attrib.get('value'))
		data[name] = mean



if reRun:
	run_save_out("node node/Main.js", "out/NodeBench.txt")

file = open("out/NodeBench.txt", "r")
line = file.readline()
while line:
	parts = line.split("=")
	name = parts[0]
	mean = float(parts[1])
	if len(parts) != 2:
		print("Node prints invalid line: " + lines + " expected \"X=Y\"")
		sys.exit(1)

	values = name.split(" | ")
	if len(values) == 3:
		data[name] = mean
	elif len(values) == 2:
		benchName = values[0]
		configuration = values[1]
		data[benchName + " | Node | " + configuration] = mean
	line = file.readline()

file.close()

graphs = {}

print("parsing data...")
for key, value in data.items():
	parts = key.split(" | ")
	if len(parts) != 3:
		print("Test name \"" + key + "\" does not have 2 parts")
		sys.exit(1)

	graphName = parts[0]
	strategy = parts[1]
	operation = parts[2]

	if not graphName in graphs:
		graphs[graphName] = {}

	if not strategy in graphs[graphName]:
		graphs[graphName][strategy] = {}

	if not operation in graphs[graphName][strategy]:
		graphs[graphName][strategy][operation] = {}

	graphs[graphName][strategy][operation]["mean"] = value

origionalGraphs = copy.deepcopy(graphs)

operationAverages = {}
print("calculating averages...")

for graphName in list(graphs.keys()):
	for stratName in list(graphs[graphName].keys()):
		for operationName in list(graphs[graphName][stratName].keys()):
			if not graphName in operationAverages:
				operationAverages[graphName] = {}

			if not operationName in operationAverages[graphName]:
				operationAverages[graphName][operationName] = {}
				operationAverages[graphName][operationName]["total"] = 0
				operationAverages[graphName][operationName]["count"] = 0

			operationAverages[graphName][operationName]["total"] += graphs[graphName][stratName][operationName]["mean"]
			operationAverages[graphName][operationName]["count"] += 1

lastCount = -1
for graphName in graphs.keys():
	for stratName in graphs[graphName].keys():
		for operationName in graphs[graphName][stratName].keys():
			count = operationAverages[graphName][operationName]["count"]
			if lastCount != -1 and lastCount != count:
				print("Graph " + graphName + " operation " + operationName + " has " + count + " entries, expected " + lastCount)
				sys.exit(1)

for graphName in operationAverages.keys():
	for operationName in operationAverages[graphName].keys():
		operationAverages[graphName][operationName]["average"] = operationAverages[graphName][operationName]["total"] / operationAverages[graphName][operationName]["count"]

print("resolving conflicts...")
#Makes sure all values for a particular graph are close enough to each other and splits up graphs if not
def resolveConflicts(graphsToFix):

	for graphName in list(graphs.keys()):
		minValue = -1
		if not graphName in graphsToFix:
			continue

		for stratName in list(graphs[graphName].keys()):
			for operationName in list(graphs[graphName][stratName].keys()):
				if minValue == -1 or operationAverages[graphName][operationName]["average"] < minValue:
					minValue = operationAverages[graphName][operationName]["average"]

		#Keep all values on a graph within a certain range
		maxAllowed = minValue * 10
		if graphName[-1:] == ']' and '[' in graphName:
			currentChar = graphName[-2:-1]
			graphNamePart = graphName[:-3]
			nextGraphName = graphNamePart + "[" + chr(ord(currentChar) + 1) + "]"
		else:
			newGraphName = graphName + " [A]"
			nextGraphName = graphName + " [B]"
			graphs[newGraphName] = graphs[graphName]
			graphs.pop(graphName)

			operationAverages[newGraphName] = operationAverages[graphName]
			operationAverages.pop(graphName)

			graphName = newGraphName

		toFix = set()
		for stratName in list(graphs[graphName].keys()):
			for operationName in list(graphs[graphName][stratName].keys()):
				if operationAverages[graphName][operationName]["average"] >= maxAllowed:
					if not nextGraphName in graphs:
						graphs[nextGraphName] = {}

					if not nextGraphName in operationAverages:
						operationAverages[nextGraphName] = {}

					if not stratName in graphs[nextGraphName]:
						graphs[nextGraphName][stratName] = {}

					if not operationName in operationAverages[nextGraphName]:
						operationAverages[nextGraphName][operationName] = {}

					operationAverages[nextGraphName][operationName] = operationAverages[graphName][operationName]

					if not operationName in graphs[nextGraphName][stratName]:
						graphs[nextGraphName][stratName][operationName] = {}
					graphs[nextGraphName][stratName][operationName]["mean"] = graphs[graphName][stratName][operationName]["mean"]

					graphs[graphName][stratName].pop(operationName)
					if (len(graphs[graphName][stratName]) == 0):
						graphs[graphName].pop(stratName)
					if (len(graphs[graphName]) == 0):
						graphs.pop(graphName)

					toFix.add(nextGraphName)

		if len(toFix) > 0:
			resolveConflicts(toFix)

resolveConflicts(graphs.keys())

import plotly.graph_objects as go

print("Adding origional graphs")
for graphName in origionalGraphs.keys():
	if not graphName in graphs.keys():
		graphs[graphName] = origionalGraphs[graphName]

print("plotting data...")

for graphName, strategies in graphs.items():
	plotBars = []
	print("\tinit plot " + graphName)

	for stratName, operations in strategies.items():
		xAxis = []
		times = []
		for operationName, values in operations.items():
			xAxis.append(operationName)
			times.append(values["mean"] / 1000000.0)

		plotBars.append(go.Bar(name=stratName, x=xAxis, y=times))

	fig = go.Figure(data=plotBars)
	# Change the bar mode
	fig.update_layout(
		barmode='group',
		title=graphName + " Performance Test",
		xaxis_title="Configurations",
		yaxis_title="Time (Milliseconds)"
	)

	fileName = "out/" + graphName + ".png"
	print("\tsaving " + fileName + "...")
	fig.write_image(fileName)


