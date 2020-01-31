import sys
import os
import platform
import subprocess
import shutil
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
run(command, env)

if osName == 'windows':
	s = '\\'
else:
	s = '/'

command = "bin" + s + "Release-" + osName + "-x86_64" + s + "Test" + s + "Test"

command += " -r xml"

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
		data[benchName + " | node | " + configuration] = mean
	line = file.readline()

file.close()

graphs = {}

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


import plotly.graph_objects as go



for graphName, strategies in graphs.items():
	print("graph: " + graphName)
	plotBars = []
	lastXAxis = []
	for stratName, operations in strategies.items():
		print("stratName: " + stratName)
		xAxis = []
		times = []
		for operationName, values in operations.items():
			print("operationName: " + operationName)
			xAxis.append(operationName)
			times.append(values["mean"] / 1000000.0)

		if set(xAxis) != set(lastXAxis) and len(lastXAxis) > 0:
			print("X axies dont match. Expected " + str(lastXAxis) + " but got " + str(xAxis))
			sys.exit(1)
		lastXAxis = xAxis
		print(str(times))

		plotBars.append(go.Bar(name=stratName, x=xAxis, y=times))

	#print("\txaxis: " + xAxis)
	fig = go.Figure(data=plotBars)
	# Change the bar mode
	fig.update_layout(
		yaxis_type="log",
		barmode='group',
		title=graphName + " Performance Test",
    	xaxis_title="Configurations",
    	yaxis_title="Time (Milliseconds)"
    )
	fig.write_image("out/" + graphName + ".png")


